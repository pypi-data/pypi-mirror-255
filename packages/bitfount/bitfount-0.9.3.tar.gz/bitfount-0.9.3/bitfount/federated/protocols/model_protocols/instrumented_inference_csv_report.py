"""Copy of the InferenceAndCSVReport protocol that sends metrics to Bitfount."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Union, cast

import numpy as np
import pandas as pd

from bitfount.federated.algorithms.base import _BaseAlgorithm
from bitfount.federated.pod_vitals import _PodVitals
from bitfount.federated.protocols.model_protocols.inference_csv_report import (
    InferenceAndCSVReport,
    _InferenceAndCSVReportCompatibleAlgoFactory_,
    _InferenceAndCSVReportCompatibleHuggingFaceAlgoFactory,
    _InferenceAndCSVReportCompatibleModelAlgoFactory,
    _InferenceAndCSVReportCSVCompatibleWorkerAlgorithm,
    _InferenceAndCSVReportModelCompatibleWorkerAlgorithm,
    _InferenceAndCSVReportModelIncompatibleWorkerAlgorithm,
    _WorkerSide as _InferenceCSVWorkerSide,
)
from bitfount.federated.transport.opentelemetry import get_task_meter
from bitfount.federated.transport.worker_transport import _WorkerMailbox

if TYPE_CHECKING:
    from bitfount.hub.api import BitfountHub


class _WorkerSide(_InferenceCSVWorkerSide):
    """Worker side of the protocol.

    Args:
        algorithm: A list of algorithms to be run by the protocol. This should be
            a list of two algorithms, the first being the model inference algorithm
            and the second being the csv report algorithm.
        mailbox: The mailbox to use for communication with the Modeller.
        **kwargs: Additional keyword arguments.
    """

    def __init__(
        self,
        *,
        algorithm: Sequence[
            Union[
                _InferenceAndCSVReportModelCompatibleWorkerAlgorithm,
                _InferenceAndCSVReportModelIncompatibleWorkerAlgorithm,
                _InferenceAndCSVReportCSVCompatibleWorkerAlgorithm,
            ]
        ],
        mailbox: _WorkerMailbox,
        **kwargs: Any,
    ):
        super().__init__(algorithm=algorithm, mailbox=mailbox, **kwargs)

        self._task_meter = get_task_meter()
        self._task_id = mailbox._task_id if mailbox._task_id is not None else "None"

    async def run(
        self,
        pod_vitals: Optional[_PodVitals] = None,
        **kwargs: Any,
    ) -> Union[List[np.ndarray], pd.DataFrame, Dict[str, np.ndarray]]:
        """Runs the algorithm on worker side."""
        inference_and_csv_result = await super().run(pod_vitals=pod_vitals)
        model_predictions = cast(pd.DataFrame, inference_and_csv_result)

        protocol_batch_num = kwargs.get("batch_num", None)  # batch_num is 0-based
        algorithm: Union[_BaseAlgorithm, str] = (
            self.algorithm[0]
            if isinstance(self.algorithm[0], _BaseAlgorithm)  # should always be
            else self.algorithm[0].__class__.__module__
        )
        self._task_meter.submit_algorithm_records_returned(
            records_count=len(model_predictions.index),
            task_id=self._task_id,
            algorithm=algorithm,
            protocol_batch_num=protocol_batch_num,
            project_id=self.project_id,
        )

        return model_predictions


class InstrumentedInferenceAndCSVReport(InferenceAndCSVReport):
    """Protocol that sends telemetry metrics back to Bitfount.

    Extends InferenceAndCSVReport to send the number of records output to CSV.
    """

    def worker(
        self, mailbox: _WorkerMailbox, hub: BitfountHub, **kwargs: Any
    ) -> _WorkerSide:
        """Returns worker side of the protocol."""
        algorithms = cast(
            Sequence[
                Union[
                    _InferenceAndCSVReportCompatibleAlgoFactory_,
                    _InferenceAndCSVReportCompatibleModelAlgoFactory,
                    _InferenceAndCSVReportCompatibleHuggingFaceAlgoFactory,
                ]
            ],
            self.algorithms,
        )
        return _WorkerSide(
            algorithm=[algo.worker(hub=hub) for algo in algorithms],
            mailbox=mailbox,
            **kwargs,
        )
