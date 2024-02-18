"""Hugging Face Text Classification Algorithm."""
from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    List,
    Literal,
    Mapping,
    Optional,
    Union,
)

from marshmallow import fields
import numpy as np
import pandas as pd
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, set_seed

from bitfount.data.datasources.base_source import BaseSource
from bitfount.data.huggingface.utils import get_data_factory_dataset
from bitfount.data.types import DataSplit, _SemanticTypeValue
from bitfount.federated.algorithms.base import (
    BaseAlgorithmFactory,
    BaseModellerAlgorithm,
    BaseWorkerAlgorithm,
)
from bitfount.federated.logging import _get_federated_logger
from bitfount.types import T_FIELDS_DICT
from bitfount.utils import DEFAULT_SEED, delegates

if TYPE_CHECKING:
    from bitfount.federated.privacy.differential import DPPodConfig


logger = _get_federated_logger(__name__)
_FunctionToApply = Literal["sigmoid", "softmax", "none"]


def sigmoid(_outputs: np.ndarray) -> torch.Tensor:
    """Sigmoid function for output postprocessing."""
    return torch.from_numpy(1.0 / (1.0 + np.exp(-_outputs)))


def softmax(_outputs: np.ndarray) -> torch.Tensor:
    """Softmax function for output postprocessing."""
    maxes = np.max(_outputs, axis=-1, keepdims=True)
    shifted_exp = np.exp(_outputs - maxes)
    return torch.from_numpy(shifted_exp / shifted_exp.sum(axis=-1, keepdims=True))


class _ModellerSide(BaseModellerAlgorithm):
    """Modeller side of the HuggingFaceTextClassificationInference algorithm."""

    def initialise(self, task_id: Optional[str] = None, **kwargs: Any) -> None:
        """Nothing to initialise here."""
        pass

    def run(self, results: Mapping[str, Any], log: bool = False) -> Dict[str, Any]:
        """Simply returns results and optionally logs them."""
        if log:
            for pod_name, response in results.items():
                for _, response_ in enumerate(response):
                    logger.info(f"{pod_name}: {response_['text_classification']}")

        return dict(results)


