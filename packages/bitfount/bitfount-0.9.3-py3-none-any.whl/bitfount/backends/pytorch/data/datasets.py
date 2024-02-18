"""PyTorch implementations for Bitfount Dataset classes."""
from typing import Iterator, Sequence, Tuple, Union

import numpy as np
import torch
from torch.utils.data import Dataset as PTDataset, IterableDataset as PTIterableDataset

from bitfount.backends.pytorch.data.utils import _index_tensor_handler
from bitfount.data.datasets import (
    _BaseBitfountDataset,
    _BitfountDataset,
    _FileSystemBitfountDataset,
    _FileSystemIterableBitfountDataset,
    _IterableBitfountDataset,
)
from bitfount.data.types import _DataEntry, _ImagesData, _SupportData, _TabularData


class BasePyTorchDataset(_BaseBitfountDataset):
    """Base class for representing a Pytorch dataset."""

    def _getitem(self, idx: Union[int, Sequence[int]]) -> _DataEntry:
        """Returns the item referenced by index `idx` in the data."""
        image: _ImagesData
        tab: _TabularData
        sup: _SupportData

        target: Union[np.ndarray, Tuple[np.ndarray, ...]]
        if self.schema is not None:
            # Schema is None for HuggingFace datasets which is
            # handled separately, so we can cast.
            if len(self.y_var) == 0:
                # Set the target, if the dataset has no supervision,
                # choose set the default value to be 0.
                target = np.array(0)
            elif (
                "image" in self.schema.features
                and self.target in self.schema.features["image"]
            ):
                # Check if the target is an image and load it.
                target = self._load_images(idx, what_to_load="target")
            else:
                target = self.y_var[idx]

            # If the Dataset contains both tabular and image data
            if self.image.size and self.tabular.size:
                tab = self.tabular[idx]
                sup = self.support_cols[idx]
                image = self._load_images(idx)
                if self.ignore_support_cols:
                    return (tab, image), target
                return (tab, image, sup), target

            # If the Dataset contains only tabular data
            elif self.tabular.size:
                tab = self.tabular[idx]
                sup = self.support_cols[idx]
                if self.ignore_support_cols:
                    return tab, target
                return (tab, sup), target

            # If the Dataset contains only image data
            else:
                sup = self.support_cols[idx]
                image = self._load_images(idx)
                if self.ignore_support_cols:
                    return image, target
                return (image, sup), target
        else:
            raise TypeError(
                "Dataset initialised without a schema. "
                "The only datasets that support this are the Huggingface algorithms, "
                "so make sure to use the correct datafactory for the dataset."
            )


class _PyTorchDataset(_BitfountDataset, PTDataset, BasePyTorchDataset):
    """See base class."""

    def __getitem__(self, idx: Union[int, Sequence[int], torch.Tensor]) -> _DataEntry:
        idx = _index_tensor_handler(idx)
        return self._getitem(idx)

    def __iter__(self) -> Iterator[_DataEntry]:
        """Iterates over the dataset."""
        # This is to make mypy happy in the case
        # where not all images have the same number of frames.
        for idx in range(len(self)):
            yield self[idx]


class _PyTorchIterableDataset(
    _IterableBitfountDataset, PTIterableDataset, BasePyTorchDataset
):
    """See base class."""

    def __iter__(self) -> Iterator[_DataEntry]:
        """Iterates over the dataset."""
        for data_partition in self.yield_dataset_split(
            split=self.data_split, data_splitter=self.data_splitter
        ):
            self._reformat_data(data_partition)

            for idx in range(len(self.data)):
                yield self._getitem(idx)


class _PytorchFileIterableDataset(
    _FileSystemIterableBitfountDataset, _PyTorchIterableDataset, PTIterableDataset
):
    """See base class."""

    pass


class _PytorchFileSystemDataset(_FileSystemBitfountDataset, _PyTorchDataset, PTDataset):
    """See base class."""

    pass
