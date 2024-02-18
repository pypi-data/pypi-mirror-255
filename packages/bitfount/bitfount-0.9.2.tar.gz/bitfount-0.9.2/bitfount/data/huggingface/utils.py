"""Utility functions for HuggingFace data."""
from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Mapping, Optional, Tuple, Union, cast

from bitfount.data.huggingface.datafactory import _BaseHuggingFaceDataFactory
from bitfount.data.huggingface.datasets import (
    _HuggingFaceDataset,
    _IterableHuggingFaceDataset,
)
from bitfount.federated.algorithms.hugging_face_algorithms.utils import (
    parse_batch_transforms,
)
from bitfount.transformations.batch_operations import BatchTimeOperation

if TYPE_CHECKING:
    from bitfount.data.datasources.base_source import BaseSource
    from bitfount.data.datasplitters import DataSplit
    from bitfount.data.types import _SemanticTypeValue
    from bitfount.types import _JSONDict


def get_data_factory_dataset(
    datasource: BaseSource,
    data_split: DataSplit,
    selected_cols: List[str],
    selected_cols_semantic_types: Mapping[_SemanticTypeValue, List[str]],
    batch_transforms: Optional[List[Dict[str, _JSONDict]]],
    labels2id: Optional[Dict[str, int]] = None,
    target: Optional[Union[str, List[str]]] = None,
) -> Tuple[
    _BaseHuggingFaceDataFactory, Union[_IterableHuggingFaceDataset, _HuggingFaceDataset]
]:
    """Get the HuggingFace data factory and dataset for the given datasource."""
    data_factory = _BaseHuggingFaceDataFactory()
    dataset = data_factory.create_dataset(
        datasource=datasource,
        data_splitter=datasource.data_splitter,
        data_split=data_split,
        selected_cols=selected_cols,
        selected_cols_semantic_types=selected_cols_semantic_types,
        batch_transforms=cast(
            Optional[List[BatchTimeOperation]], parse_batch_transforms(batch_transforms)
        ),
        labels2id=labels2id,
        target=target,
    )
    return data_factory, dataset
