"""Hugging Face Zero-Shot Image Classification Algorithm."""
from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    List,
    Mapping,
    Optional,
    Union,
    cast,
)

from marshmallow import fields
import pandas as pd
from transformers import (
    AutoImageProcessor,
    AutoModelForZeroShotImageClassification,
    AutoTokenizer,
    pipeline,
    set_seed,
)

from bitfount.data.datasources.base_source import BaseSource
from bitfount.federated.algorithms.base import (
    BaseAlgorithmFactory,
    BaseModellerAlgorithm,
    BaseWorkerAlgorithm,
)
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.types import (
    HuggingFaceImageClassificationInferenceDefaultReturnType,
)
from bitfount.types import T_FIELDS_DICT
from bitfount.utils import DEFAULT_SEED, delegates

if TYPE_CHECKING:
    from bitfount.federated.privacy.differential import DPPodConfig


logger = _get_federated_logger(__name__)


class _ModellerSide(BaseModellerAlgorithm):
    """Modeller side of the HuggingFaceZeroShotImageClassificationInference algorithm."""  # noqa: B950

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
    """Worker side of the HuggingFaceZeroShotImageClassificationInference algorithm."""  # noqa: B950

    def __init__(
        self,
        model_id: str,
        image_column_name: str,
        candidate_labels: List[str],
        batch_size: int = 1,
        class_outputs: Optional[List[str]] = None,
        hypothesis_template: Optional[str] = None,
        seed: int = DEFAULT_SEED,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.model_id = model_id
        self.image_column_name = image_column_name
        self.batch_size = batch_size
        self.class_outputs = class_outputs
        self.candidate_labels = candidate_labels
        self.hypothesis_template = hypothesis_template
        self.seed = seed

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
        set_seed(self.seed)
        self.image_processor = AutoImageProcessor.from_pretrained(self.model_id)
        self.model = AutoModelForZeroShotImageClassification.from_pretrained(
            self.model_id
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.pipe = pipeline(
            "zero-shot-image-classification",
            model=self.model,
            image_processor=self.image_processor,
            tokenizer=self.tokenizer,
        )

    def run(
        self,
    ) -> Union[
        pd.DataFrame,
        HuggingFaceImageClassificationInferenceDefaultReturnType,
        Dict[str, Any],
    ]:
        """Runs the pipeline for zero-shot image classification."""
        if self.hypothesis_template is not None:
            # "If" statement here as hypothesis_template=None raises error
            # on the pipeline
            preds = self.pipe(
                self.datasource.get_column(self.image_column_name).tolist(),
                batch_size=self.batch_size,
                candidate_labels=self.candidate_labels,
                hypothesis_template=self.hypothesis_template,
            )
        else:
            preds = self.pipe(
                self.datasource.get_column(self.image_column_name).tolist(),
                batch_size=self.batch_size,
                candidate_labels=self.candidate_labels,
            )
        # Predictions from the above pipeline are returned as a nested
        # list of dictionaries. Each list of dictionaries corresponds
        # to the scores and different labels for a specific datapoint,
        # chosen from the candidate labels.

        predictions = cast(
            HuggingFaceImageClassificationInferenceDefaultReturnType, preds
        )
        if self.class_outputs:
            if len(predictions[0]) == len(self.class_outputs):
                # this is how all built in models return prediction outputs.
                return pd.DataFrame(data=predictions, columns=self.class_outputs)
            elif len(predictions) == len(self.class_outputs):
                # we can only return dataframe if all arrays have 1d dimension
                dim_check = len([item for item in predictions if len(item) > 1])
                if dim_check == 0:
                    # we return dataframe
                    return pd.DataFrame(
                        dict(zip(self.class_outputs, predictions)),
                        columns=self.class_outputs,
                    )
                else:
                    # we return dictionary
                    return {
                        output: pred
                        for output, pred in zip(self.class_outputs, predictions)
                    }
            else:
                logger.warning(
                    "Class outputs provided do not match the model prediction output. "
                    f"You provided a list of {len(self.class_outputs)}, and "
                    f"the model predictions are a list of {len(predictions[0])}. "
                    "Outputting predictions as a list of numpy arrays."
                )
                return predictions
        else:
            return predictions


@delegates()
class HuggingFaceZeroShotImageClassificationInference(BaseAlgorithmFactory):
    """Inference for pre-trained Hugging Face zero shot image classification models.

    Args:
        model_id: The model id to use for zero shot image classification
            inference. The model id is of a pretrained model hosted inside
            a model repo on huggingface.co.
        image_column_name: The image column on which the inference should be done.
        candidate_labels: The candidate labels for this image.
        batch_size: The batch size for inference. Defaults to 1.
        class_outputs: A list of strings corresponding to prediction outputs.
            If provided, the model will return a dataframe of results with the
            class outputs list elements as columns. Defaults to None.
        hypothesis_template:  The sentence used in conjunction with candidate_labels
            to attempt the image classification by replacing the placeholder with the
            candidate_labels. Then likelihood is estimated by using logits_per_image.
            Defaults to None.
        seed: Sets the seed of the algorithm. For reproducible behavior
            it defaults to 42.

    Attributes:
        model_id: The model id to use for zero shot image classification
            inference. The model id is of a pretrained model hosted inside
            a model repo on huggingface.co.
        image_column_name: The image column on which the inference should be done.
        candidate_labels: The candidate labels for this image.
        class_outputs: A list of strings corresponding to prediction outputs.
            If provided, the model will return a dataframe of results with the
            class outputs list elements as columns. Defaults to None.
        batch_size: The batch size for inference. Defaults to 1.
        hypothesis_template:  The sentence used in conjunction with candidate_labels
            to attempt the image classification by replacing the placeholder with the
            candidate_labels. Then likelihood is estimated by using logits_per_image.
            Defaults to None.
        seed: Sets the seed of the algorithm. For reproducible behavior
            it defaults to 42.
    """

    def __init__(
        self,
        model_id: str,
        image_column_name: str,
        candidate_labels: List[str],
        batch_size: int = 1,
        class_outputs: Optional[List[str]] = None,
        hypothesis_template: Optional[str] = None,
        seed: int = DEFAULT_SEED,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.model_id = model_id
        self.image_column_name = image_column_name
        self.batch_size = batch_size
        self.candidate_labels = candidate_labels
        self.class_outputs = class_outputs
        self.hypothesis_template = hypothesis_template
        self.seed = seed

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "model_id": fields.Str(required=True),
        "image_column_name": fields.Str(required=True),
        "candidate_labels": fields.List(fields.String(), required=True),
        "batch_size": fields.Int(required=False),
        "class_outputs": fields.List(fields.String(), allow_none=True),
        "hypothesis_template": fields.Str(allow_none=True),
        "seed": fields.Int(required=False, missing=DEFAULT_SEED),
    }

    def modeller(self, **kwargs: Any) -> _ModellerSide:
        """Returns the modeller side of the HuggingFaceZeroShotImageClassificationInference algorithm."""  # noqa: B950
        return _ModellerSide(**kwargs)

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Returns the worker side of the HuggingFaceZeroShotImageClassificationInference algorithm."""  # noqa: B950
        return _WorkerSide(
            model_id=self.model_id,
            candidate_labels=self.candidate_labels,
            image_column_name=self.image_column_name,
            batch_size=self.batch_size,
            class_outputs=self.class_outputs,
            hypothesis_template=self.hypothesis_template,
            seed=self.seed,
            **kwargs,
        )
