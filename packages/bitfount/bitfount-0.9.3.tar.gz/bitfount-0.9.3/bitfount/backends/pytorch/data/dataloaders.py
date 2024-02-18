"""PyTorch-specific DataLoader implementations."""
import math
import random
import secrets
from typing import Any, Dict, Iterator, List, Union, cast

import torch
from torch.utils.data import DataLoader as PyTorchDataLoader

from bitfount.backends.pytorch.data.datasets import (
    _PyTorchDataset,
    _PyTorchIterableDataset,
)
from bitfount.backends.pytorch.data.utils import _convert_batch_to_tensor
from bitfount.data.dataloaders import BitfountDataLoader
from bitfount.data.datasets import _BitfountDataset, _IterableBitfountDataset
from bitfount.data.types import _DataBatch, _DataEntry, _SingleOrMulti
from bitfount.utils import delegates

#: The default buffer size for shuffling Iterable Datasets.
DEFAULT_BUFFER_SIZE: int = 1000


class _BasePyTorchBitfountDataLoader(BitfountDataLoader):
    """Base class for PyTorch-specific Bitfount DataLoaders.

    Args:
       dataset: An pytorch compatible dataset.
       batch_size: The batch size for the dataloader.
           Defaults to 1.
       shuffle: A boolean value indicating whether the values
           in the dataset should be shuffled. Defaults to False.

    Attributes:
       dataset: An pytorch compatible dataset.
       batch_size: The batch size for the dataloader.
           Defaults to 1.
       shuffle: A boolean value indicating whether the values
           in the dataset should be shuffled. Defaults to False.
    """

    def __init__(
        self,
        dataset: Union[_PyTorchDataset, _PyTorchIterableDataset],
        batch_size: int = 1,
        shuffle: bool = False,
    ):
        self.dataset = dataset
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.secure_rng = False  # not used for non-iterable dataloader

    @property
    def buffer_size(self) -> int:
        """Number of elements to buffer.

        The size of the buffer is the greatest of the batch size and default buffer size
        unless the dataset is smaller than the default buffer in which case the dataset
        size is used. PyTorch already ensures that the batch size is not greater than
        the dataset size under the hood.
        """
        # Batch size is optional in the core hierarchy but in pytorch we ensure it is
        # set to 1 if not provided. Re-assuring mypy of this.
        assert self.batch_size is not None  # nosec assert_used
        return max(min(len(self.dataset), DEFAULT_BUFFER_SIZE), self.batch_size)

    def _image_iter(self) -> Iterator[List[_SingleOrMulti[torch.Tensor]]]:
        self.dataset = cast(
            Union[_PyTorchDataset, _PyTorchIterableDataset], self.dataset
        )
        # If there are images, we need to handle missing frames
        if not self.shuffle:
            batch_buffer_: _DataBatch = []
            sample: _DataEntry
            for sample in self.dataset:
                # Get the number of elements for each sample
                num_x_elements_per_sample = len(
                    sample[0]
                )  # Can be either [tabular, images,  supplementary] or
                # [images, supplementary]. Note that all samples in
                # the dataset will have the same number of elements per sample

                # If batch is empty, add the sample to them
                if len(batch_buffer_) == 0:
                    batch_buffer_.append(sample)
                else:
                    # Otherwise get the last sample from the batch_buffer
                    prev_sample = batch_buffer_[-1]
                    if num_x_elements_per_sample == 3:
                        number_of_frames_current_sample = len(sample[0][1])
                        number_of_frames_previous_sample = len(prev_sample[0][1])
                    else:  # if number of elements is 2
                        number_of_frames_current_sample = len(sample[0][0])
                        number_of_frames_previous_sample = len(prev_sample[0][0])
                    # Check if the number of frames is the same for the current
                    # and previous sample, as we need to handle them differently
                    if (
                        number_of_frames_current_sample
                        == number_of_frames_previous_sample
                    ):
                        batch_buffer_.append(sample)
                        if len(batch_buffer_) == self.batch_size:
                            # if the batch is full, yield it and then clear it
                            yield _convert_batch_to_tensor(batch_buffer_)
                            batch_buffer_.clear()
                    else:
                        # otherwise, yield the current batch_buffer and
                        # start a new one with the current sample
                        yield _convert_batch_to_tensor(batch_buffer_)
                        batch_buffer_ = [sample]
            # If there are any elements left in the batch after the
            # last iteration, yield them
            if batch_buffer_:
                yield _convert_batch_to_tensor(batch_buffer_)
        else:
            batch_dict: Dict[int, _DataBatch] = {}
            # If the dataset should be shuffled, we use a reservoir sampling method
            # to sample from a buffer of elements from the dataset. We also have to
            # group samples with the same shapes for images within a same batch.
            buffer_dict: Dict[int, _DataBatch] = {}
            # buffer_size = 0
            for sample in cast(_PyTorchIterableDataset, self.dataset):
                # Get the number of elements for each sample
                num_x_elements_per_sample = len(
                    sample[0]
                )  # Can be either [tabular,images, supplementary]
                # or [images, supplementary]
                if num_x_elements_per_sample == 3:
                    number_of_frames = len(sample[0][1])
                else:  # if number of elements is 2
                    number_of_frames = len(sample[0][0])
                # add keys for the number of frames for both dictionaries if not present
                if number_of_frames not in buffer_dict.keys():
                    buffer_dict[number_of_frames] = []
                if number_of_frames not in batch_dict.keys():
                    batch_dict[number_of_frames] = []

                if len(buffer_dict[number_of_frames]) == self.buffer_size:
                    buffer_ = buffer_dict[number_of_frames]
                    if len(batch_dict[number_of_frames]) == self.batch_size:
                        yield _convert_batch_to_tensor(batch_dict[number_of_frames])
                        batch_dict[number_of_frames] = []

                    if len(buffer_) == self.buffer_size:
                        if self.secure_rng:
                            idx = secrets.randbelow(self.buffer_size)
                        else:
                            # Ignoring security warning here because RNG does not need
                            # to be cryptographically secure if it is turned off by
                            # the user.
                            idx = random.randint(
                                0, self.buffer_size - 1
                            )  # nosec B311 # "random" usage
                        batch_dict[number_of_frames].append(buffer_[idx])
                        buffer_[idx] = sample
                        buffer_dict[number_of_frames] = buffer_
                else:
                    buffer_dict[number_of_frames].append(sample)
            # This is only reached once the dataset iterator has been exhausted. The
            # remainder of the buffer is shuffled and yielded until empty.
            for key in buffer_dict.keys():
                buffer_ = buffer_dict[key]
                random.shuffle(buffer_)
                batch: _DataBatch = batch_dict[key]
                while buffer_:
                    if len(batch) == self.batch_size:
                        yield _convert_batch_to_tensor(batch)
                        batch = []

                    batch.append(buffer_.pop())
                # If there are any elements left in the batch after the
                # dataset/buffer are empty, yield an incomplete batch.
                if len(batch) > 0:
                    yield _convert_batch_to_tensor(batch)


