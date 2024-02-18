"""OpenTelemetry Task Metrics Setup."""
from pathlib import Path
from threading import Lock
from typing import (
    Dict,
    Iterable,
    List,
    Optional,
    Sequence as TypingSequence,
    Tuple,
    Union,
)
from uuid import UUID, uuid4

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc import _OTLP_GRPC_HEADERS
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    MetricExportResult,
    MetricReader,
    MetricsData,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ReadableSpan

from bitfount.config import BITFOUNT_STORAGE_PATH
from bitfount.exceptions import BitfountError
from bitfount.federated.algorithms.base import (
    _BaseAlgorithm,
    module_registry as algorithmRegistry,
)
from bitfount.federated.algorithms.model_algorithms.base import (
    _BaseWorkerModelAlgorithm,
)
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.transport.config import MessageServiceConfig
from bitfount.hub.authentication_flow import BitfountSession

logger = _get_federated_logger(__name__)


class TaskMeter:
    """Meter that can be used to report task metrics."""

    _algorithm_records_returned_observations: List[metrics.Observation] = []
    __algorithm_records_returned_lock = Lock()

    def __init__(self) -> None:
        # Creates a meter from the global meter provider
        meter = metrics.get_meter("TaskMeter")

        meter.create_observable_gauge(
            name="algorithm_records_returned",
            callbacks=[self._algorithm_records_returned_callback],
            description="The number of records returned by the algorithm",
        )

    def _algorithm_records_returned_callback(
        self, options: metrics.CallbackOptions
    ) -> Iterable[metrics.Observation]:
        """Callback to return algorithm_records_returned observations."""
        with self.__algorithm_records_returned_lock:
            observations = self._algorithm_records_returned_observations.copy()
            self._algorithm_records_returned_observations.clear()
            return observations

    def submit_algorithm_records_returned(
        self,
        *,
        records_count: int,
        task_id: str,
        algorithm: Union[_BaseAlgorithm, str],
        protocol_batch_num: Optional[int] = None,
        project_id: Optional[str] = None,
    ) -> None:
        """Submit algorithm_records_returned observation."""
        attributes = self._build_attributes(
            task_id=task_id,
            algorithm=algorithm,
            protocol_batch_num=protocol_batch_num,
            project_id=project_id,
        )

        with self.__algorithm_records_returned_lock:
            self._algorithm_records_returned_observations.append(
                metrics.Observation(
                    records_count,
                    attributes,
                )
            )

    def submit_algorithm_records_per_class_returned(
        self,
        *,
        records_count_per_class: Dict[str, int],
        task_id: str,
        algorithm: Union[_BaseAlgorithm, str],
        protocol_batch_num: Optional[int],
        project_id: Optional[str] = None,
    ) -> None:
        """Submit a algorithm_records_returned observation per class."""
        attributes = self._build_attributes(
            task_id=task_id,
            algorithm=algorithm,
            protocol_batch_num=protocol_batch_num,
            project_id=project_id,
        )

        with self.__algorithm_records_returned_lock:
            if len(records_count_per_class.keys()) > 0:
                for class_name, class_count in records_count_per_class.items():
                    attributes_with_class = attributes.copy()
                    attributes_with_class["records_class_name"] = class_name
                    self._algorithm_records_returned_observations.append(
                        metrics.Observation(
                            class_count,
                            attributes_with_class,
                        )
                    )
            else:
                self._algorithm_records_returned_observations.append(
                    metrics.Observation(
                        0,
                        attributes,
                    )
                )

    def _build_attributes(
        self,
        *,
        task_id: str,
        algorithm: Union[_BaseAlgorithm, str],
        protocol_batch_num: Optional[int],
        project_id: Optional[str],
    ) -> Dict[str, Union[str, int]]:
        algorithm_fqn: str
        model: Optional[str] = None
        if isinstance(algorithm, _BaseAlgorithm):
            algorithm_fqn, model = self._get_algorithm_properties(algorithm)
        else:
            algorithm_fqn = algorithm

        attributes: Dict[str, Union[str, int]] = {
            "task_id": task_id,
            "algorithm": algorithm_fqn,
        }

        if protocol_batch_num is not None:
            attributes["protocol_batch_num"] = protocol_batch_num

        if project_id is not None:
            attributes["project_id"] = project_id

        if model is not None:
            attributes["model"] = model

        return attributes

    def _get_algorithm_properties(
        self,
        algorithm: _BaseAlgorithm,
    ) -> Tuple[str, Optional[str]]:
        fqn = algorithm.__class__.__module__

        name: Optional[str] = algorithmRegistry.get(algorithm.__class__.__module__)
        if name is not None:
            fqn = f"{algorithm.__class__.__module__}.{name}"

        model: Optional[str] = None
        if isinstance(algorithm, _BaseWorkerModelAlgorithm):
            model = algorithm.model.class_name

        return (fqn, model)


