"""PyTorch implementations of the datafactory module contents."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, List, Mapping, Optional, Union, cast

from bitfount.backends.pytorch.data.dataloaders import (
    PyTorchBitfountDataLoader,
    PyTorchIterableBitfountDataLoader,
    _BasePyTorchBitfountDataLoader,
)
from bitfount.backends.pytorch.data.datasets import (
    _PyTorchDataset,
    _PytorchFileIterableDataset,
    _PytorchFileSystemDataset,
    _PyTorchIterableDataset,
)
from bitfount.data.datafactory import _DataFactory
from bitfount.data.datasources.base_source import (
    BaseSource,
    FileSystemIterableSource,
    IterableSource,
)
from bitfount.data.datasources.views import _DataViewFromFileIterableSource

if TYPE_CHECKING:
    from bitfount.data.datasets import _BaseBitfountDataset
    from bitfount.data.datasplitters import DatasetSplitter
    from bitfount.data.schema import TableSchema
    from bitfount.data.types import DataSplit, _SemanticTypeValue
    from bitfount.transformations.batch_operations import BatchTimeOperation

_logger = logging.getLogger(__name__)


class _PyTorchDataFactory(_DataFactory):
    """A PyTorch-specific implementation of the DataFactory provider."""

    def create_dataloader(
        self,
        dataset: _BaseBitfountDataset,
        batch_size: Optional[int] = None,
        **kwargs: Any,
    ) -> _BasePyTorchBitfountDataLoader:
        """See base class."""
        if isinstance(dataset, (_PyTorchIterableDataset, _PytorchFileIterableDataset)):
            _logger.debug("Creating PyTorchIterableBitfountDataLoader")
            return PyTorchIterableBitfountDataLoader(
                dataset=dataset, batch_size=batch_size, **kwargs
            )
        elif isinstance(dataset, _PyTorchDataset):
            _logger.debug("Creating PyTorchBitfountDataLoader")
            return PyTorchBitfountDataLoader(dataset, batch_size=batch_size, **kwargs)

        raise TypeError(
            "The _PyTorchDataFactory class only supports "
            "subclasses of PyTorch Dataset for creating a DataLoader."
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
    ) -> Union[_PyTorchDataset, _PyTorchIterableDataset, _PytorchFileIterableDataset]:
        """See base class."""
        if schema is None:
            raise ValueError("The schema must be provided to create a PyTorch dataset.")
        if (
            isinstance(
                datasource, (FileSystemIterableSource, _DataViewFromFileIterableSource)
            )
            and datasource.cache_images is False
            and datasource.iterable
        ):
            logging.debug(
                f"Datasource is a {FileSystemIterableSource.__name__},"
                f" creating a {_PytorchFileIterableDataset.__name__} dataset."
            )
            return _PytorchFileIterableDataset(
                schema=schema,
                selected_cols_semantic_types=selected_cols_semantic_types,
                data_splitter=data_splitter,
                datasource=datasource,
                target=target,
                selected_cols=selected_cols,
                batch_transforms=batch_transforms,
                data_split=data_split,
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
            logging.debug(
                f"Datasource is a {FileSystemIterableSource.__name__},"
                f" creating a {_PytorchFileIterableDataset.__name__} dataset."
            )
            return _PytorchFileSystemDataset(
                schema=schema,
                selected_cols_semantic_types=selected_cols_semantic_types,
                data_splitter=data_splitter,
                datasource=datasource,
                target=target,
                selected_cols=selected_cols,
                batch_transforms=batch_transforms,
                data_split=data_split,
                auto_convert_grayscale_images=auto_convert_grayscale_images,
                **kwargs,
            )
        elif datasource.iterable:
            logging.debug(
                f"Datasource is iterable,"
                f" creating a {_PyTorchIterableDataset.__name__} dataset."
            )
            return _PyTorchIterableDataset(
                schema=schema,
                selected_cols_semantic_types=selected_cols_semantic_types,
                data_splitter=data_splitter,
                datasource=cast(IterableSource, datasource),
                target=target,
                selected_cols=selected_cols,
                batch_transforms=batch_transforms,
                data_split=data_split,
                auto_convert_grayscale_images=auto_convert_grayscale_images,
                **kwargs,
            )
        else:
            logging.debug(
                f"Datasource is not iterable,"
                f" creating a {_PyTorchDataset.__name__} dataset."
            )
            return _PyTorchDataset(
                schema=schema,
                selected_cols_semantic_types=selected_cols_semantic_types,
                data_splitter=data_splitter,
                datasource=datasource,
                target=target,
                selected_cols=selected_cols,
                batch_transforms=batch_transforms,
                data_split=data_split,
                auto_convert_grayscale_images=auto_convert_grayscale_images,
                **kwargs,
            )