@delegates()
class PyTorchBitfountDataLoader(_BasePyTorchBitfountDataLoader):
    """Wraps a PyTorch DataLoader with bitfount functions.

    Args:
       dataset: An pytorch compatible dataset.
    """

    def __init__(self, dataset: _BitfountDataset, **kwargs: Any):
        dataset = cast(_PyTorchDataset, dataset)
        super().__init__(dataset=dataset, **kwargs)
        self.dataloader = self.get_pytorch_dataloader()

    def get_pytorch_dataloader(self, **kwargs: Any) -> PyTorchDataLoader:
        """Return a PyTorch DataLoader for `self.dataset`.

        Keyword arguments are passed to PyTorch's DataLoader constructor and take
        precedence over the values set in the constructor.
        """
        return PyTorchDataLoader(
            dataset=kwargs.pop("dataset", self.dataset),
            batch_size=kwargs.pop("batch_size", self.batch_size),
            shuffle=kwargs.pop("shuffle", self.shuffle),
            **kwargs,
        )

    def __len__(self) -> int:
        """Number of batches or number of elements if batch size is None."""
        # If there is only one image columns, then we keep everything as before.
        # From the pytorch dataloader, the length of the dataloader will be
        # given by len(dataset) /batch_size, since we might have uneven batches,
        # we could even be in the case where we will have all batch sizes equal to 1,
        # which means we will have to go through the whole dataset.
        # If there are fewer batches, we reach a StopIteration.
        if len(self.dataset.image_columns) > 1:
            return len(self.dataset)
        else:
            return len(self.dataloader)

    def __iter__(self) -> Iterator[List[_SingleOrMulti[torch.Tensor]]]:
        """Wrapper around the default PyTorch DataLoader iterator.

        If there is less than one image selected as part o the dataset or
        batch size is set to, the only difference is that the elements of
        each batch are wrapped in a list. Otherwise, we use the custom
        iterator defined in the parent class for batching based on the
        number of frames.
        """
        # Batch size is optional in the core hierarchy but in pytorch we ensure it is
        # set to 1 if not provided. Re-assuring mypy of this.
        assert self.batch_size is not None  # nosec assert_used
        if len(self.dataset.image_columns) > 1 and self.batch_size > 1:
            yield from self._image_iter()
        else:
            # If there are no images, we handle missing values in the
            # _reformat_data function on the dataset, so we can just
            # go through the batches.
            for batch in self.dataloader:
                yield [x for x in batch]


