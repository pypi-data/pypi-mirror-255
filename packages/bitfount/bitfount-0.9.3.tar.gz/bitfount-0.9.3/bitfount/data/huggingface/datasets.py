"""Hugging Face Datasets."""

from typing import Any, Iterator, Mapping, Optional, Sequence, Tuple, Union, cast

import numpy as np
import pandas as pd
import torch

from bitfount.data.datasets import (
    _BaseBitfountDataset,
    _BitfountDataset,
    _FileSystemBitfountDataset,
    _FileSystemIterableBitfountDataset,
    _IterableBitfountDataset,
)
from bitfount.data.datasources.base_source import (
    FileSystemIterableSource,
    IterableSource,
)
from bitfount.data.types import (
    _DataEntryAllowingText,
    _HFSegmentation_ImageTextEntry,
    _ImagesData,
    _TabularData,
    _TextData,
)


class _BaseHuggingFaceDataset(_BaseBitfountDataset):
    """Hugging Face Dataset."""

    def __init__(
        self, labels2id: Optional[Mapping[str, int]] = None, **kwargs: Any
    ) -> None:
        self.labels2id = labels2id
        super().__init__(**kwargs)

    def _set_text_values(self, data: pd.DataFrame) -> None:
        """Sets `self.text`."""
        self.text = data.loc[
            :, self.selected_cols_semantic_types.get("text", [])
        ].values.tolist()

    def __len__(self) -> int:
        """Returns the length of the dataset."""
        data = self.get_dataset_split(
            split=self.data_split, data_splitter=self.data_splitter
        )
        self._reformat_data(data)
        return len(self.x_var[0])

    def _reformat_data(self, data: pd.DataFrame) -> None:
        """Reformats the data to be compatible with the Dataset class."""
        self.data = data.reset_index(drop=True)
        if self.labels2id is not None:
            # Encode categorical labels to integers in the data
            self.data = self.data.replace(self.labels2id)
        X, Y = self._get_xy(self.data)
        if self.image_columns:
            self._set_image_values(X)
        self._set_tabular_values(X)
        self._set_text_values(X)
        # Package tabular, image and text columns together under the x_var attribute
        self.x_var = (self.tabular, self.image, self.text)
        self._set_target_values(Y)

    def __getitem__(
        self, idx: Union[int, Sequence[int], torch.Tensor]
    ) -> _DataEntryAllowingText:
        if torch.is_tensor(idx):
            idx = cast(torch.Tensor, idx)
            list_idx: list = idx.tolist()
            return self._getitem(list_idx)
        else:
            idx = cast(Union[int, Sequence[int]], idx)
            return self._getitem(idx)

    def _getitem(self, idx: Union[int, Sequence[int]]) -> _DataEntryAllowingText:
        """Returns the item referenced by index `idx` in the data."""
        image: _ImagesData
        tab: _TabularData
        text: _TextData

        target: Union[np.ndarray, Tuple[np.ndarray, ...]]
        if len(self.y_var) == 0:
            # Set the target, if the dataset has no supervision,
            # choose set the default value to be 0.
            target = np.array(0)
        elif (
            "image" in self.selected_cols_semantic_types
            and self.target in self.selected_cols_semantic_types["image"]
        ):
            # Check if the target is an image and load it.
            target = self._load_images(idx, what_to_load="target")
        else:
            target = self.y_var[idx]
        # If the Dataset contains both tabular and image data
        if self.image.size and self.tabular.size:
            tab = self.tabular[idx]
            image = self._load_images(idx)
            return (tab, image), target

        # If the Dataset contains only tabular data
        elif self.tabular.size:
            tab = self.tabular[idx]
            return tab, target

        # If the Dataset contains image and text data
        # Used for Hugging Face image segmentation algorithm
        elif self.image.size and np.array(self.text).size:
            image = self._load_images(idx)
            text = self.text[idx]
            return cast(_HFSegmentation_ImageTextEntry, (image, text, target))
        # If the Dataset contains only image data
        elif self.image.size:
            image = self._load_images(idx)
            return image, target
        else:
            # All cases remaining cases require text data only need the text (for now)
            text = self.text[idx]
            return text, target


class _HuggingFaceDataset(_BaseHuggingFaceDataset, _BitfountDataset):
    """Hugging Face Dataset."""

    datasource: IterableSource
    pass


class _IterableHuggingFaceDataset(_IterableBitfountDataset, _BaseHuggingFaceDataset):
    """Iterable HuggingFace Dataset.

    The main difference between this and other datasets
    is that it does not require a schema and does not
    include the support columns.
    """

    datasource: IterableSource

    def __iter__(self) -> Iterator[_DataEntryAllowingText]:
        """Iterates over the dataset."""
        for data_partition in self.yield_dataset_split(
            split=self.data_split, data_splitter=self.data_splitter
        ):
            self._reformat_data(data_partition)
            for idx in range(len(self.data)):
                yield self._getitem(idx)


class _FileSystemHuggingFaceDataset(_FileSystemBitfountDataset, _HuggingFaceDataset):
    """File System HuggingFace Dataset."""

    datasource: FileSystemIterableSource

    pass


class _FileIterableHuggingFaceDataset(
    _FileSystemIterableBitfountDataset, _IterableHuggingFaceDataset
):
    """File Iterable HuggingFace Dataset."""

    datasource: FileSystemIterableSource

    pass
