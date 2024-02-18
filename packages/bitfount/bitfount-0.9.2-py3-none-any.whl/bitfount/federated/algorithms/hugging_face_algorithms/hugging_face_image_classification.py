"""Hugging Face Image Classification Algorithm."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, Mapping, Optional

from marshmallow import fields
import pandas as pd
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification, set_seed

from bitfount.data.huggingface.utils import get_data_factory_dataset
from bitfount.data.types import DataSplit, _SemanticTypeValue
from bitfount.federated.algorithms.base import (
    BaseAlgorithmFactory,
    BaseModellerAlgorithm,
    BaseWorkerAlgorithm,
)
from bitfount.federated.logging import _get_federated_logger
from bitfount.utils import DEFAULT_SEED, delegates

if TYPE_CHECKING:
    from bitfount.data.datasources.base_source import BaseSource
    from bitfount.federated.privacy.differential import DPPodConfig
    from bitfount.types import T_FIELDS_DICT

logger = _get_federated_logger(__name__)


class _ModellerSide(BaseModellerAlgorithm):
    """Modeller side of the HuggingFaceImageClassificationInference algorithm."""

    def initialise(self, task_id: Optional[str] = None, **kwargs: Any) -> None:
        """Nothing to initialise here."""
        pass

    def run(self, results: Mapping[str, Any], log: bool = False) -> Dict[str, Any]:
        """Simply returns results and optionally logs them."""
        if log:
            for pod_name, response in results.items():
                for _, response_ in enumerate(response):
                    logger.info(f"{pod_name}: {response_['image_classification']}")

        return dict(results)


class _WorkerSide(BaseWorkerAlgorithm):
    """Worker side of the HuggingFaceImageClassificationInference algorithm."""

    def __init__(
        self,
        model_id: str,
        image_column_name: str,
        apply_softmax_to_predictions: bool = True,
        batch_size: int = 1,
        seed: int = DEFAULT_SEED,
        top_k: int = 5,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.model_id = model_id
        self.batch_size = batch_size
        self.top_k = top_k
        self.seed = seed
        self.image_column_name = image_column_name
        self.image_col_with_semantic_type: Mapping[_SemanticTypeValue, List[str]] = {
            "image": [self.image_column_name]
        }
        self.apply_softmax_to_predictions = apply_softmax_to_predictions

    def initialise(
        self,
        datasource: BaseSource,
        pod_dp: Optional[DPPodConfig] = None,
        pod_identifier: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialises the model and tokenizer."""
        # TODO: [BIT-3097] Resolve initialise without DP
        if pod_dp:
            logger.warning("The use of DP is not supported, ignoring set `pod_dp`.")
        self.initialise_data(datasource=datasource)
        data_factory, dataset = get_data_factory_dataset(
            datasource=datasource,
            data_split=DataSplit.TEST,
            selected_cols=[self.image_column_name],
            selected_cols_semantic_types=self.image_col_with_semantic_type,
            batch_transforms=[],
        )
        self.test_dataloader = data_factory.create_dataloader(
            dataset, batch_size=self.batch_size, **kwargs
        )
        set_seed(self.seed)
        self.image_processor = AutoImageProcessor.from_pretrained(self.model_id)
        self.model = AutoModelForImageClassification.from_pretrained(self.model_id)
        # Update top_k if it is higher than the number of labels defined by the model
        if self.top_k > self.model.config.num_labels:
            logger.warning(
                f"The provided `top_k` ({self.top_k}) is higher than the number of "
                f"labels defined by the model ({self.model.config.num_labels}). "
                f"Setting `top_k` to {self.model.config.num_labels}."
            )
            self.top_k = self.model.config.num_labels

    def run(
        self,
    ) -> pd.DataFrame:
        """Runs inference on the given image classification HuggingFace model."""
        dataframe_records = []

        for _batch_idx, (input_, _) in enumerate(self.test_dataloader):
            input_ = self.image_processor(images=input_, return_tensors="pt")
            with torch.no_grad():
                outputs = self.model(**input_)
            if self.apply_softmax_to_predictions:
                # Apply the same softmax as it is in the HF ImageClassificationPipeline
                probabilities = outputs.logits.softmax(-1)[0]
            else:
                probabilities = outputs.logits
            values, indices = probabilities.topk(self.top_k)
            if indices.dim() >= 2:
                for idx, val in zip(indices, values):
                    labels = {
                        self.model.config.id2label[i.item()]: v.item()
                        for i, v in zip(idx, val)
                    }
                    dataframe_records.append(labels)
            else:
                labels = {
                    self.model.config.id2label[i.item()]: v.item()
                    for i, v in zip(indices, values)
                }
                dataframe_records.append(labels)
        df = pd.DataFrame.from_records(dataframe_records)
        df = df.reindex(sorted(df.columns), axis=1)
        return df


@delegates()
class HuggingFaceImageClassificationInference(BaseAlgorithmFactory):
    """Inference for pre-trained Hugging Face image classification models.

    Args:
        model_id: The model id to use for image classification inference.
            The model id is of a pretrained model hosted inside a model
            repo on huggingface.co. Accepts resnet models.
        image_column_name: The image column on which the inference should be done.
        batch_size: The batch size for inference. Defaults to 1.
        top_k: The number of top labels that will be returned by the pipeline.
            If the provided number is higher than the number of labels available
            in the model configuration, it will default to the number of labels.
            Defaults to 5.
        seed: Sets the seed of the algorithm. For reproducible behavior
            it defaults to 42.

    Attributes:
        model_id: The model id to use for image classification inference.
            The model id is of a pretrained model hosted inside a model
            repo on huggingface.co. Accepts resnet models.
        image_column_name: The image column on which the inference should be done.
        batch_size: The batch size for inference. Defaults to 1.
        top_k: The number of top labels that will be returned by the pipeline.
            If the provided number is higher than the number of labels available
            in the model configuration, it will default to the number of labels.
            Defaults to 5.
        seed: Sets the seed of the algorithm. For reproducible behavior
            it defaults to 42.
    """

    def __init__(
        self,
        model_id: str,
        image_column_name: str,
        seed: int = DEFAULT_SEED,
        apply_softmax_to_predictions: bool = True,
        batch_size: int = 1,
        top_k: int = 5,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.model_id = model_id
        self.image_column_name = image_column_name
        self.batch_size = batch_size
        self.top_k = top_k
        self.seed = seed
        self.apply_softmax_to_predictions = apply_softmax_to_predictions

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "model_id": fields.Str(required=True),
        "image_column_name": fields.Str(required=True),
        "batch_size": fields.Int(required=False),
        "top_k": fields.Int(required=False),
        "seed": fields.Int(required=False, missing=DEFAULT_SEED),
        "apply_softmax_to_predictions": fields.Bool(required=False),
    }

    def modeller(self, **kwargs: Any) -> _ModellerSide:
        """Returns the modeller side of the HuggingFaceImageClassificationInference algorithm."""  # noqa: B950
        return _ModellerSide(**kwargs)

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Returns the worker side of the HuggingFaceImageClassification algorithm."""
        return _WorkerSide(
            model_id=self.model_id,
            image_column_name=self.image_column_name,
            top_k=self.top_k,
            apply_softmax_to_predictions=self.apply_softmax_to_predictions,
            batch_size=self.batch_size,
            seed=self.seed,
            **kwargs,
        )