class _WorkerSide(BaseWorkerAlgorithm):
    """Worker side of the HuggingFaceTextClassificationInference algorithm."""

    def __init__(
        self,
        model_id: str,
        target_column_name: str,
        batch_size: int = 1,
        function_to_apply: Optional[_FunctionToApply] = None,
        seed: int = DEFAULT_SEED,
        top_k: int = 1,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.model_id = model_id
        self.target_column_name = target_column_name
        self.target_col_with_semantic_type: Mapping[_SemanticTypeValue, List[str]] = {
            "text": [self.target_column_name]
        }
        self.batch_size = batch_size
        self.function_to_apply = function_to_apply
        self.seed = seed
        self.top_k = top_k

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
            selected_cols=[self.target_column_name],
            selected_cols_semantic_types=self.target_col_with_semantic_type,
            batch_transforms=[],
        )
        self.test_dataloader = data_factory.create_dataloader(
            dataset, batch_size=self.batch_size, **kwargs
        )
        set_seed(self.seed)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_id)
        if self.top_k > self.model.config.num_labels:
            logger.warning(
                f"The provided `top_k` ({self.top_k}) is higher than the number of "
                f"labels defined by the model ({self.model.config.num_labels}). "
                f"Setting `top_k` to {self.model.config.num_labels}."
            )
            self.top_k = self.model.config.num_labels

    def run(
        self,
    ) -> Union[pd.DataFrame, List[List[Dict[str, Union[str, float]]]], Dict[str, Any]]:
        """Runs the pipeline to generate text."""
        dataframe_records = []
        for _batch_idx, (input_, _) in enumerate(self.test_dataloader):
            if isinstance(input_[0], tuple):
                input_ = [item[0] for item in input_]
            input_ = self.tokenizer(input_, return_tensors="pt")
            with torch.no_grad():
                model_outputs = self.model(**input_)
            # Get and apply the right post-processing function
            if self.function_to_apply is None:
                if (
                    self.model.config.problem_type == "multi_label_classification"
                    or self.model.config.num_labels == 1
                ):
                    self.function_to_apply = "sigmoid"
                elif (
                    self.model.config.problem_type == "single_label_classification"
                    or self.model.config.num_labels > 1
                ):
                    self.function_to_apply = "softmax"
                elif (
                    hasattr(self.model.config, "function_to_apply")
                    and self.function_to_apply is None
                ):
                    self.function_to_apply = self.model.config.function_to_apply
                else:
                    self.function_to_apply = "none"
            # Extract the logits, convert to numpy and
            # apply the post-processing function
            outputs = model_outputs["logits"][0]
            outputs = outputs.numpy()
            if self.function_to_apply == "sigmoid":
                probabilities = sigmoid(outputs)
            elif self.function_to_apply == "softmax":
                probabilities = softmax(outputs)
            elif self.function_to_apply == "none":
                probabilities = outputs
            else:
                raise ValueError(
                    "Unrecognized `function_to_apply` "
                    f"argument: {self.function_to_apply}"
                )
            values, indices = torch.topk(probabilities, self.top_k)
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
class HuggingFaceTextClassificationInference(BaseAlgorithmFactory):
    """Inference for pre-trained Hugging Face text classification models.

    Args:
        model_id: The model id to use for text classification inference.
            The model id is of a pretrained model hosted inside a model
            repo on huggingface.co. Accepts resnet models.
        target_column_name: The target column on which the inference should be done.
        batch_size: The batch size for inference. Defaults to 1.
        function_to_apply: The function to apply to the model outputs in order
            to retrieve the scores. Accepts four different values: if this argument
            is not specified, then it will apply the following functions according
            to the number of labels - if the model has a single label, will apply
            the `sigmoid` function on the output; if the model has several labels,
            will apply the `softmax` function on the output. Possible values are:
            "sigmoid": Applies the sigmoid function on the output.
            "softmax": Applies the softmax function on the output.
            "none": Does not apply any function on the output. Default to None.
        seed: Sets the seed of the algorithm. For reproducible behavior
            it defaults to 42.
        top_k: The number of top labels that will be returned by the pipeline.
            Defaults to 1.

    Attributes:
        model_id: The model id to use for text classification inference.
            The model id is of a pretrained model hosted inside a model
            repo on huggingface.co. Accepts resnet models.
        target_column_name: The target column on which the inference should be done.
        batch_size: The batch size for inference. Defaults to 1.
        function_to_apply: The function to apply to the model outputs in order
            to retrieve the scores. Accepts four different values: if this argument
            is not specified, then it will apply the following functions according
            to the number of labels - if the model has a single label, will apply
            the `sigmoid` function on the output; if the model has several labels,
            will apply the `softmax` function on the output. Possible values are:
            "sigmoid": Applies the sigmoid function on the output.
            "softmax": Applies the softmax function on the output.
            "none": Does not apply any function on the output. Default to None.
        seed: Sets the seed of the algorithm. For reproducible behavior
            it defaults to 42.
        top_k: The number of top labels that will be returned by the pipeline.
            Defaults to 1.
    """

    def __init__(
        self,
        model_id: str,
        target_column_name: str,
        batch_size: int = 1,
        function_to_apply: Optional[_FunctionToApply] = None,
        seed: int = DEFAULT_SEED,
        top_k: int = 1,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.model_id = model_id
        self.target_column_name = target_column_name
        self.batch_size = batch_size
        self.function_to_apply = function_to_apply
        self.seed = seed
        self.top_k = top_k

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "model_id": fields.Str(required=True),
        "target_column_name": fields.Str(required=True),
        "batch_size": fields.Int(required=False),
        "function_to_apply": fields.Str(required=False, allow_none=True),
        "seed": fields.Int(required=False, missing=DEFAULT_SEED),
        "top_k": fields.Int(required=False),
    }

    def modeller(self, **kwargs: Any) -> _ModellerSide:
        """Returns the modeller side of the HuggingFaceTextClassificationInference algorithm."""  # noqa: B950
        return _ModellerSide(**kwargs)

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Returns the worker side of the HuggingFaceTextClassificationInference algorithm."""  # noqa: B950
        return _WorkerSide(
            model_id=self.model_id,
            target_column_name=self.target_column_name,
            batch_size=self.batch_size,
            function_to_apply=self.function_to_apply,
            seed=self.seed,
            top_k=self.top_k,
            **kwargs,
        )
