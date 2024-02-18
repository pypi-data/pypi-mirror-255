"""Hugging Face TIMM inference Algorithm.

Adapted from: https://github.com/huggingface/api-inference-community/
"""
import os
from typing import Any, ClassVar, Dict, List, Mapping, Optional, Union

from marshmallow import fields
import pandas as pd
import timm
from timm.data import (
    CustomDatasetInfo,
    ImageNetInfo,
    create_transform,
    infer_imagenet_subset,
    resolve_model_data_config,
)
import torch

from bitfount.data.datasources.base_source import BaseSource
from bitfount.data.datastructure import DEFAULT_IMAGE_TRANSFORMATIONS
from bitfount.data.huggingface.utils import get_data_factory_dataset
from bitfount.data.types import DataSplit, _SemanticTypeValue
from bitfount.federated.algorithms.base import (
    BaseAlgorithmFactory,
    BaseModellerAlgorithm,
    BaseWorkerAlgorithm,
)
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.privacy.differential import DPPodConfig
from bitfount.types import T_FIELDS_DICT, _JSONDict
from bitfount.utils import delegates

logger = _get_federated_logger(__name__)


class _ModellerSide(BaseModellerAlgorithm):
    """Modeller side of the TIMMInference algorithm."""

    def initialise(
        self,
        task_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Nothing to initialise here."""
        pass

    def run(self, results: Mapping[str, Any]) -> Dict[str, Any]:
        """Simply returns results."""
        return dict(results)


class _WorkerSide(BaseWorkerAlgorithm):
    """Worker side of the TIMMInference algorithm."""

    def __init__(
        self,
        model_id: str,
        image_column_name: str,
        checkpoint_path: Optional[Union[os.PathLike, str]],
        batch_size: int = 1,
        batch_transformations: Optional[List[Dict[str, _JSONDict]]] = None,
        num_classes: Optional[int] = None,
        class_outputs: Optional[List[str]] = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.model_id = f"hf_hub:{model_id}"
        self.image_column_name = image_column_name
        self.checkpoint_path = checkpoint_path
        self.num_classes = num_classes
        self.class_outputs = class_outputs
        self.image_col_with_semantic_type: Mapping[_SemanticTypeValue, List[str]] = {
            "image": [self.image_column_name]
        }
        default_transformations = [
            {
                "albumentations": {
                    "arg": self.image_column_name,
                    "output": True,
                    "transformations": DEFAULT_IMAGE_TRANSFORMATIONS,
                    "step": "test",
                }
            }
        ]
        self.batch_transformations = (
            batch_transformations
            if batch_transformations is not None
            else default_transformations
        )
        self.batch_size = batch_size

        # Prepopulate num_classes when not provided to match the class_outputs.
        if self.class_outputs is not None and self.num_classes is None:
            self.num_classes = len(self.class_outputs)

    def initialise(
        self,
        datasource: BaseSource,
        pod_dp: Optional[DPPodConfig] = None,
        pod_identifier: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Primarily initialises the model with the checkpoint file.

        Also initialises the transformations.
        """
        # TODO: [BIT-3097] Resolve initialise without DP
        if pod_dp:
            logger.warning("The use of DP is not supported, ignoring set `pod_dp`.")

        self.initialise_data(datasource=datasource)
        # If checkpoint and model don't have matching num_classes
        # the below will fail with a RuntimeError.
        self.model = timm.create_model(
            self.model_id,
            num_classes=self.num_classes,
            checkpoint_path=self.checkpoint_path or "",
        )
        data_factory, dataset = get_data_factory_dataset(
            datasource=datasource,
            data_split=DataSplit.TEST,
            selected_cols=[self.image_column_name],
            selected_cols_semantic_types=self.image_col_with_semantic_type,
            batch_transforms=self.batch_transformations,
        )
        self.test_dataloader = data_factory.create_dataloader(
            dataset, batch_size=self.batch_size, **kwargs
        )

        self.transform = create_transform(
            **resolve_model_data_config(self.model, use_test_size=True)
        )
        self.model.eval()

        dataset_info = None
        label_names = self.model.pretrained_cfg.get("label_names", None)
        label_descriptions = self.model.pretrained_cfg.get("label_descriptions", None)

        if label_names is None:
            # If no labels added to config, check if these are provided
            # explicitly as class outputs
            if self.class_outputs is not None:
                label_names = self.class_outputs
            else:
                # If no labels in config/provided explicitly, use imagenet labeller
                imagenet_subset = infer_imagenet_subset(self.model)
                if imagenet_subset:
                    dataset_info = ImageNetInfo(imagenet_subset)
                elif self.model.num_classes is not None:
                    # Otherwise use num_classes as fallback for label names
                    label_names = [f"LABEL_{i}" for i in range(self.model.num_classes)]
                else:
                    # Label fallback failed, raise exception.
                    raise ValueError(
                        "Unable to infer labels for the model. ",
                        "Please ensure that either `class_outputs` or ",
                        "`num_classes` is set.",
                    )

        if dataset_info is None:
            dataset_info = CustomDatasetInfo(
                label_names=label_names,
                label_descriptions=label_descriptions,
            )

        self.dataset_info = dataset_info

    def run(self) -> pd.DataFrame:
        """Runs the inference on the images in the datasource.

        Returns:
            A dataframe with the predictions where each row is an image and each column
            is a class.
        """
        dataframe_records = []

        for _batch_idx, (input_, _) in enumerate(self.test_dataloader):
            with torch.no_grad():
                out = self.model(input_)
            probabilities = out.squeeze(0).softmax(dim=0)
            values, indices = torch.topk(probabilities, self.model.num_classes)
            if indices.dim() >= 2:
                for idx, val in zip(indices, values):
                    labels = {
                        self.dataset_info.index_to_description(
                            i, detailed=True
                        ): v.item()
                        for i, v in zip(idx, val)
                    }
                    dataframe_records.append(labels)
            else:
                labels = {
                    self.dataset_info.index_to_description(i, detailed=True): v.item()
                    for i, v in zip(indices, values)
                }
                dataframe_records.append(labels)
        df = pd.DataFrame.from_records(dataframe_records)
        df = df.reindex(sorted(df.columns), axis=1)
        return df


@delegates()
class TIMMInference(BaseAlgorithmFactory):
    """HuggingFace TIMM Inference Algorithm..

    Args:
        model_id: The model id to use from the Hugging Face Hub.
        image_column_name: The column name of the image paths.
        num_classes: The number of classes in the model.
            Defaults to None.
        checkpoint_path: The path to a checkpoint file local to the Pod.
            Defaults to None.
        class_outputs: A list of explict class outputs to use as labels.
            Defaults to None.

    Attributes:
        model_id: The model id to use from the Hugging Face Hub.
        image_column_name: The column name of the image paths.
        num_classes: The number of classes in the model.
            Defaults to None.
        checkpoint_path: The path to a checkpoint file local to the Pod.
            Defaults to None.
        class_outputs: A list of explict class outputs to use as labels.
            Defaults to None.
    """

    def __init__(
        self,
        model_id: str,
        image_column_name: str,
        num_classes: Optional[int] = None,
        batch_transformations: Optional[List[Dict[str, _JSONDict]]] = None,
        batch_size: int = 1,
        checkpoint_path: Optional[Union[os.PathLike, str]] = None,
        class_outputs: Optional[List[str]] = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.model_id = model_id
        self.image_column_name = image_column_name
        self.num_classes = num_classes
        self.checkpoint_path = checkpoint_path
        self.class_outputs = class_outputs
        self.batch_transformations = batch_transformations
        self.batch_size = batch_size

        if self.num_classes is None and self.class_outputs is None:
            raise ValueError(
                "Either `num_classes` or `class_outputs` must be provided "
                "for `TIMMInference` initialisation. Currently, both are missing."
            )
        elif self.num_classes is not None and self.class_outputs is not None:
            # Ensure both represent the same number of classes.
            if self.num_classes != len(self.class_outputs):
                raise ValueError(
                    "The `num_classes` and the length of `class_outputs` ",
                    "must be the same. ",
                    f"Currently, `num_classes` is {self.num_classes} and ",
                    f"`class_outputs` has {len(self.class_outputs)} elements.",
                )

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "model_id": fields.String(required=True),
        "image_column_name": fields.String(required=True),
        "num_classes": fields.Integer(required=False, allow_none=True),
        "batch_transformations": fields.List(
            fields.Dict(
                keys=fields.Str(),
                values=fields.Dict(keys=fields.Str()),
            ),
            allow_none=True,
        ),
        "batch_size": fields.Integer(required=False, allow_none=True),
        "checkpoint_path": fields.String(required=False, allow_none=True),
        "class_outputs": fields.List(fields.String(), allow_none=True),
    }

    def modeller(self, **kwargs: Any) -> _ModellerSide:
        """Returns the modeller side of the TIMMInference algorithm."""
        return _ModellerSide(**kwargs)

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Returns the worker side of the TIMMInference algorithm."""
        return _WorkerSide(
            model_id=self.model_id,
            image_column_name=self.image_column_name,
            num_classes=self.num_classes,
            batch_transformations=self.batch_transformations,
            batch_size=self.batch_size,
            checkpoint_path=self.checkpoint_path,
            class_outputs=self.class_outputs,
            **kwargs,
        )
