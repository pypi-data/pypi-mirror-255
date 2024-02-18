"""Module for creating Pod Vitals webserver."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
import logging
import os
import socket
import threading
import time
from typing import TYPE_CHECKING

from aiohttp import web
from aiohttp.web_app import Application
from aiohttp.web_runner import GracefulExit
import desert

from bitfount.data.datastructure import DataStructure
from bitfount.data.utils import check_datastructure_schema_compatibility
from bitfount.runners.config_schemas import DataStructureConfig

if TYPE_CHECKING:
    from asyncio import AbstractEventLoop
    from concurrent.futures import Future as ConcurrentFuture
    from typing import Dict, List, Optional

    from aiohttp.web_request import Request
    from aiohttp.web_response import Response

    from bitfount.data.schema import BitfountSchema
    from bitfount.types import _JSONDict

logger = logging.getLogger(__name__)

MAX_TASK_EXECUTION_TIME = 3_600


@dataclass
class _PodVitals:
    """Tracks statistics used to determine a pod's vitals."""

    # On initalization, set last_task_execution_time
    # to current time so that we don't kill a Pod
    # before it has had time to pick up its first task
    _last_task_execution_time = time.time()
    _last_task_execution_lock = threading.Lock()
    # Create event to monitor when pod is up and ready to retrieve tasks
    _pod_ready_event = threading.Event()

    @property
    def last_task_execution_time(self) -> float:
        """The timestamp of the lastest task executed in the pod."""
        with self._last_task_execution_lock:
            return self._last_task_execution_time

    @last_task_execution_time.setter
    def last_task_execution_time(self, time: float) -> None:
        """Set last_task_execution_time."""
        with self._last_task_execution_lock:
            self._last_task_execution_time = time

    def is_pod_ready(self) -> bool:
        """Determines if the pod is marked as ready."""
        return self._pod_ready_event.is_set()

    def mark_pod_ready(self) -> None:
        """Marks pod as ready and live."""
        self._pod_ready_event.set()


