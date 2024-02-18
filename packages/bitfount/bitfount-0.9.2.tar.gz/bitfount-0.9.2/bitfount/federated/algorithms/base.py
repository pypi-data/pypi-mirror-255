"""Base classes for all algorithms.

Each module in this package defines a single algorithm.

Attributes:
    registry: A read-only dictionary of algorithm factory names to their
              implementation classes.
"""
from __future__ import annotations

from abc import ABC, ABCMeta, abstractmethod
from functools import wraps
import inspect
from types import FunctionType, MappingProxyType, new_class
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    Mapping,
    Optional,
    Type,
    TypeVar,
)

from typing_extensions import ParamSpec

from bitfount.federated.exceptions import AlgorithmError
from bitfount.federated.helper import TaskContext
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.privacy.differential import DPPodConfig
from bitfount.federated.roles import _RolesMixIn
from bitfount.federated.types import AlgorithmType
from bitfount.hooks import BaseDecoratorMetaClass, HookType, get_hooks
from bitfount.types import T_FIELDS_DICT, T_NESTED_FIELDS, _BaseSerializableObjectMixIn

if TYPE_CHECKING:
    from bitfount.data.datasources.base_source import BaseSource

logger = _get_federated_logger(__name__)


class AlgorithmDecoratorMetaClass(BaseDecoratorMetaClass, type):
    """Decorates the `__init__`, `initialise` and `run` algorithm methods."""

    @staticmethod
    def decorator(f: Callable) -> Callable:
        """Hook and federated error decorators."""
        method_name = f.__name__
        if method_name == "__init__":

            @wraps(f)
            def init_wrapper(
                self: _BaseAlgorithm,
                *args: Any,
                **kwargs: Any,
            ) -> None:
                """Wraps __init__ method of algorithm.

                Calls relevant hooks before and after the algorithm is initialised.

                Args:
                    self: The algorithm instance.
                    hook_kwargs: Keyword arguments to pass to the hooks.
                    *args: Positional arguments to pass to the algorithm.
                    **kwargs: Keyword arguments to pass to the algorithm.
                """
                for hook in get_hooks(HookType.ALGORITHM):
                    hook.on_init_start(self)
                logger.debug(f"Calling method {method_name} from algorithm")
                f(self, *args, **kwargs)
                for hook in get_hooks(HookType.ALGORITHM):
                    hook.on_init_end(self)

            return init_wrapper

        elif method_name == "initialise":

            @wraps(f)
            def initialise_wrapper(
                self: _BaseAlgorithm,
                *args: Any,
                **kwargs: Any,
            ) -> Any:
                """Wraps initialise method of algorithm.

                For the Worker side wraps exceptions in an AlgorithmError
                and logs a federated error to the modeller.

                Args:
                    self: Algorithm instance.
                    *args: Positional arguments to pass to the initialise method.
                    **kwargs: Keyword arguments to pass to the initialise method.

                Returns:
                    Return value of the run method.
                """
                task_context: Optional[TaskContext] = None
                if isinstance(self, BaseModellerAlgorithm):
                    task_context = TaskContext.MODELLER
                elif isinstance(self, BaseWorkerAlgorithm):
                    task_context = TaskContext.WORKER

                try:
                    logger.debug(f"Calling method {method_name} from algorithm")
                    result = f(self, *args, **kwargs)
                    return result
                except Exception as e:
                    if task_context == TaskContext.WORKER:
                        # TODO: [BIT-1619] change to federated_exception
                        logger.federated_error(str(e))
                        raise AlgorithmError(
                            f"Algorithm function {method_name} from "
                            f"{self.__class__.__module__} "
                            f"raised the following exception: {e}"
                        ) from e
                    else:
                        raise e

            return initialise_wrapper

        elif method_name == "run":

            @wraps(f)
            def run_wrapper(
                self: _BaseAlgorithm,
                *args: Any,
                **kwargs: Any,
            ) -> Any:
                """Wraps run method of algorithm.

                Calls hooks before and after the run method is called.

                For the Worker side wraps exceptions in an AlgorithmError
                and logs a federated error to the modeller.

                Args:
                    self: Algorithm instance.
                    *args: Positional arguments to pass to the run method.
                    **kwargs: Keyword arguments to pass to the run method.

                Returns:
                    Return value of the run method.
                """
                task_context: Optional[TaskContext] = None
                if isinstance(self, BaseModellerAlgorithm):
                    task_context = TaskContext.MODELLER
                elif isinstance(self, BaseWorkerAlgorithm):
                    task_context = TaskContext.WORKER

                hooks = get_hooks(HookType.ALGORITHM)
                for hook in hooks:
                    hook.on_run_start(self, task_context)

                try:
                    logger.debug(f"Calling method {method_name} from algorithm")
                    result = f(self, *args, **kwargs)
                    for hook in hooks:
                        hook.on_run_end(self, task_context)
                    return result
                except Exception as e:
                    if task_context == TaskContext.WORKER:
                        # TODO: [BIT-1619] change to federated_exception
                        logger.federated_error(str(e))
                        raise AlgorithmError(
                            f"Algorithm function {method_name} from "
                            f"{self.__class__.__module__} "
                            f"raised the following exception: {e}"
                        ) from e
                    else:
                        raise e

            return run_wrapper

        # This is not expected to ever happen, but if it does, raise an error
        raise ValueError(f"Method {method_name} cannot be decorated.")

    @classmethod
    def do_decorate(cls, attr: str, value: Any) -> bool:
        """Checks if an object should be decorated.

        Only the __init__, initialise and run methods should be decorated.
        """
        return attr in ("__init__", "initialise", "run") and isinstance(
            value, FunctionType
        )


