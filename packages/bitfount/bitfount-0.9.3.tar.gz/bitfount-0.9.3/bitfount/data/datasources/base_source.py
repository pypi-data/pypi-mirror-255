"""Module containing BaseSource class.

BaseSource is the abstract data source class from which all concrete data sources
must inherit.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import date, datetime
import functools
from functools import cached_property
import inspect
import logging
from logging.handlers import QueueHandler
import os
from pathlib import Path
import random
import shutil
import sys
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Final,
    Iterable,
    Iterator,
    List,
    Literal,
    Optional,
    Sequence,
    Set,
    Tuple,
    TypeVar,
    Union,
    cast,
)

from filetype import guess_extension
from mypy_extensions import Arg, DefaultNamedArg, KwArg, VarArg
import numpy as np
import pandas as pd
from pandas.core.dtypes.cast import (  # type: ignore[attr-defined] # Reason: this function _is_ defined but is technically private # noqa: B950
    find_common_type,
)
from pandas.core.dtypes.common import is_datetime64_any_dtype as is_datetime
import psutil

from bitfount.config import BITFOUNT_CACHE_DIR
from bitfount.data.datasources.types import Date, DateTD
from bitfount.data.datasources.utils import (
    FILE_SYSTEM_ITERABLE_METADATA_COLUMNS,
    LAST_MODIFIED_METADATA_COLUMN,
    ORIGINAL_FILENAME_METADATA_COLUMN,
    _modify_column,
    _modify_file_paths,
)
from bitfount.data.datasplitters import DatasetSplitter, SplitterDefinedInData
from bitfount.data.exceptions import DataNotLoadedError, IterableDataSourceError
from bitfount.data.persistence.base import DataPersister
from bitfount.data.types import (
    DataPathModifiers,
    _Column,
    _GetColumnCallable,
    _GetDtypesCallable,
    _SingleOrMulti,
)
from bitfount.data.utils import _generate_dtypes_hash, _hash_str
from bitfount.hooks import HookType, get_hooks
from bitfount.types import _Dtypes
from bitfount.utils import delegates, seed_all
from bitfount.utils.logging_utils import (
    _get_bitfount_console_handler,
    _get_bitfount_log_file_handler,
)

if TYPE_CHECKING:
    from queue import Queue

logger = logging.getLogger(__name__)

# Suffix used for caching images in the file system.
FILE_SYSTEM_ITERABLE_IMAGE_CACHE_SUFFIX: str = "-cache"

# The following constants are used for fast loading of data. Fast loading is used to
# speed up the process of schema generation where only a small subset of the data is
# loaded.
FAST_LOAD_NUMBER_OF_FILES_PERCENTAGE: float = 0.01
FAST_LOAD_MINIMUM_NUMBER_OF_FILES_WITHOUT_NEW_FIELDS: int = 3
FAST_LOAD_MAXIMUM_NUMBER_OF_FILES_WITHOUT_NEW_FIELDS: int = 10
FAST_LOAD_MAXIMUM_NUMBER_OF_FILES_TO_LOAD: int = 50

# Used for converting megabytes to bytes
NUM_BYTES_IN_A_MEGABYTE: Final[int] = 1024 * 1024

# This is used for annotating the data in the datasource with
# the inferred label
BITFOUNT_INFERRED_LABEL_COLUMN: str = "BITFOUNT_INFERRED_LABEL"

# This determines the maximum number of multiprocessing workers that can be used
# for file processing parallelisation.
MAX_NUM_MULTIPROCESSING_WORKERS: Final[int] = 5


T = TypeVar("T", bound="BaseSource")
BaseSourceInitSignature = Callable[
    [
        Arg(T, "self"),  # noqa: F821
        VarArg(Any),
        DefaultNamedArg(Optional[DatasetSplitter], "data_splitter"),  # noqa: F821
        DefaultNamedArg(Optional[int], "seed"),  # noqa: F821
        DefaultNamedArg(
            Optional[Dict[str, DataPathModifiers]], "modifiers"  # noqa: F821
        ),
        DefaultNamedArg(Union[str, Sequence[str], None], "ignore_cols"),  # noqa: F821
        KwArg(Any),
    ],
    None,
]


class BaseSource(ABC):
    """Abstract Base Source from which all other data sources must inherit.

    Args:
        data_splitter: Approach used for splitting the data into training, test,
            validation. Defaults to None.
        seed: Random number seed. Used for setting random seed for all libraries.
            Defaults to None.
        modifiers: Dictionary used for modifying paths/ extensions in the dataframe.
            Defaults to None.
        ignore_cols: Column/list of columns to be ignored from the data.
            Defaults to None.

    Attributes:
        data: A Dataframe-type object which contains the data.
        data_splitter: Approach used for splitting the data into training, test,
            validation.
        seed: Random number seed. Used for setting random seed for all libraries.
    """

    def __init__(
        self,
        data_splitter: Optional[DatasetSplitter] = None,
        seed: Optional[int] = None,
        modifiers: Optional[Dict[str, DataPathModifiers]] = None,
        ignore_cols: Optional[Union[str, Sequence[str]]] = None,
        **kwargs: Any,
    ) -> None:
        self._base_source_init = True
        self.data_splitter = data_splitter
        self.seed = seed
        self._modifiers = modifiers
        self._data_is_split: bool = False
        self._data_is_loaded: bool = False
        self._is_task_running: bool = False
        seed_all(self.seed)

        self._train_idxs: Optional[np.ndarray] = None
        self._validation_idxs: Optional[np.ndarray] = None
        self._test_idxs: Optional[np.ndarray] = None

        self._data: pd.DataFrame
        self._table_hashes: Set[str] = set()

        self._ignore_cols: List[str] = []
        if isinstance(ignore_cols, str):
            self._ignore_cols = [ignore_cols]
        elif ignore_cols is not None:
            self._ignore_cols = list(ignore_cols)

        for unexpected_kwarg in kwargs:
            logger.warning(f"Ignoring unexpected keyword argument {unexpected_kwarg}")

        super().__init__()

    def __init_subclass__(cls, **kwargs: Any) -> None:
        if not (inspect.isabstract(cls) or ABC in cls.__bases__):
            cls.get_dtypes = cls._get_dtypes()  # type: ignore[method-assign] # reason: wrap subclass get_dtypes # noqa: B950
            cls.get_column = cls._get_column()  # type: ignore[method-assign] # reason: wrap subclass get_column # noqa: B950

    @classmethod
    def _get_dtypes(cls) -> _GetDtypesCallable:
        """Decorate subclass' get_dtypes implementation.

        Decorate subclass' implementation of get_dtypes to handle ignored
        columns and handle `_table_hashes`.
        """
        subclass_get_dtypes = cls.get_dtypes

        def get_dtypes(self: BaseSource, *args: Any, **kwargs: Any) -> _Dtypes:
            dtypes: _Dtypes = subclass_get_dtypes(self, *args, **kwargs)
            if self._ignore_cols:
                for col in self._ignore_cols:
                    if col in dtypes:
                        del dtypes[col]
            self._table_hashes.add(_generate_dtypes_hash(dtypes))
            return dtypes

        return get_dtypes

    @classmethod
    def _get_column(
        cls,
    ) -> _GetColumnCallable:
        """Decorate subclass' get_column implementation.

        Decorate subclass' implementation of get_column to handle ignored
        columns and modifiers.
        """
        subclass_get_column = cls.get_column

        def get_column(
            self: BaseSource, col_name: str, *args: Any, **kwargs: Any
        ) -> _Column:
            column = subclass_get_column(self, col_name, *args, **kwargs)
            if self._modifiers:
                if modifier_dict := self._modifiers.get(col_name):
                    column = _modify_column(column, modifier_dict)
            return column

        return get_column

    @property
    def is_task_running(self) -> bool:
        """Returns True if a task is running."""
        return self._is_task_running

    @is_task_running.setter
    def is_task_running(self, value: bool) -> None:
        """Sets `_is_task_running` to `value`."""
        self._is_task_running = value

    @property
    def is_initialised(self) -> bool:
        """Checks if `BaseSource` was initialised."""
        if hasattr(self, "_base_source_init"):
            return True
        else:
            return False

    @property
    def data(self) -> pd.DataFrame:
        """A property containing the underlying dataframe if the data has been loaded.

        Raises:
            DataNotLoadedError: If the data has not been loaded yet.
        """
        if self._data_is_loaded:
            return self._data
        else:
            raise DataNotLoadedError(
                "Data is not loaded yet. Please call `load_data` first."
            )

    @data.setter
    def data(self, _data: Optional[pd.DataFrame]) -> None:
        """Data setter."""
        self._data_setter(_data)

    def _data_setter(self, _data: Optional[pd.DataFrame]) -> None:
        """Implementation method for data setter."""
        if _data is not None:
            if isinstance(_data, pd.DataFrame):
                if self._ignore_cols:
                    # If columns already ignored in data, ignore errors.
                    _data = _data.drop(columns=self._ignore_cols, errors="ignore")
                self._data = _data

                if self._modifiers:
                    _modify_file_paths(self._data, self._modifiers)

                self._data_is_loaded = True
            else:
                raise TypeError(
                    "Invalid data attribute. "
                    "Expected pandas dataframe for attribute 'data' "
                    f"but received :{type(_data)}"
                )

    @property
    def hash(self) -> str:
        """The hash associated with this BaseSource.

        This is the hash of the static information regarding the underlying DataFrame,
        primarily column names and content types but NOT anything content-related
        itself. It should be consistent across invocations, even if additional data
        is added, as long as the DataFrame is still compatible in its format.

        Returns:
            The hexdigest of the DataFrame hash.
        """
        if not self._table_hashes:
            raise DataNotLoadedError(
                "Data is not loaded yet. Please call `get_dtypes` first."
            )
        else:
            return _hash_str(str(sorted(self._table_hashes)))

    @staticmethod
    def _get_data_dtypes(data: pd.DataFrame) -> _Dtypes:
        """Returns the nullable column types of the dataframe.

        This is called by the `get_dtypes` method. This method also overrides datetime
        column dtypes to be strings. This is not done for date columns which are of
        type object.
        """
        data = data.convert_dtypes()
        dtypes: _Dtypes = data.dtypes.to_dict()
        for name in list(dtypes):
            if is_datetime(data[name]):
                dtypes[name] = pd.StringDtype()

        return dtypes

    def load_data(self, **kwargs: Any) -> None:
        """Load the data for the datasource.

        Raises:
            TypeError: If data format is not supported.
        """
        if not self._data_is_loaded:
            if (data := self.get_data(**kwargs)) is not None:
                self.data = data
            elif not self.iterable:
                logger.warning(
                    f"Datasource {self} returned None from get_data()"
                    f" but {self.iterable=}"
                )
            else:
                logger.debug(
                    f"Datasource {self} returned None from get_data()"
                    f" (expected as {self.iterable=})"
                )
        else:
            logger.warning(
                f"Datasource {self} has already been loaded; will not load again."
            )

    def get_values(
        self, col_names: List[str], **kwargs: Any
    ) -> Dict[str, Iterable[Any]]:
        """Get distinct values from list of columns."""
        dic: Dict[str, Iterable[Any]] = {}

        for col in col_names:
            try:
                dic[col] = self.data[col].unique()
            except TypeError:
                logger.warning(f"Found unhashable value type, skipping column {col}.")
        return dic

    def get_column_names(self, **kwargs: Any) -> Iterable[str]:
        """Get the column names as an iterable."""
        return list(self.data.columns)

    def get_column(self, col_name: str, **kwargs: Any) -> _Column:
        """Get a single column from dataset.

        Used in the `ColumnAverage` algorithm as well as to iterate over image columns
        for the purposes of schema generation.
        """
        return self.data[col_name]

    @abstractmethod
    def get_data(self, **kwargs: Any) -> Optional[pd.DataFrame]:
        """Implement this method to load and return dataset."""
        raise NotImplementedError

    def get_dtypes(self, **kwargs: Any) -> _Dtypes:
        """Get the columns and column types from dataset."""
        return self._get_data_dtypes(self.data)

    def __len__(self) -> int:
        """Get the number of rows in the dataset."""
        return len(self.data)

    @property
    def multi_table(self) -> bool:
        """This returns False if the DataSource does not subclass `MultiTableSource`.

        However, this property must be re-implemented in `MultiTableSource`, therefore
        it is not necessarily True if the DataSource inherits from `MultiTableSource`.
        """
        return False

    @property
    def iterable(self) -> bool:
        """This returns False if the DataSource does not subclass `IterableSource`.

        However, this property must be re-implemented in `IterableSource`, therefore it
        is not necessarily True if the DataSource inherits from `IterableSource`.
        """
        return False


@delegates()
class MultiTableSource(BaseSource, ABC):
    """Abstract base source that supports multiple tables.

    This class is used to define a data source that supports multiple tables. The
    datasources do not necessarily have multiple tables though.
    """

    @property
    @abstractmethod
    def multi_table(self) -> bool:
        """Implement this method to define whether the data source is multi-table.

        The datasource must inherit from `MultiTableSource` if this is True. However,
        the inverse is not necessarily True.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def table_names(self) -> List[str]:
        """Implement this to return a list of table names.

        If there is only one table, it should return a list with one element.
        """
        raise NotImplementedError

    @abstractmethod
    def _validate_table_name(self, table_name: str) -> None:
        """Validate the table name exists in the multi-table datasource.

        This method should raise a ValueError if the table_name is not valid.
        """
        raise NotImplementedError

    @abstractmethod
    def get_values(
        self, col_names: List[str], table_name: Optional[str] = None, **kwargs: Any
    ) -> Dict[str, Iterable[Any]]:
        """Implement this method to get distinct values from list of columns."""
        raise NotImplementedError

    @abstractmethod
    def get_column_names(
        self, table_name: Optional[str] = None, **kwargs: Any
    ) -> Iterable[str]:
        """Implement this method to get the column names as an iterable."""
        raise NotImplementedError

    @abstractmethod
    def get_column(
        self, col_name: str, table_name: Optional[str] = None, **kwargs: Any
    ) -> _Column:
        """Implement this method to get single column from dataset."""
        raise NotImplementedError

    @abstractmethod
    def get_data(
        self, table_name: Optional[str] = None, **kwargs: Any
    ) -> Optional[pd.DataFrame]:
        """Implement this method to loads and return dataset."""
        raise NotImplementedError

    @abstractmethod
    def get_dtypes(self, table_name: Optional[str] = None, **kwargs: Any) -> _Dtypes:
        """Implement this method to get the columns and column types from dataset."""
        raise NotImplementedError