task_meter: Optional[TaskMeter] = None
"""The OpenTelemetry Python SDK doesn't seem to have a way to unregister callbacks,
   (https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/metrics/api.md#asynchronous-gauge-operations)
   so to avoid creating a new gauge and registering a new callback that will have a
   reference kept my OpenTelemetry (memory leak) every time we instantiate a Protocol
   we have this global Meter that can be used by all Protocol instances."""

_task_meter_lock = Lock()


def _setup_metric_reader(session: BitfountSession) -> MetricReader:
    ms_config = MessageServiceConfig()
    exporter = BitfountOLTPMetricsExporter(
        session=session,
        endpoint=f"{ms_config.url}:{ms_config.port}",
        insecure=not ms_config.tls,
    )
    return PeriodicExportingMetricReader(exporter)


def setup_opentelemetry_metrics(
    *,
    session: BitfountSession,
) -> None:
    """Setup Open Telemetry metrics exporter and TaskMeter."""
    global task_meter, _task_meter_lock
    with _task_meter_lock:
        if task_meter is None:
            metric_reader = _setup_metric_reader(session)
            installation_uuid = get_installation_uuid()

            resource = Resource(attributes={"installation_uuid": installation_uuid})
            provider = MeterProvider(resource=resource, metric_readers=[metric_reader])

            # Sets the global default meter provider
            metrics.set_meter_provider(provider)

            # Sets the global TaskMeter
            task_meter = TaskMeter()


def get_task_meter() -> TaskMeter:
    """Fetch global TaskMeter."""
    if task_meter is not None:
        return task_meter

    raise BitfountError(
        "Global TaskMeter not found - "
        "need to call setup_opentelemetry_metrics once before"
    )


def get_installation_uuid(
    storage_path: Path = BITFOUNT_STORAGE_PATH,
) -> str:
    """Return the installation UUID."""
    uuid_path = storage_path / ".uuid"
    if uuid_path.exists():
        with open(uuid_path, encoding="utf-8") as f:
            uuid = f.read()
            try:
                UUID(uuid)
                return uuid
            except ValueError:
                logger.warning(
                    f"Could not parse contents of {uuid_path} as UUID: {uuid}"
                )

    uuid = str(uuid4())
    logger.info(
        f"Installation UUID not found at {uuid_path} - "
        f"generated new UUID ({uuid}) and will store it there"
    )
    with open(uuid_path, mode="w", encoding="utf-8") as f:
        f.write(uuid)

    return uuid


class BitfountOLTPMetricsExporter(OTLPMetricExporter):
    """OTLPMetricExporter that sends Bitfount session headers.

    The BitfountSession message_service_metadata property may change over time
    so we need to ensure we have it fresh when we export metrics.
    """

    _session: BitfountSession

    def __init__(self, *, session: BitfountSession, endpoint: str, insecure: bool):
        super().__init__(
            endpoint,
            insecure,
        )
        self._session = session

    def _export(
        self, data: Union[TypingSequence[ReadableSpan], MetricsData]
    ) -> MetricExportResult:
        self._headers = tuple(self._session.message_service_metadata) + tuple(
            _OTLP_GRPC_HEADERS
        )
        return super()._export(data)
