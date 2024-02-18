"""HuggingFace-specific implementation of the DataFactory provider."""
from typing import Any, List, Mapping, Optional, Union

from bitfount.data.datafactory import _DataFactory
from bitfount.data.dataloaders import BitfountDataLoader
from bitfount.data.datasets import _BaseBitfountDataset
from bitfount.data.datasources.base_source import BaseSource, FileSystemIterableSource
from bitfount.data.datasources.views import _DataViewFromFileIterableSource
from bitfount.data.datasplitters import DatasetSplitter
from bitfount.data.huggingface.dataloaders import (
    HuggingFaceBitfountDataLoader,
    HuggingFaceIterableBitfountDataLoader,
)
from bitfount.data.huggingface.datasets import (
    _FileIterableHuggingFaceDataset,
    _FileSystemHuggingFaceDataset,
    _HuggingFaceDataset,
    _IterableHuggingFaceDataset,
)
from bitfount.data.schema import TableSchema
from bitfount.data.types import DataSplit, _SemanticTypeValue
from bitfount.transformations.batch_operations import BatchTimeOperation


class _BaseHuggingFaceDataFactory(_DataFactory):
    """A HuggingFace-specific implementation of the DataFactory provider."""

    def create_dataloader(
        self,
        dataset: _BaseBitfountDataset,
        batch_size: Optional[int] = None,
        **kwargs: Any,
    ) -> BitfountDataLoader:
        """See base class."""
        kwargs["batch_size"] = batch_size

        # torch is part of our main requirements, and if using
        # a torch model for any of the hugging face tasks, will need to be installed.
        if isinstance(dataset, _IterableHuggingFaceDataset):
            return HuggingFaceIterableBitfountDataLoader(dataset, **kwargs)
        elif isinstance(dataset, _HuggingFaceDataset):
            return HuggingFaceBitfountDataLoader(dataset, **kwargs)
        raise TypeError(
            "The _HuggingFaceDataFactory class only supports "
            "subclasses of HuggingFace Dataset for creating a DataLoader."
        )

    def create_dataset(
        self,
        datasource: BaseSource,
        data_splitter: Optional[DatasetSplitter],
        data_split: DataSplit,
        selected_cols: List[str],
        selected_cols_semantic_types: Mapping[_SemanticTypeValue, List[str]],
        schema: Optional[TableSchema] = None,
        target: Optional[Union[str, List[str]]] = None,
        batch_transforms: Optional[List[BatchTimeOperation]] = None,
        auto_convert_grayscale_images: bool = True,
        **kwargs: Any,
    ) -> Union[_IterableHuggingFaceDataset, _HuggingFaceDataset]:
        """See base class."""
        if (
            isinstance(
                datasource, (FileSystemIterableSource, _DataViewFromFileIterableSource)
            )
            and datasource.cache_images is False
            and datasource.iterable
        ):
            return _FileIterableHuggingFaceDataset(
                datasource=datasource,
                data_splitter=data_splitter,
                data_split=data_split,
                target=target,
                selected_cols=selected_cols,
                selected_cols_semantic_types=selected_cols_semantic_types,
                batch_transforms=batch_transforms,
                auto_convert_grayscale_images=auto_convert_grayscale_images,
                **kwargs,
            )
        elif (
            isinstance(
                datasource, (FileSystemIterableSource, _DataViewFromFileIterableSource)
            )
            and datasource.cache_images is False
            and not datasource.iterable
        ):
            return _FileSystemHuggingFaceDataset(
                datasource=datasource,
                data_splitter=data_splitter,
                data_split=data_split,
                target=target,
                selected_cols=selected_cols,
                selected_cols_semantic_types=selected_cols_semantic_types,
                batch_transforms=batch_transforms,
                auto_convert_grayscale_images=auto_convert_grayscale_images,
                **kwargs,
            )
        elif datasource.iterable:
            return _IterableHuggingFaceDataset(
                datasource=datasource,
                data_splitter=data_splitter,
                data_split=data_split,
                target=target,
                selected_cols=selected_cols,
                selected_cols_semantic_types=selected_cols_semantic_types,
                batch_transforms=batch_transforms,
                auto_convert_grayscale_images=auto_convert_grayscale_images,
                **kwargs,
            )

        return _HuggingFaceDataset(
            datasource=datasource,
            data_splitter=data_splitter,
            data_split=data_split,
            target=target,
            selected_cols=selected_cols,
            selected_cols_semantic_types=selected_cols_semantic_types,
            batch_transforms=batch_transforms,
            auto_convert_grayscale_images=auto_convert_grayscale_images,
            **kwargs,
        )