@delegates()
class IterableSource(BaseSource, ABC):
    """Abstract base source that supports iterating over the data.

    This is used for streaming data in batches as opposed to loading the entire dataset
    into memory.

    Args:
        partition_size: The size of each partition when iterating over the data.
    """

    def __init__(
        self,
        partition_size: int = 100,
        **kwargs: Any,
    ) -> None:
        # TODO: [BIT-3486] Make partition size configurable?
        self.partition_size = partition_size
        super().__init__(**kwargs)

    @property
    @abstractmethod
    def iterable(self) -> bool:
        """Implement this method to define whether the data source is iterable.

        The datasource must inherit from `IterableSource` if this is True. However,
        the inverse is not necessarily True.
        """
        raise NotImplementedError

    def get_data(self, **kwargs: Any) -> Optional[pd.DataFrame]:
        """This method must return None if the data source is iterable."""
        if self.iterable:
            logger.warning(f"Datasource {self} is iterable; get_data() returns None")
            return None
        else:
            return super().get_data(**kwargs)

    @abstractmethod
    def yield_data(self, **kwargs: Any) -> Iterator[pd.DataFrame]:
        """Implement this method to yield dataframes."""
        raise NotImplementedError

    @property
    def data(self) -> pd.DataFrame:
        """A property containing the underlying dataframe if the data has been loaded.

        If the datasource is iterable, this will raise an exception.

        Raises:
            IterableDataSourceError: If the datasource is set to iterable.
            DataNotLoadedError: If the data has not been loaded yet.
        """
        if self.iterable:
            raise IterableDataSourceError(
                ".data property cannot be used when datasource is iterable."
            )
        else:
            return super().data

    @data.setter
    def data(self, _data: Optional[pd.DataFrame]) -> None:
        """Data property setter."""
        if self.iterable:
            raise IterableDataSourceError(
                ".data property cannot be used when datasource is iterable."
            )
        else:
            super()._data_setter(_data)

    def get_values(
        self, col_names: List[str], **kwargs: Any
    ) -> Dict[str, Iterable[Any]]:
        """Implement this method to get distinct values from list of columns."""
        if self.iterable:
            return self._get_values_iteratively(col_names, **kwargs)
        else:
            return self._get_values_noniteratively(col_names, **kwargs)

    def _get_values_iteratively(
        self, col_names: List[str], **kwargs: Any
    ) -> Dict[str, Iterable[Any]]:
        """Get values for iterable datasource."""
        values: Dict[str, Set[Any]] = defaultdict(set)
        cols_to_skip: Set[str] = set()

        for chunk in self.yield_data(**kwargs):
            for col in col_names:
                if col in cols_to_skip:
                    continue

                try:
                    values[col].update(chunk[col].unique())
                except TypeError:
                    logger.warning(
                        f"Found unhashable value type, skipping column {col}."
                    )
                    # Remove from `values` dict, if present, and add to skip list
                    values.pop(col, None)
                    cols_to_skip.add(col)

        return {k: list(v) for k, v in values.items()}

    def _get_values_noniteratively(
        self, col_names: List[str], **kwargs: Any
    ) -> Dict[str, Iterable[Any]]:
        """Get values for non-iterable datasource."""
        dic: Dict[str, Iterable[Any]] = {}

        for col in col_names:
            try:
                dic[col] = self.data[col].unique()
            except TypeError:
                logger.warning(f"Found unhashable value type, skipping column {col}.")
        return dic

    def get_column_names(self, **kwargs: Any) -> Iterable[str]:
        """Get the column names as an iterable."""
        if self.iterable:
            return self._get_column_names_iteratively(**kwargs)
        else:
            return self._get_column_names_noniteratively(**kwargs)

    def _get_column_names_iteratively(self, **kwargs: Any) -> Iterable[str]:
        """Get column names for iterable datasource."""
        # The dataframes should be the same throughout the yield_data iteration
        # so we should only need to get one of them.
        df_0: pd.DataFrame = next(self.yield_data(**kwargs))
        return list(df_0.columns)

    def _get_column_names_noniteratively(self, **kwargs: Any) -> Iterable[str]:
        """Get column names for non-iterable datasource."""
        return list(self.data.columns)

    def get_column(self, col_name: str, **kwargs: Any) -> _Column:
        """Get a single column from dataset.

        Used in the `ColumnAverage` algorithm as well as to iterate over image columns
        for the purposes of schema generation.
        """
        if self.iterable:
            return self._get_column_iteratively(col_name, **kwargs)
        else:
            return self._get_column_noniteratively(col_name, **kwargs)

    def _get_column_iteratively(self, col_name: str, **kwargs: Any) -> _Column:
        """Get column for iterable datasource."""

        def extend_series(s1: pd.Series, s2: pd.Series) -> pd.Series:
            return pd.concat([s1, s2])

        # We use a for-loop and per-chunk concat to avoid holding all the chunks
        # in memory together _and_ trying to create a concatenated one
        col: pd.Series = functools.reduce(
            extend_series,
            (chunk[col_name] for chunk in self.yield_data(**kwargs)),
        )
        return col

    def _get_column_noniteratively(self, col_name: str, **kwargs: Any) -> _Column:
        """Get column for non-iterable datasource."""
        return self.data[col_name]

    def get_dtypes(self, **kwargs: Any) -> _Dtypes:
        """Get the columns and column types from dataset.

        Note: iterable=True and iterable=False may return different dtypes for the
              columns, as with iterable=False we are able to infer pandas dtypes
              from the whole dataset in one go.
        """
        if self.iterable:
            return self._get_dtypes_iteratively(**kwargs)
        else:
            return self._get_dtypes_noniteratively(**kwargs)

    def _get_dtypes_iteratively(self, **kwargs: Any) -> _Dtypes:
        """Get dtypes for iterable datasource."""
        dtypes: _Dtypes = {}

        # We iterate through each chunk, finding the common type that best
        # expresses the dtype for a column from all the chunks seen so far
        for chunk in self.yield_data(**kwargs):
            chunk_dtypes: _Dtypes = self._get_data_dtypes(chunk)
            for k, dtype in chunk_dtypes.items():
                if k not in dtypes:
                    dtypes[k] = dtype
                else:
                    dtypes[k] = find_common_type([dtypes[k], dtype])

        return dtypes

    def _get_dtypes_noniteratively(self, **kwargs: Any) -> _Dtypes:
        """Get dtypes for non-iterable datasource."""
        return self._get_data_dtypes(self.data)

    def __len__(self) -> int:
        if self.iterable:
            return self._len_iteratively()
        else:
            return self._len_noniteratively()

    def _len_iteratively(self) -> int:
        """Get len for iterable datasource."""
        chunk_lens: Iterable[int] = map(len, self.yield_data())
        return sum(chunk_lens)

    def _len_noniteratively(self) -> int:
        """Get len for non-iterable datasource."""
        return len(self.data)