@delegates()
class PyTorchIterableBitfountDataLoader(_BasePyTorchBitfountDataLoader):
    """Wraps a PyTorch DataLoader with bitfount functions.

    Args:
        dataset: An iterable dataset.
        secure_rng: A boolean value indicating whether to use a secure
            random number generator. Defaults to False.

    Attributes:
         secure_rng: A boolean value indicating whether to use a secure
            random number generator. Defaults to False.
    """

    def __init__(
        self, dataset: _IterableBitfountDataset, secure_rng: bool = False, **kwargs: Any
    ):
        # _PytorchIterableDataset is a wrapper around of
        # _IterableBitfountDataset so this cast is safe.
        dataset = cast(_PyTorchIterableDataset, dataset)
        super().__init__(dataset=dataset, **kwargs)
        self.secure_rng = secure_rng

    def __len__(self) -> int:
        """Number of batches in the dataset."""
        if len(self.dataset.image_columns) > 1:
            return len(self.dataset)
        else:
            assert self.batch_size is not None  # nosec assert_used
            return math.ceil(len(self.dataset) / self.batch_size)

    def __iter__(self) -> Iterator[List[_SingleOrMulti[torch.Tensor]]]:
        """Yields a batch of data when iterated.

        We use a custom iterator with different behaviour depending on whether the
        dataset should be shuffled or not. Each batch is explicitly converted to torch
        tensors prior to yielding as this is not done automatically by pytorch.
        """
        # Batch size is optional in the core hierarchy but in pytorch we ensure it is
        # set to 1 if not provided. Re-assuring mypy of this.
        assert self.batch_size is not None  # nosec assert_used
        if len(self.dataset.image_columns) > 1 and self.batch_size > 1:
            yield from self._image_iter()
        else:
            batch: _DataBatch = []

            if self.shuffle:
                # If the dataset should be shuffled, we use a reservoir sampling method
                # to sample from a buffer of elements from the dataset.
                buffer_: _DataBatch = []
                for sample in cast(_PyTorchIterableDataset, self.dataset):
                    if len(batch) == self.batch_size:
                        yield _convert_batch_to_tensor(batch)
                        batch = []

                    if len(buffer_) == self.buffer_size:
                        if self.secure_rng:
                            idx = secrets.randbelow(self.buffer_size)
                        else:
                            # Ignoring security warning here because RNG does not need
                            # to be cryptographically secure if it is turned off by
                            # the user.
                            idx = random.randint(
                                0, self.buffer_size - 1
                            )  # nosec B311 # "random" usage
                        batch.append(buffer_[idx])
                        buffer_[idx] = sample
                    else:
                        buffer_.append(sample)

                # This is only reached once the dataset iterator has been exhausted. The
                # remainder of the buffer is shuffled and yielded until empty.
                random.shuffle(buffer_)
                while buffer_:
                    if len(batch) == self.batch_size:
                        yield _convert_batch_to_tensor(batch)
                        batch = []

                    batch.append(buffer_.pop())

            else:
                # If the dataset should not be shuffled, we simply
                # iterate over the dataset
                for sample in cast(_PyTorchIterableDataset, self.dataset):
                    if len(batch) == self.batch_size:
                        yield _convert_batch_to_tensor(batch)
                        batch = []

                    batch.append(sample)

            # If there are any elements left in the batch after the dataset/buffer are
            # empty, yield an incomplete batch.
            if batch:
                yield _convert_batch_to_tensor(batch)