# The metaclass for the BaseAlgorithm must also have all the same classes in its own
# inheritance chain so we need to create a thin wrapper around it.
AbstractAlgorithmDecoratorMetaClass = new_class(
    "AbstractAlgorithmDecoratorMetaClass",
    (ABCMeta, AlgorithmDecoratorMetaClass),
    {},
)

_P = ParamSpec("_P")
_R = TypeVar("_R")


class _BaseAlgorithm(ABC, metaclass=AbstractAlgorithmDecoratorMetaClass):  # type: ignore[misc] # Reason: see above # noqa: B950
    """Blueprint for either the modeller side or the worker side of BaseAlgorithm."""

    def __init__(self, **kwargs: Any):
        super().__init__()
        self.class_name = module_registry.get(self.__class__.__module__, "")

    @abstractmethod
    def run(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Runs the algorithm."""
        ...


class BaseModellerAlgorithm(_BaseAlgorithm, ABC):
    """Modeller side of the algorithm."""

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    @abstractmethod
    def initialise(self, task_id: Optional[str], **kwargs: Any) -> None:
        """Initialise the algorithm."""
        raise NotImplementedError


class BaseWorkerAlgorithm(_BaseAlgorithm, ABC):
    """Worker side of the algorithm."""

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def _apply_pod_dp(self, pod_dp: Optional[DPPodConfig]) -> None:
        """Applies pod-level Differential Privacy constraints.

        Subclasses should override this method if DP is supported.

        Args:
            pod_dp: The pod DP constraints to apply or None if no constraints.
        """
        pass

    @abstractmethod
    def initialise(
        self,
        datasource: BaseSource,
        pod_dp: Optional[DPPodConfig] = None,
        pod_identifier: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialises the algorithm.

        This method is only called once regardless of the number of batches in the task.

        :::note

        This method must call the `initialise_data` method.

        :::

        """
        raise NotImplementedError

    def initialise_data(self, datasource: BaseSource) -> None:
        """Initialises the algorithm with data.

        This method will be called once per task batch. It is expected that algorithms
        will override this method to initialise their data in the required way.

        :::note

        This is called by the `initialise` method and should not be called directly by
        the algorithm or protocol.

        :::
        """
        self.datasource = datasource


# The mutable underlying dict that holds the registry information
_registry: Dict[str, Type[BaseAlgorithmFactory]] = {}
# The read-only version of the registry that is allowed to be imported
registry: Mapping[str, Type[BaseAlgorithmFactory]] = MappingProxyType(_registry)

# The mutable underlying dict that holds the mapping of module name to class name
_module_registry: Dict[str, str] = {}
# The read-only version of the module registry that is allowed to be imported
module_registry: Mapping[str, str] = MappingProxyType(_module_registry)


class BaseAlgorithmFactory(ABC, _RolesMixIn, _BaseSerializableObjectMixIn):
    """Base algorithm factory from which all other algorithms must inherit.

    Attributes:
       class_name: The name of the algorithm class.
    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {}
    nested_fields: ClassVar[T_NESTED_FIELDS] = {}

    def __init__(self, **kwargs: Any):
        try:
            self.class_name = AlgorithmType[type(self).__name__].value
        except KeyError:
            # Check if the algorithm is a plug-in
            self.class_name = type(self).__name__
        super().__init__(**kwargs)

    @classmethod
    def __init_subclass__(cls, **kwargs: Any):
        if not inspect.isabstract(cls):
            logger.debug(f"Adding {cls.__name__}: {cls} to Algorithm registry")
            _registry[cls.__name__] = cls
            _module_registry[cls.__module__] = cls.__name__