class MultiProcessingMixIn:
    """MixIn class for multiprocessing of `_get_data`."""

    skipped_files: Set[str]

    @abstractmethod
    def _get_data(
        self, file_names: Optional[List[str]] = None, **kwargs: Any
    ) -> pd.DataFrame:
        ...

    @staticmethod
    def _mp_configure_listener_logger(log_file_name: str) -> None:
        """Configure the logger for the listener process.

        Adds the same handlers as the main process logger to the listener process
        logger. This requires passing the name of the log file to use to the listener
        because otherwise it can't be found because it has a timestamp in the name.

        Args:
            log_file_name: The name of the log file to use.
        """
        logger = logging.getLogger()
        logger.addHandler(_get_bitfount_log_file_handler(log_file_name=log_file_name))
        logger.addHandler(_get_bitfount_console_handler())
        logger.propagate = False

    @classmethod
    def _mp_listener_process(cls, queue: Queue, log_file_name: str) -> None:
        """Process that listens for log messages from the worker processes.

        Whenever a log message is received, it is handled by the logger.

        Args:
            queue: The queue to listen on.
            log_file_name: The name of the log file to use.
        """
        cls._mp_configure_listener_logger(log_file_name)
        while True:
            try:
                record = queue.get()
                if record is None:  # Sentinel to tell the listener to quit
                    break
                logger.handle(record)
            except Exception:
                import traceback

                traceback.print_exc()

    @staticmethod
    def _mp_configure_worker_logger(queue: Queue) -> None:
        """Configure the logger for the worker processes.

        Adds a QueueHandler to the logger to send log messages to the listener process.

        Args:
            queue: The queue to send log messages to.
        """
        h = QueueHandler(queue)
        bf_logger = logging.getLogger("bitfount")
        bf_logger.setLevel(logging.DEBUG)
        plugins_logger = logging.getLogger("plugins")
        plugins_logger.setLevel(logging.DEBUG)
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.WARNING)
        for _logger in (bf_logger, plugins_logger, root_logger):
            _logger.handlers.clear()  # Clear existing handlers
            _logger.addHandler(h)
            _logger.propagate = False

    def _mp_worker_get_data_process(
        self,
        queue: Queue,
        file_names: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Tuple[pd.DataFrame, List[str]]:
        """Process that calls `_get_data` to load data.

        This is called by the main process to load data in parallel. This method
        configures the logger for the worker process and calls `_get_data`.

        Args:
            queue: The queue to send log messages to.
            file_names: The list of file names to load.
            kwargs: Keyword arguments to pass to `_get_data`.

        Returns:
            The loaded data as a dataframe and a list of skipped files. The skipped
            files are returned so that they can be added to the `skipped_files` set
            in the main process - otherwise this information would be lost when the
            worker process is terminated. The skipped files are returned as a list
            rather than a set because sets are not pickleable.
        """
        self._mp_configure_worker_logger(queue)
        data = self._get_data(file_names=file_names, **kwargs)
        return data, list(self.skipped_files)

    def _mp_get_data(self, file_names: List[str], **kwargs: Any) -> pd.DataFrame:
        """Call `_get_data` in parallel.

        This method sets up the multiprocessing queue and processes and calls
        `_get_data` in parallel. It also sets up the listener process to handle log
        messages from the worker processes.

        Args:
            file_names: The list of file names to load.
            kwargs: Keyword arguments to pass to `_get_data`.

        Returns:
            The loaded data as a dataframe.
        """
        from concurrent.futures import Future, ProcessPoolExecutor, as_completed
        from multiprocessing import Manager, Process

        # If there is more than one file, we use multiprocessing to load the data
        logger.info("Loading data in parallel using multiprocessing.")
        log_file_name: str = ""
        for handler in logging.getLogger("bitfount").handlers:
            if isinstance(handler, logging.FileHandler):
                # Already have a file handler, so return it
                log_file_name = Path(handler.baseFilename).stem
                break

        if not log_file_name:
            # If there is no file handler, then there is no need for this message
            # to be logged any higher than debug anyway
            logger.debug("No existing file handler found for logger.")

        try:
            log_queue = Manager().Queue(-1)
            log_listener = Process(
                target=self._mp_listener_process, args=(log_queue, log_file_name)
            )
            log_listener.start()

            # Ensure that the number of workers is at least 1 and at most equal to
            # MAX_NUM_MULTIPROCESSING_WORKERS. If the number of files is less than
            # MAX_NUM_MULTIPROCESSING_WORKERS, then we use the number of files as the
            # number of workers. Unless the number of machine cores is also less than
            # MAX_NUM_MULTIPROCESSING_WORKERS, in which case we use the lower of the
            # two.
            max_workers = min(
                max(1, len(file_names)),
                # Make sure we don't use all the available cores
                max(1, psutil.cpu_count(logical=False) - 1),
                MAX_NUM_MULTIPROCESSING_WORKERS,
            )
            logger.info(f"Multiprocessing max workers: {max_workers}")
            executor = ProcessPoolExecutor(max_workers=max_workers)
            futures: List[Future] = [
                executor.submit(
                    self._mp_worker_get_data_process, log_queue, [i], **kwargs
                )
                for i in file_names
            ]

            total_num_files = len(file_names)
            dfs: List[pd.DataFrame] = []
            # Wait for the results to come in one by one as they complete
            for i, future in enumerate(as_completed(futures)):
                # Signal file finished processing
                for hook in get_hooks(HookType.POD):
                    hook.on_file_process_end(
                        cast(FileSystemIterableSource, self),
                        file_num=i + 1,
                        total_num_files=total_num_files,
                    )
                data, skipped_files = future.result()
                self.skipped_files.update(set(cast(List[str], skipped_files)))
                dfs.append(cast(pd.DataFrame, data))

        finally:
            log_queue.put_nowait(None)  # Send sentinel to tell listener to quit
            # Wait for listener to quit. Must be done before terminating the process
            # to ensure all the log messages continue to get processed
            log_listener.join()
            # Terminate listener process
            log_listener.terminate()

            # Shutdown the executor. We don't wait for it to finish as we have already
            # waited for the results to come in one by one as they complete
            executor.shutdown(wait=False)

        if dfs:
            return pd.concat(dfs, axis=0, ignore_index=True)

        # If no data was loaded, return an empty dataframe as `pd.concat` will fail
        # if no dataframes are passed to it
        return pd.DataFrame()


@delegates()
class FileSystemIterableSource(IterableSource, MultiProcessingMixIn, ABC):
    """Abstract base source that supports iterating over file-based data.

    This is used for Iterable data sources that whose data is stored as files on disk.

    Args:
        path: Path to the directory which contains the data files. Subdirectories
            will be searched recursively.
        output_path: The path where to save intermediary output files. Defaults to
            'preprocessed/'.
        iterable: Whether the data source is iterable. This is used to determine
            whether the data source can be used in a streaming context during a task.
            Defaults to False.
        fast_load: Whether the data will be loaded in fast mode. This is used to
            determine whether the data will be iterated over during set up for schema
            generation and splitting (where necessary). Only relevant if `iterable` is
            True, otherwise it is ignored. Defaults to False.
        file_extension: File extension(s) of the data files. If None, all files
            will be searched. Can either be a single file extension or a list of
            file extensions. Case-insensitive. Defaults to None.
        strict: Whether File loading should be strictly done on files with the
            explicit file extension provided. If set to True will only load
            those files in the dataset. Otherwise, it will scan the given path
            for files of the same type as the provided file extension. Only
            relevant if `file_extension` is provided. Defaults to False.
        cache_images: Whether to cache images in the file system. Defaults to True.
            This is ignored if `fast_load` is True.
        file_creation_cutoff_date: The oldest possible date to consider for file
            creation. If None, all files will be considered. Defaults to None.
        file_modification_cutoff_date: The oldest possible date to consider for file
            modification. If None, all files will be considered. Defaults to None.
        min_file_size: The minimum file size in megabytes to consider. If None, all
            files will be considered. Defaults to None.
        max_file_size: The maximum file size in megabytes to consider. If None, all
            files will be considered. Defaults to None.
    """

    def __init__(
        self,
        path: Union[os.PathLike, str],
        output_path: Optional[Union[os.PathLike, str]] = None,
        iterable: bool = False,
        fast_load: bool = False,
        file_extension: Optional[_SingleOrMulti[str]] = None,
        strict: bool = False,
        cache_images: bool = True,
        file_creation_cutoff_date: Optional[Union[Date, DateTD]] = None,
        file_modification_cutoff_date: Optional[Union[Date, DateTD]] = None,
        min_file_size: Optional[float] = None,
        max_file_size: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.cache_images = cache_images if fast_load is False else False
        self._unsanitized_path = path
        self.out_path: Path
        if output_path is None:
            self.out_path = BITFOUNT_CACHE_DIR
        else:
            self.out_path = Path(output_path)
        logger.debug(f"File output path set to {self.out_path}")
        self.out_path.mkdir(exist_ok=True, parents=True)  # create if not exists

        self._iterable = iterable

        self.file_extension: Optional[List[str]] = None
        if file_extension:
            file_extension_: List[str] = (
                [file_extension]
                if isinstance(file_extension, str)
                else list(file_extension)
            )
            self.file_extension = [
                f".{fe}" if not fe.startswith(".") else fe for fe in file_extension_
            ]

        self.strict = strict if self.file_extension is not None else False

        # Create a datetime.date object from the provided creation cutoff date
        self.file_creation_cutoff_date: Optional[date] = None
        if file_creation_cutoff_date:
            if isinstance(file_creation_cutoff_date, Date):
                self.file_creation_cutoff_date = file_creation_cutoff_date.get_date()
            else:  # is typed dict
                self.file_creation_cutoff_date = Date(
                    **file_creation_cutoff_date
                ).get_date()

        # Create a datetime.date object from the provided modification cutoff date
        self.file_modification_cutoff_date: Optional[date] = None
        if file_modification_cutoff_date:
            if isinstance(file_modification_cutoff_date, Date):
                self.file_modification_cutoff_date = (
                    file_modification_cutoff_date.get_date()
                )
            else:  # is typed dict
                self.file_modification_cutoff_date = Date(
                    **file_modification_cutoff_date
                ).get_date()

        if (
            not self.file_creation_cutoff_date
            and not self.file_modification_cutoff_date
        ):
            logger.warning(
                "No file creation or modification cutoff date provided. All files in "
                "the directory will be considered which may impact performance."
            )

        # Set the min and max file sizes in megabytes
        self.min_file_size: Optional[float] = min_file_size
        self.max_file_size: Optional[float] = max_file_size

        if not self.min_file_size and not self.max_file_size:
            logger.warning(
                "No file size limits provided. All files in the directory will be "
                "considered which may impact performance."
            )

        # This is used to select a subset of file names by the data splitter rather than
        # every file that has been loaded or that is in the directory. In particular,
        # this is used to subset the files for batched execution of a task.
        self.selected_file_names_override: List[str] = []
        # This is used to filter the file names to only new records.
        # In particular, this is used only when pod database exists and task
        # is set with `run_on_new_data_only` flag.
        self.new_file_names_only_set: Union[Set[str], None] = None
        # A list of files that have previously been skipped either because of errors or
        # because they don't contain any image data and `images_only` is True. This
        # allows us to skip these files again more quickly if they are still present in
        # the directory.
        self.skipped_files: Set[str] = set()

        # A list of image column names, so we can keep track of them when
        # cache_images is False.
        self.image_columns: Set[str] = set()
        # Fast-load related attributes
        self.fast_load = fast_load
        self._sampled_data_priv: Optional[pd.DataFrame] = None

    ####################
    # Other Properties #
    ####################
    @property
    def iterable(self) -> bool:
        """Defines whether the data source is iterable.

        This is defined by the user when instantiating the class.
        """
        return self._iterable

    @property
    def path(self) -> Path:
        """Resolved absolute path to data.

        Provides a consistent version of the path provided by the user
        which should work throughout regardless of operating system
        and of directory structure.
        """
        return Path(self._unsanitized_path).absolute().resolve()

    @property
    def _sampled_data(self) -> pd.DataFrame:
        """Subset of data, as loaded by fast load."""
        if self._sampled_data_priv is None:
            self._fast_load_data()
        # We can make this cast as the above `is None` check causes data to be loaded
        return cast(pd.DataFrame, self._sampled_data_priv)

    @_sampled_data.setter
    def _sampled_data(self, data: pd.DataFrame) -> None:
        """Setter for sampled data."""
        self._sampled_data_priv = data

    @property
    def stale(self) -> bool:
        """Whether the data source is stale.

        This is defined by whether the data is loaded and the number of files matches
        the number of rows in the dataframe.
        """
        # Iterable data is always stale, as we hold none of it in memory longer
        # than it is needed
        if self.iterable:
            return True
        elif self._data_is_loaded and len(self.data) == len(self.file_names):
            return False
        else:
            return True

    ####################
    # File Properties #
    ####################
    @cached_property
    def file_names(self) -> List[str]:
        """Returns a cached list of file names in the directory."""
        # TODO: [BIT-3486] This may also need to be made iterable somehow, in case
        #       the file list is too large
        if not os.path.exists(self.path):
            logger.warning(
                "The specified path for the datasource was not found. "
                "No files can be loaded."
            )
            return []
        original_files = [x for x in self.path.rglob("*") if x.is_file()]
        files = [x for x in original_files if str(x) not in self.skipped_files]
        # We aren't assuming that all the files in `self.skipped_files`
        # are still present in the directory, so we have to calculate
        # the number of skipped files based on the difference between
        # the original files and the files that have been skipped.
        num_skipped_files = len(original_files) - len(files)
        if num_skipped_files > 0:
            logger.info(f"Skipping {num_skipped_files} files.")

        if self.strict or not self.file_extension:
            if self.file_extension:
                lower_case_file_extensions = [x.lower() for x in self.file_extension]
                files = [
                    x for x in files if x.suffix.lower() in lower_case_file_extensions
                ]
                logger.info(
                    f"Found {len(files)} files with the explicit extensions "
                    f"{self.file_extension}."
                )
            else:
                logger.info(f"Found {len(files)} files.")

            # After filtering by file extension, we can filter by date and size
            return self._filter_files_by_size(
                self._filter_files_by_date([str(x.resolve()) for x in files])
            )

        # Only called if self.file_extension is specified and self.strict is False
        return self._filter_files_by_size(
            self._filter_files_by_date(
                self._scan_files_for_extension(files, self.file_extension)
            )
        )

    def clear_file_names_cache(self) -> None:
        """Clears the list of selected file names.

        This allows the datasource to pick up any new files that have been added to the
        directory since the last time it was cached.
        """
        # This is the specified way to clear the cache on a cached_property
        # https://docs.python.org/3/library/functools.html#functools.cached_property
        try:
            del self.file_names
        except AttributeError:
            # If the file_names property hasn't been accessed yet, it will raise an
            # AttributeError. We can safely ignore this.
            pass

    @property
    def selected_file_names(self) -> List[str]:
        """Returns a list of selected file names.

        Selected file names are affected by the
        `selected_file_names_override` and `new_file_names_only` attributes.
        """
        filenames = []
        try:
            if self.selected_file_names_override:
                filenames = self.selected_file_names_override
            elif len(self.data) > 0:
                filenames = list(self.data[ORIGINAL_FILENAME_METADATA_COLUMN])
        except (DataNotLoadedError, IterableDataSourceError):
            filenames = self.file_names

        # If self.new_file_names_only_set is set to None (default), we don't want
        # apply any filter.
        # Otherwise, if empty set or a set that has at least one record,
        # filter filenames to match the new records only as set by the
        # worker.
        if self.new_file_names_only_set is not None:
            filenames = [
                filename
                for filename in filenames
                if filename in self.new_file_names_only_set
            ]
            logger.debug(f"Filtered {len(filenames)} files as new entries.")

        return filenames

    @staticmethod
    def _scan_files_for_extension(
        files: List[Path], file_extension: List[str]
    ) -> List[str]:
        """Scans files for the provided file extension.

        Looks for files with same defined or guessed extension as the provided
        file extension.

        Args:
            files: A list of files to scan.

        Returns:
            A list of files with a matching extension.
        """

        # Otherwise, restrict files based on specified file extension.
        ignored_file_types = set()
        number_of_ignored_files = 0
        matched_files: List[Path] = []

        for file in files:
            # Order: file extension, guessed extension
            file_type = file.suffix or f".{guess_extension(file)}"

            # If guessing the extension failed the result is ".None"
            if file_type == ".None":
                logger.warning(
                    f"Could not determine file type of '{file.resolve()}'. Ignoring..."
                )
            elif file_type.lower() not in [x.lower() for x in file_extension]:
                ignored_file_types.add(file_type)
                number_of_ignored_files += 1
            else:
                matched_files.append(file)

        logger.info(
            f"Found {len(matched_files)} files that match file types "
            f"{file_extension}."
        )
        if ignored_file_types:
            logger.info(
                f"Ignoring {number_of_ignored_files} files with file types "
                f"{ignored_file_types}."
            )

        # Fix for shuffling so that data is mapped correctly
        matched_files.sort(key=lambda x: hash(x))
        return [str(x.resolve()) for x in matched_files]

    @staticmethod
    def _get_date_from_date_components(
        cutoff_type: Literal["creation", "modification"],
        year: Optional[int],
        month: Optional[int],
        day: Optional[int],
    ) -> Optional[date]:
        """Get a date from the provided year, month and day.

        Args:
            cutoff_type: The type of cutoff date to create. Either "creation" or
                "modification". This is used for logging purposes.
            year: The year.
            month: The month.
            day: The day.

        Returns:
            A date object if at least a year is provided, otherwise None.
        """
        if year:
            if month:
                if day:
                    cutoff_datetime = datetime(year, month, day)
                else:
                    cutoff_datetime = datetime(year, month, 1)
            else:
                cutoff_datetime = datetime(year, 1, 1)

            return cutoff_datetime.date()

        elif any((month, day)):
            logger.warning(
                f"Ignoring {cutoff_type} cutoff month and day as no year was provided."
            )

        return None

    def get_file_creation_date(self, path: str) -> date:
        """Get the creation date of a file with consideration for different OSs.

        :::caution

        It is not possible to get the creation date of a file on Linux. This method
        will return the last modification date instead. This will impact filtering of
        files by date.

        :::

        Args:
            path: The path to the file.

        Returns:
            The creation date of the file.
        """
        if sys.platform == "win32":
            timestamp = os.path.getctime(path)
        else:
            stat = os.stat(path)
            if sys.platform == "darwin":
                timestamp = stat.st_birthtime
            else:
                # We're probably on Linux. No easy way to get creation dates here,
                # so we'll settle for when its content was last modified.
                timestamp = stat.st_mtime

        return datetime.fromtimestamp(timestamp).date()

    def get_file_last_modification_date(self, path: str) -> date:
        """Get the last modification date of a file.

        Args:
            path: The path to the file.

        Returns:
            The last modification date of the file.
        """
        stat = os.stat(path)
        timestamp = stat.st_mtime
        return datetime.fromtimestamp(timestamp).date()

    def _filter_files_by_date(self, file_names: List[str]) -> List[str]:
        """Filter provided files by the creation/modification date cutoffs.

        Args:
            file_names: A list of file names to filter.

        Returns:
            A list of file names that were created/modified after the relevant
            cutoff dates.
        """
        if (
            not self.file_creation_cutoff_date
            and not self.file_modification_cutoff_date
        ):
            return file_names

        filtered_files = []
        for file in file_names:
            try:
                meets_date_cutoff_criteria = True
                if self.file_creation_cutoff_date:
                    file_creation_date = self.get_file_creation_date(file)
                    if file_creation_date < self.file_creation_cutoff_date:
                        meets_date_cutoff_criteria = False

                if self.file_modification_cutoff_date and meets_date_cutoff_criteria:
                    file_modification_date = self.get_file_last_modification_date(file)
                    if file_modification_date < self.file_modification_cutoff_date:
                        meets_date_cutoff_criteria = False

                if meets_date_cutoff_criteria:
                    filtered_files.append(file)
                else:
                    self.skipped_files.add(file)

            except Exception:
                logger.warning(
                    f"Could not determine creation/modification date of '{file}'. "
                    "Ignoring..."
                )
                self.skipped_files.add(file)

        return filtered_files

    def _filter_files_by_size(self, file_names: List[str]) -> List[str]:
        """Filter provided files by the minimum/maximum file size limits.

        Args:
            file_names: A list of file names to filter.

        Returns:
            A list of file names that are within the size limits.
        """
        if not self.min_file_size and not self.max_file_size:
            return file_names

        filtered_files = []
        for file in file_names:
            try:
                file_size = os.path.getsize(file)
                meets_size_criteria = True
                if self.min_file_size:
                    if file_size < (self.min_file_size * NUM_BYTES_IN_A_MEGABYTE):
                        meets_size_criteria = False

                if self.max_file_size and meets_size_criteria:
                    if file_size > (self.max_file_size * NUM_BYTES_IN_A_MEGABYTE):
                        meets_size_criteria = False

                if meets_size_criteria:
                    filtered_files.append(file)
                else:
                    self.skipped_files.add(file)
            except Exception:
                logger.warning(f"Could not determine size of '{file}'. Ignoring...")
                self.skipped_files.add(file)

        return filtered_files

    ##################
    # Data Retrieval #
    ##################
    def load_data(self, **kwargs: Any) -> None:
        """Load the data for the datasource.

        Args:
            **kwargs: Keyword arguments to be passed to underlying functions.

        Raises:
            TypeError: If data format is not supported.
        """
        if self.iterable:
            # TODO: [BIT-3486] Add capability to _load_ iterably, even if not
            #       _processing_ iterably
            logger.warning("Data cannot be loaded when using iterable=True")
            return

        # If the data is up-to-date, no need to reload
        if not self.stale:
            return

        # If a task isn't running, we can try fast load if allowed
        if self.fast_load and not self.is_task_running:
            if self._data_is_loaded:
                # If the data is already loaded, we don't need to load it again.
                pass
            else:
                self._fast_load_data(**kwargs)
            # Either way, we can return early
            return

        # If a task is running (or fast load is not enabled) we need to defer to
        # normal loading
        # TODO: [BIT-3486] Add capability to _load_ iterably, even if not
        #       _processing_ iterably
        # if self.iterable:
        #     self._load_data_iteratively(**kwargs)

        # We cannot rely on super().load_data() here because we need to account
        # for additional files being added, and the check of `_data_is_loaded`
        # precludes that
        if (data := self.get_data(**kwargs)) is not None:
            self.data = data
        else:
            logger.error("Attempted to load non-iterable data but got get_data()=None")

    def _load_data_iteratively(self, **kwargs: Any) -> None:
        """Load data iteratively using `yield_data`.

        Data will still be stored on the .data property of the class.
        """
        dfs = []
        for df in self.yield_data(**kwargs):
            dfs.append(df)
        self.data = pd.concat(dfs, axis=0, ignore_index=True)

    def _fast_load_data(self, **kwargs: Any) -> None:
        """Load the data in fast mode.

        Loads a small random subset of the data to speed up the process of schema
        generation. The number of files loaded is determined by the number of files
        in the directory and the variability of the data. The more unique fields that
        get discovered with each file, the more files will be loaded.

        This data sample is saved onto the `_sampled_data` attribute of the class.
        """
        # We don't want to load too many or too few files, so we aim for a small
        # percentage of the total number of files, but with a minimum and maximum
        # number of files which overrides the percentage if the number of files falls
        # outside of the range.
        minimum_number_of_files_without_new_fields = np.clip(
            FAST_LOAD_NUMBER_OF_FILES_PERCENTAGE * len(self.file_names),
            FAST_LOAD_MINIMUM_NUMBER_OF_FILES_WITHOUT_NEW_FIELDS,
            FAST_LOAD_MAXIMUM_NUMBER_OF_FILES_WITHOUT_NEW_FIELDS,
        )
        minimum_number_of_files_without_new_fields = int(
            min(minimum_number_of_files_without_new_fields, len(self.file_names))
        )
        logger.debug(
            "Minimum number of files without new fields is "
            f"{minimum_number_of_files_without_new_fields}"
        )
        sampled_file_names = random.sample(
            self.file_names,
            # Ensure we don't attempt to sample more files than there are in the
            # directory.
            min(len(self.file_names), FAST_LOAD_MAXIMUM_NUMBER_OF_FILES_TO_LOAD),
        )
        number_of_files_without_new_fields = 0
        num_files_processed = 0
        unique_fields: Set[str] = set()
        dfs: List[pd.DataFrame] = []
        for file in sampled_file_names:
            df = self._get_data(file_names=[file], **kwargs)
            if len(set(df.columns).difference(unique_fields)) == 0:
                number_of_files_without_new_fields += 1
            else:
                number_of_files_without_new_fields = 0

            unique_fields.update(df.columns)
            dfs.append(df)
            num_files_processed += 1
            if (
                number_of_files_without_new_fields
                >= minimum_number_of_files_without_new_fields
            ):
                break

        logger.info(f"Loaded {num_files_processed} files using fast load.")
        if (
            number_of_files_without_new_fields
            < minimum_number_of_files_without_new_fields
        ) and len(sampled_file_names) < len(self.file_names):
            logger.warning(
                "Schema generation may be inaccurate. "
                f"Loaded {num_files_processed} files "
                f"but didn't reach {minimum_number_of_files_without_new_fields} "
                "consecutive files without finding new fields."
            )

        # Save onto _sampled_data, not main `.data`
        self._sampled_data = pd.concat(dfs, axis=0, ignore_index=True)

    def get_data(
        self, file_names: Optional[List[str]] = None, **kwargs: Any
    ) -> Optional[pd.DataFrame]:
        """Returns data if the datasource is not iterable, otherwise None.

        We don't reload the data if it has already been loaded. We are assuming that
        files are only added, not removed, meaning we can rely on simply matching the
        number of files detected with the length of the dataframe to ascertain whether
        the data has already been loaded.
        """
        if self.iterable:
            logger.warning("Data cannot be retrieved when using iterable=True")
            return None

        if not file_names and not self.stale:
            return self.data

        file_names = file_names or self.file_names

        if len(file_names) == 0:
            logger.warning("No files found to return data from.")
            return None

        for hook in get_hooks(HookType.POD):
            # Signal file processing start
            hook.on_file_process_start(
                self, file_num=0, total_num_files=len(file_names)
            )

        if len(file_names) == 1:
            result = self._get_data(file_names=file_names, **kwargs)
            for hook in get_hooks(HookType.POD):
                hook.on_file_process_end(self, file_num=1, total_num_files=1)

            return result

        # TODO: [BIT-3597] Remove this feature flag and the corresponding
        # `else` block.
        if os.environ.get("BITFOUNT_FILE_MULTIPROCESSING_ENABLED"):
            return self._mp_get_data(file_names, **kwargs)
        else:
            dfs = []
            for idx, file_name in enumerate(file_names):
                dfs.append(self._get_data([file_name], **kwargs))
                for hook in get_hooks(HookType.POD):
                    hook.on_file_process_end(
                        self,
                        file_num=idx + 1,
                        total_num_files=len(file_names),
                    )

            return pd.concat(dfs, axis=0, ignore_index=True) if dfs else pd.DataFrame()

    @abstractmethod
    def _get_data(
        self,
        file_names: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Implement to return data corresponding to the provided file names.

        This method is called under the hood by `get_data` and `yield_data`. This
        method must return a dataframe with the columns `_original_filename` and
        `_last_modified` containing the original file name of each row, and the
        timestamp when the file was last modified in ISO 8601 format, respectively.

        Args:
            file_names: List of file names to load. If None, all files should be
                loaded.

        Returns:
            A dataframe containing the data.
        """
        raise NotImplementedError

    def yield_data(
        self, file_names: Optional[List[str]] = None, **kwargs: Any
    ) -> Iterator[pd.DataFrame]:
        """Yields data in batches from files that match the given file names.

        Args:
            file_names: An optional list of file names to use for yielding data.
                Otherwise, all files that have already been found will be used.
                `file_names` is always provided when this method is called from the
                Dataset as part of a task.

        Raises:
            ValueError: If no file names provided and no files have been found.
        """
        if not file_names and not self.file_names:
            logger.warning("No files found to yield data from.")
            # if there are no files, log a warning, and yield an empty dataframe
            yield pd.DataFrame()
            return

        file_names_: List[str] = file_names or self.file_names

        for idx, file_names_partition in enumerate(
            self.partition(file_names_, self.partition_size)
        ):
            try:
                file_names_partition = cast(List[str], file_names_partition)
                logger.debug(f"Yielding partition {idx} from {self}")
                # TODO: [BIT-3597] Remove this feature flag and the corresponding
                # `else` block.
                if os.environ.get("BITFOUNT_FILE_MULTIPROCESSING_ENABLED"):
                    yield self._mp_get_data(file_names_partition, **kwargs)
                else:
                    yield self._get_data(file_names_partition, **kwargs)
                    file_num = idx * self.partition_size + len(file_names_partition)
                    for hook in get_hooks(HookType.POD):
                        hook.on_file_process_end(
                            self,
                            file_num=file_num,
                            total_num_files=len(file_names_),
                        )
            finally:
                # Delete the files after they have been processed and used
                try:
                    self._cleanup(file_names_partition)
                except Exception as e:
                    logger.error(
                        f"Error whilst trying to cleanup files"
                        f" from partition {idx}: {e}"
                    )

    def partition(self, iterable: Sequence, partition_size: int = 1) -> Iterable:
        """Takes an iterable and yields partitions of size `partition_size`.

        The final partition may be less than size `partition_size` due to the variable
        length of the iterable.
        """
        for hook in get_hooks(HookType.POD):
            # Signal files partition
            hook.on_files_partition(
                self, total_num_files=len(iterable), batch_size=partition_size
            )

        len_ = len(iterable)
        for partition_start_idx in range(0, len_, partition_size):
            yield iterable[
                partition_start_idx : min(partition_start_idx + partition_size, len_)
            ]

    def _recreate_file_structure(self, file_path: str, exist_ok: bool) -> Path:
        """Recreates the file structure in the output directory.

        This is used to ensure that the output directory has the same structure as the
        input directory. This is useful for when the input data is partitioned into
        subdirectories.

        Args:
            file_path: The file name to recreate the structure for.
            exist_ok: Whether to raise an error if the directory already exists.

        Returns:
            The path to the recreated file structure.

        Raises:
            FileExistsError: If the subdir already exists in the output directory and
                `exist_ok` is False.
        """
        path = Path(file_path)
        file_id = path.stem + FILE_SYSTEM_ITERABLE_IMAGE_CACHE_SUFFIX
        parent_path = path.parent.absolute()
        # Relative path gets the path of the original file relative to the specified
        # input path. This relative path is then used to recreate the file structure
        # in the output directory with the original filename being used as a
        # subdirectory instead containing any relevant extracted files.
        relative_path = parent_path.relative_to(self.path)
        save_prefix = self.out_path / relative_path / file_id
        save_prefix.mkdir(parents=True, exist_ok=exist_ok)
        return save_prefix

    def _cleanup(self, file_names: List[str]) -> None:
        """Remove intermediate files creating during yielding of partitions.

        Intended to be called by `yield_data` every partition.
        """
        for file_name in file_names:
            save_dir = self._recreate_file_structure(file_name, exist_ok=True)
            shutil.rmtree(save_dir)

    ########################
    # Dataframe Processing #
    ########################
    def get_column_names(self, **kwargs: Any) -> Iterable[str]:
        """Get the column names as an iterable."""
        if self.fast_load:
            return self._get_column_names_fast_load(**kwargs)
        else:
            return super().get_column_names(**kwargs)

    def _get_column_names_noniteratively(self, **kwargs: Any) -> Iterable[str]:
        """Get column names for non-iterable datasource."""
        if self.stale:
            self.load_data(**kwargs)

        return list(self.data.columns)

    def _get_column_names_fast_load(self, **kwargs: Any) -> Iterable[str]:
        """Get column names for fast-load datasource."""
        return list(self._sampled_data.columns)

    def get_column(self, col_name: str, **kwargs: Any) -> Union[np.ndarray, pd.Series]:
        """Loads and returns single column from the dataset.

        Args:
            col_name: The name of the column which should be loaded.
            **kwargs: Additional keyword arguments to pass to the `load_data` method
                if the data is stale.

        Returns:
            The column request as a series.
        """
        if self.fast_load and not self.is_task_running:
            return self._get_column_fast_load(col_name, **kwargs)
        else:
            return super().get_column(col_name, **kwargs)

    def _get_column_noniteratively(self, col_name: str, **kwargs: Any) -> _Column:
        """Get column non-iteratively, loading data if it is stale."""
        if self.stale:
            self.load_data(**kwargs)

        return self.data[col_name]

    def _get_column_fast_load(self, col_name: str, **kwargs: Any) -> _Column:
        """Get column for fast-load datasource."""
        return self._sampled_data[col_name]

    def get_dtypes(self, **kwargs: Any) -> _Dtypes:
        """Loads and returns the column names and types of the dataframe.

        If `fast_load` is set to True and the data is stale, only the first file will
        be loaded to get the column names and types. Otherwise, all files will be
        loaded. We only perform this optimisation if the data is stale because if it's
        not, it's faster to just return the dtypes of the already loaded data.

        Args:
            **kwargs: Additional keyword arguments to pass to the `load_data` method
                if the data is stale.

        Returns:
            A mapping from column names to column types.
        """
        if self.fast_load:
            if self.stale:
                data = self._get_data(file_names=[self.file_names[0]], **kwargs)
                return self._get_data_dtypes(data)
            else:
                return self._get_data_dtypes(self._sampled_data)
        else:
            return super().get_dtypes(**kwargs)

    def _get_dtypes_noniteratively(self, **kwargs: Any) -> _Dtypes:
        """Get dtypes non-iteratively, loading data if it is stale."""
        if self.stale:
            self.load_data(**kwargs)

        return self._get_data_dtypes(self.data)

    def get_values(
        self, col_names: List[str], **kwargs: Any
    ) -> Dict[str, Iterable[Any]]:
        """Get distinct values from columns in the dataset.

        Args:
            col_names: The list of the columns whose distinct values should be
                returned.
            **kwargs: Additional keyword arguments to pass to the `load_data` method
                if the data is stale.

        Returns:
            The distinct values of the requested column as a mapping from col name to
            a series of distinct values.
        """
        if self.fast_load and not self.is_task_running:
            return self._get_values_fast_load(col_names, **kwargs)
        else:
            return super().get_values(col_names, **kwargs)

    def _get_values_noniteratively(
        self, col_names: List[str], **kwargs: Any
    ) -> Dict[str, Iterable[Any]]:
        """Get values non-iteratively, loading data if it is stale."""
        if self.stale:
            self.load_data(**kwargs)
        return self._get_values_from_dataframe(self.data, col_names, **kwargs)

    def _get_values_fast_load(
        self, col_names: List[str], **kwargs: Any
    ) -> Dict[str, Iterable[Any]]:
        """Get column values for fast-load datasource."""
        return self._get_values_from_dataframe(self._sampled_data, col_names, **kwargs)

    @staticmethod
    def _get_values_from_dataframe(
        data: pd.DataFrame, col_names: List[str], **kwargs: Any
    ) -> Dict[str, Iterable[Any]]:
        """Helper method to get values from a dataframe.

        Handles non-hashable elements.
        """
        dic: Dict[str, Iterable[Any]] = {}
        for col in col_names:
            try:
                dic[col] = data[col].unique()
            except TypeError:
                logger.warning(f"Found unhashable value type, skipping column {col}.")
        return dic

    def __len__(self) -> int:
        return len(self.selected_file_names)


@delegates()
class FileSystemIterableSourceInferrable(FileSystemIterableSource, ABC):
    """Abstract base source that supports iterating over file-based data.

    This is used for Iterable data sources that whose data is stored as files on disk.

    Args:
        path: Path to the directory which contains the data files. Subdirectories
            will be searched recursively.
        infer_class_labels_from_filepaths: Whether class labels should be
            added to the data based on the filepath of the files.
            Defaults to the first directory within `self.path`,
            but can go a level deeper if the datasplitter is provided
            with `infer_data_split_labels` set to true
        data_cache: A DataPersister instance to use if data caching is desired.
    """

    _first_directory_in_path: Final[str] = "_first_directory"
    _second_directory_in_path: Final[str] = "_second_directory"
    _unused_directory_in_path: Final[str] = "_unused_path_segment"

    def __init__(
        self,
        path: Union[os.PathLike, str],
        infer_class_labels_from_filepaths: bool = False,
        data_cache: Optional[DataPersister] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(path=path, **kwargs)
        self.infer_class_labels_from_filepaths = infer_class_labels_from_filepaths
        self.data_cache = data_cache

    def _get_data(
        self,
        file_names: Optional[List[str]] = None,
        use_cache: bool = True,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Returns data corresponding to the provided file names.

        Args:
            file_names: List of file names to load. If None, all files should be
                loaded.
            use_cache: Whether the cache should be used to retrieve data for these
                files. Note that cached data may have some elements, particularly
                image-related fields such as image data or file paths, replaced
                with placeholder values when stored in the cache.

                If data_cache is set on the instance, data will be _set_ in the
                cache, regardless of this argument.

        Returns:
            A dataframe containing the data.
        """
        if file_names:
            full_data = False
        else:
            file_names = self.file_names
            # Check if data is stale
            full_data = not self.stale

        processed_data_list: List[Dict[str, Any]] = []
        cached_data_list: List[pd.DataFrame] = []
        num_files_loaded: int = 0
        for filename in file_names:
            # Try to retrieve data from the cache if present.
            cached_data: Optional[pd.DataFrame] = None
            if self.data_cache and use_cache:
                # TODO: [BIT-3633] Ensure this works in the multiprocessing context
                cached_data = self.data_cache.get(filename)

            # If data was not in the cache (or was invalid) we will need to process
            # the file
            if cached_data is None:
                logger.info(f"Processing file {filename}...")
                processed_data = self._process_file(filename, full_data, **kwargs)

                if processed_data:
                    num_files_loaded += 1
                    # File has not been skipped and is not empty,
                    # so we can add some metadata
                    # columns and append it to the list of data points.
                    for row in processed_data:
                        processed_data_with_metadata = self._add_metadata_to_data(
                            row, filename
                        )
                        processed_data_list.append(processed_data_with_metadata)
            # Data stored in the cache will already be in the form that is output
            # post-`_process_dataset()` so we can simply skip processing and append
            # it to a separate list (to be joined after all processing is done)
            else:
                logger.info(f"Retrieved cached data for {filename}...")
                cached_data_list.append(cached_data)

        if num_files_loaded == 0 and len(file_names) == 1:
            logger.warning("File could not be loaded.")
        elif num_files_loaded == 0 and len(file_names) > 1:
            logger.warning("No files could be loaded.")
        # We don't want to log when we're just loading a single file because this is
        # not a meaningful log message as sometimes we iterate through all the files
        # one by one calling this method.
        elif num_files_loaded > 1 and len(file_names) > 1:
            if num_files_loaded < len(file_names):
                logger.warning(
                    f"{num_files_loaded} files loaded successfully out of"
                    f" {len(file_names)} files."
                )
            else:
                logger.info(f"{num_files_loaded} files loaded successfully.")
        if len(cached_data_list) > 1:
            logger.info(f"{len(cached_data_list)} file(s) loaded from cache.")

        # Create the (processed items) dataframe
        df = pd.DataFrame.from_records(processed_data_list)

        # Perform any subclass defined processing of the dataframe
        df = self._process_dataset(df, **kwargs)

        # Infer the data split and class labels if necessary
        df = self._infer_data_split_and_class_labels(df, **kwargs)

        # Add metadata columns if they were not added (e.g. if no files where processed)
        # This is because we want to ensure that the metadata columns are always present
        # in the dataframe as they are relied upon downstream even if they are empty.
        for col in FILE_SYSTEM_ITERABLE_METADATA_COLUMNS:
            if col not in df.columns:
                df[col] = None

        # Save any new processed data to the cache
        if self.data_cache and not df.empty:
            # We need to avoid caching anything that cannot/should not be placed
            # in the cache, such as image data or image filepaths that won't be
            # relevant after this pass
            try:
                cacheable_df = self.data_cache.prep_data_for_caching(
                    df, image_cols=self.image_columns
                )
                # TODO: [BIT-3633] Ensure this works in the multiprocessing context
                self.data_cache.bulk_set(cacheable_df)
            except Exception as e:
                logger.warning(
                    f"Error whilst attempting to bulk set new cache entries: {e}"
                )

        # Combine newly processed data with the data retrieved from the cache (which
        # was already in the format needed post-`_process_dataset()`)
        df = pd.concat(
            [df, *cached_data_list], axis="index", join="outer", ignore_index=True
        )

        if self._data_is_loaded and full_data:
            # If the data is already loaded, and we want all the data, we append the new
            # data to the existing dataframe.
            return pd.concat([self.data, df], axis=0, ignore_index=True)

        return df

    def _infer_data_split_and_class_labels(
        self, df: pd.DataFrame, **kwargs: Any
    ) -> pd.DataFrame:
        """Infers the data split and class labels from the file paths.

        Args:
            df: The dataframe to infer the data split and class labels for.

        Returns:
            The dataframe with the data split and class labels inferred.
        """
        # We now can infer the various labels of the data from the folder structure
        # if needed.
        #
        # The folder structure may provide labels for the data split (i.e. train,
        # test, validation), the class labels for the data, or both.
        infer_data_split_column_name: Union[str, Literal[False]] = (
            self.data_splitter.column_name
            if isinstance(self.data_splitter, SplitterDefinedInData)
            and self.data_splitter.infer_data_split_labels
            else False
        )
        unique_first_directory_column_values: List[str] = []
        unique_second_directory_column_values: List[str] = []

        if self.infer_class_labels_from_filepaths or infer_data_split_column_name:
            # We need to extract unique values from the first and second directories
            # so we can differentiate between the data split and the class label
            # directories.
            first_directory_col_in_df: bool = (
                self._first_directory_in_path in df.columns
            )
            if first_directory_col_in_df:
                unique_first_directory_column_values = (
                    df[self._first_directory_in_path].unique().tolist()
                )

            second_directory_col_in_df: bool = (
                self._second_directory_in_path in df.columns
            )
            if second_directory_col_in_df:
                unique_second_directory_column_values = (
                    df[self._second_directory_in_path].unique().tolist()
                )

            inferred_class_label_column_name: str = (
                BITFOUNT_INFERRED_LABEL_COLUMN
                if self.infer_class_labels_from_filepaths
                else self._unused_directory_in_path
            )

            if infer_data_split_column_name:
                # infer_data_split_column_name will *only* be
                # truthy for SplitterDefinedInData
                self.data_splitter = cast(SplitterDefinedInData, self.data_splitter)

                # We extract the split labels from the data splitter for
                # SplitterDefinedInData (note they are lowercased)
                datasplitter_labels = [
                    self.data_splitter.training_set_label.lower(),
                    self.data_splitter.validation_set_label.lower(),
                    self.data_splitter.test_set_label.lower(),
                ]

                # We then identify which column is the data split labels. We then
                # mark the other column as the inferred class labels.
                if unique_first_directory_column_values and set(
                    i.lower() for i in unique_first_directory_column_values
                ).issubset(datasplitter_labels):
                    logger.info(
                        f"`{self._first_directory_in_path}` column contains"
                        f" data split labels."
                        " Inferring class labels from second directory."
                    )
                    df = df.rename(
                        columns={
                            self._first_directory_in_path: infer_data_split_column_name,  # noqa: B950
                            self._second_directory_in_path: inferred_class_label_column_name,  # noqa: B950
                        },
                        # "ignore" as we may not have the second directory/class labels
                        errors="ignore",
                    )
                elif unique_second_directory_column_values and set(
                    i.lower() for i in unique_second_directory_column_values
                ).issubset(datasplitter_labels):
                    logger.info(
                        f"`{self._second_directory_in_path}` column contains"
                        f" data split labels."
                        " Inferring class labels from first directory."
                    )
                    df = df.rename(
                        columns={
                            self._first_directory_in_path: inferred_class_label_column_name,  # noqa: B950
                            self._second_directory_in_path: infer_data_split_column_name,  # noqa: B950
                        },
                        # "raise" as if we have the second directory we _must_ have
                        # the first
                        errors="raise",
                    )
                else:
                    # If we reach here, either the appropriate columns aren't in
                    # the dataframe or the columns don't contain the expected values.
                    #
                    # Either way, we cannot proceed with the requested label inference.
                    datasplitter_labels_str: str = ", ".join(datasplitter_labels)
                    logger.debug(
                        f"Neither directory column seemed to contain"
                        f" datasplitter labels ({datasplitter_labels_str}):"
                        f" {first_directory_col_in_df=},"
                        f" {unique_first_directory_column_values=},"
                        f" {second_directory_col_in_df=},"
                        f" {unique_second_directory_column_values=}"
                    )
                    raise ValueError(
                        f"Neither the '{self._first_directory_in_path}' column"
                        f" nor the '{self._second_directory_in_path}' column"
                        f" seem to contain only datasplit labels"
                        f" ({datasplitter_labels_str}),"
                        f" or are not present;"
                        f" unable to infer datasplits."
                    )

                # Finally, we convert the datasplitter labels (i.e. train, test,
                # validation) to match the case expected by the datasplitter.
                #
                # This is needed as we perform a case-insensitive matching above
                # (see the `.lower()` usages), but the datasplitter is very much
                # case-sensitive.
                #
                # We convert all the labels to lowercase, then replace them with
                # the actual version of the label.
                df[infer_data_split_column_name] = df[
                    infer_data_split_column_name
                ].str.lower()
                df[infer_data_split_column_name].replace(
                    {
                        label.lower(): label
                        for label in (
                            self.data_splitter.training_set_label,
                            self.data_splitter.test_set_label,
                            self.data_splitter.validation_set_label,
                        )
                    },
                    inplace=True,
                )
            else:  # self.infer_class_labels_from_filepaths is True
                # We only need the class labels
                df = df.rename(
                    columns={
                        self._first_directory_in_path: inferred_class_label_column_name,
                    },
                    # We use raise here as there's _only_ the one column we care
                    # about so it _needs_ to be present
                    errors="raise",
                )

        # Drop any intermediate columns that aren't needed
        df = df.drop(
            columns=[
                self._first_directory_in_path,
                self._second_directory_in_path,
                self._unused_directory_in_path,
            ],
            errors="ignore",
        )
        return df

    @abstractmethod
    def _process_file(
        self,
        filename: str,
        full_data: bool,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """Implement to process a single file.

        Files may contain more than one datapoint, so this function can return a list
        of dictionaries.

        Args:
            filename: The name of the file to process.
            full_data: True if we're loading all data and want to append to existing
                data.

        """
        raise NotImplementedError

    @abstractmethod
    def _process_dataset(self, dataframe: pd.DataFrame, **kwargs: Any) -> pd.DataFrame:
        """This method can be overridden to perform any processing of the dataset."""
        raise NotImplementedError

    def _add_metadata_to_data(
        self, data: Dict[str, Any], filename: str
    ) -> Dict[str, Any]:
        """Adds metadata to the data.

        Args:
            data: The data to add metadata to.
            filename: The filename of the file to be processed.

        Returns:
            The data with metadata added.
        """
        data[ORIGINAL_FILENAME_METADATA_COLUMN] = filename
        modify_time = os.path.getmtime(filename)
        data[LAST_MODIFIED_METADATA_COLUMN] = datetime.fromtimestamp(
            modify_time
        ).isoformat()
        # Track the first two directory levels so that we can easily
        # process the possible labels later on as needed
        relative_filepath = Path(filename).relative_to(self.path).parts
        if len(relative_filepath) > 1:
            data[self._first_directory_in_path] = relative_filepath[0]
        if len(relative_filepath) > 2:
            data[self._second_directory_in_path] = relative_filepath[1]

        return data