class _PodVitalsHandler:
    """_PodVitals webserver."""

    def __init__(self, pod_vitals: _PodVitals, pod_schemas: Dict[str, BitfountSchema]):
        """Create a new _PodVitalsHandler.

        Args:
            pod_vitals: Vitals class that contains information/methods about pod
                execution and pod readiness.
            pod_schemas: A mapping of dataset name (not identifier) to the schema
                of that dataset for all datasets served by this pod.
        """
        self._pod_vitals = pod_vitals
        self._schemas = pod_schemas

        self._app = Application()
        self._app.add_routes(
            [
                web.post("/compatibility-check", self.compatibility_check),
                web.get("/dataset-names", self.dataset_names),
                web.get("/health", self.health),
                web.get("/schemas", self.get_schemas),
                web.get("/status", self.status),
                web.post("/stop", self._stop_endpoint),
                web.delete("/stop", self._stop_endpoint),
            ]
        )

        self._lock = threading.Lock()
        self._server_thread: Optional[threading.Thread] = None
        self._event_loop: Optional[AbstractEventLoop] = None

    async def compatibility_check(self, request: Request) -> Response:
        """Check compatibility of this pod with a task.

        The request should be a JSON POST request containing the following:
            - datasetName: string - the name of the dataset within the pod to check
                  compatibility with.
            - taskDataStructure: object - the dict representation of the task's
                  datastructure configuration.
        """
        try:
            json = await request.json()

            ds_name: str = json["datasetName"]

            if ds_name not in self._schemas:
                return web.json_response(
                    {
                        "error": (
                            f'dataset "{ds_name}" could not be found'
                            f" in this pod's schemas."
                        )
                    },
                    status=404,
                )

            datastructure_config: DataStructureConfig = desert.schema(
                DataStructureConfig
            ).load(json["taskDataStructure"])
            datastructure: DataStructure = DataStructure.create_datastructure(
                datastructure_config.table_config,
                datastructure_config.select,
                datastructure_config.transform,
                datastructure_config.assign,
            )

            compat, msgs = check_datastructure_schema_compatibility(
                datastructure, self._schemas[ds_name]
            )
            return web.json_response(
                {"compatibility": compat.name, "msgs": msgs}, status=200
            )
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def dataset_names(self, request: Request) -> Response:
        """Retrieve the names of the datasets in this pod."""
        return web.json_response(sorted(self._schemas.keys()), status=200)

    async def health(self, request: Request) -> Response:
        """Determine a pod's health.

        We define a pod as healthy if its lastest task execution time
        is less than 1 hour ago.
        """
        is_healthy = False
        now = time.time()
        if now - self._pod_vitals.last_task_execution_time < MAX_TASK_EXECUTION_TIME:
            is_healthy = True
        return web.json_response(
            {
                "healthy": is_healthy,
                "ready": self._pod_vitals.is_pod_ready(),
            },
            status=200,
        )

    async def get_schemas(self, request: Request) -> Response:
        """Retrieve the schema(s) of the datasets in this pod.

        A single dataset can be specified by putting `datasetName` in the query
        string of the request.

        Otherwise, all schemas are returned.

        Returns:
            - A JSON list of the JSON representations of the requested schema(s).
        """
        query = request.query

        schemas: List[BitfountSchema] = []
        try:
            dataset_name: str = query["datasetName"]
        except KeyError:
            schemas = list(self._schemas.values())
        else:
            try:
                schemas.append(self._schemas[dataset_name])
            except KeyError:
                return web.json_response(
                    {
                        "error": (
                            f'dataset "{dataset_name}" could not be found'
                            f" in the set of schemas"
                        )
                    },
                    status=404,
                )

        schemas_dump: List[_JSONDict] = [schema.to_json() for schema in schemas]
        return web.json_response(schemas_dump, status=200)

    async def status(self, request: Request) -> Response:
        """Handler to support `/status` requests."""
        return web.json_response({"status": "OK"}, status=200)

    async def _stop_endpoint(self, request: Request) -> Response:
        logger.info("Pod vitals server stop requested via /stop; stopping...")
        await self._stop_server()
        return web.json_response({"status": "OK"}, status=200)

    def _get_pod_vitals_port(self) -> int:
        """Determine port to serve _PodVitals webserver over.

        If env var `BITFOUNT_POD_VITALS_PORT` is set we use this
        port number. Else we dynamically select an open ports.
        Dynamically selecting an open port allows end users to
        run multiple pods locally.
        """
        pod_vitals_port = os.getenv("BITFOUNT_POD_VITALS_PORT")
        if pod_vitals_port:
            try:
                port = int(pod_vitals_port)
            except ValueError as e:
                raise ValueError(
                    f"BITFOUNT_POD_VITALS_PORT must be an integer. "
                    f"BITFOUNT_POD_VITALS_PORT set to '{pod_vitals_port}'"
                ) from e
            if not (1 <= port <= 65535):
                raise ValueError(
                    "Invalid BITFOUNT_POD_VITALS_PORT given. Must be in range [1-65535]"
                )
        else:
            port = self._open_socket()
        return port

    def _open_socket(self) -> int:
        """Retrieves an open tcp port.

        This introduces the risk of race condition as we
        choose an open port here but do not claim it until
        we start the server. If the pod is running inside
        a container the BITFOUNT_POD_VITALS_PORT
        env var should be set.
        """
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp.bind(("", 0))
        _, port = tcp.getsockname()
        tcp.close()
        return int(port)

    def _run_server(self) -> None:
        with self._lock:
            if self._event_loop is not None:
                if self._event_loop.is_closed():
                    logger.warning(
                        "Found existing closed event loop for pod vitals server;"
                        " overriding..."
                    )
                else:
                    raise ValueError("Event loop is already set for pod vitals server")

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._event_loop = loop

        # Get port
        port = self._get_pod_vitals_port()

        # Host needs to be set to `0.0.0.0` to bind in Docker container
        # Could be made configurable in future?
        # NOTE: run_app will implicitly handle closing the loop
        # Marked nosec as this is just serving a static healthcheck endpoint
        logger.info(f"Running Pod Vitals interface on: http://localhost:{port}/health")
        web.run_app(
            app=self._app,
            host="0.0.0.0",  # nosec hardcoded_bind_all_interfaces
            port=port,
            handle_signals=False,
            loop=self._event_loop,
        )
        logger.info("Pod vitals server finished")

    async def _stop_server(self) -> None:
        logger.debug("Stopping pod vitals server: raising GracefulExit")
        raise GracefulExit()

    def start(self, thread_name: Optional[str] = None, daemon: bool = False) -> None:
        """Start _PodVitals webserver."""
        with self._lock:
            if self._server_thread is not None:
                if not self._server_thread.is_alive():
                    logger.warning("Found dead pod vitals server thread; overriding...")
                else:
                    raise ValueError(
                        "Pod vitals server already has running server thread assigned"
                    )

            self._server_thread = threading.Thread(target=self._run_server)
            if thread_name:
                self._server_thread.name = thread_name
            if daemon:
                self._server_thread.daemon = daemon

            self._server_thread.start()
            logger.debug(
                f"Running pod vitals server in thread {self._server_thread.ident}"
            )

    def stop(self, timeout: int) -> None:
        logger.info("Stopping pod vitals server")

        with self._lock:
            if self._event_loop is None or self._event_loop.is_closed():
                logger.warning(
                    "Event loop is not set or is closed for pod vitals server,"
                    " server may have already stopped."
                )
                return None

        coro_result: ConcurrentFuture = asyncio.run_coroutine_threadsafe(
            self._stop_server(), self._event_loop
        )

        try:
            logger.debug(
                "Stopping pod vitals server: waiting for coroutine to complete"
            )
            coro_result.result(timeout)
        except GracefulExit:
            logger.debug("Stopping pod vitals server: coroutine complete")
        finally:
            with self._lock:
                if self._server_thread is not None:
                    self._server_thread.join(timeout=timeout)
                if self._server_thread is not None and self._server_thread.is_alive():
                    logger.warning(
                        f"Pod vitals server thread was still alive"
                        f" after {timeout} seconds"
                    )
                if self._event_loop is not None and not self._event_loop.is_closed():
                    logger.warning(
                        f"Pod vitals server event loop was not closed"
                        f" after {timeout} seconds"
                    )

                # aiohttp handles the loop closing, so we don't need to
                self._event_loop = None
                self._server_thread = None
