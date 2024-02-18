"""Support for different "views" over existing datasets.

These allow constraining the usable data that is exposed to a modeller, or only
presenting a transformed view to the modeller rather than the raw underlying data.
"""
from abc import ABC
from functools import cached_property
import logging
from typing import Any, Dict, Iterable, Iterator, List, Optional, Set, Union

import methodtools
import numpy as np
import pandas as pd

from bitfount.data.datasources.base_source import BaseSource, FileSystemIterableSource
from bitfount.data.datasources.empty_source import _EmptySource
from bitfount.data.datasources.utils import (
    FILE_SYSTEM_ITERABLE_METADATA_COLUMNS,
    ORIGINAL_FILENAME_METADATA_COLUMN,
)
from bitfount.data.datasplitters import DatasetSplitter
from bitfount.data.types import _SingleOrMulti
from bitfount.types import _Dtypes
from bitfount.utils import delegates
from bitfount.utils.db_connector import PodDbConnector

logger = logging.getLogger(__name__)


class DataView(BaseSource, ABC):
    """Base class for datasource views.

    Args:
        datasource: The `BaseSource` the view is generated from.
    """

    def __init__(
        self,
        datasource: BaseSource,
        source_dataset_name: str,
        data_splitter: Optional[DatasetSplitter] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._datasource = datasource
        self.source_dataset_name = source_dataset_name
        self.data_splitter = (
            data_splitter
            if data_splitter is not None
            else self._datasource.data_splitter
        )

    @property
    def is_task_running(self) -> bool:
        """Returns `_is_task_running` for the view and the parent datasource."""
        return self._is_task_running and self._datasource.is_task_running

    @is_task_running.setter
    def is_task_running(self, value: bool) -> None:
        """Sets `_is_task_running` to `value` for the view and the parent datasource."""
        self._is_task_running = value
        self._datasource.is_task_running = value

    def load_data(self, **kwargs: Any) -> None:
        """Loads data from the underlying datasource."""
        self._datasource.load_data(**kwargs)
        super().load_data(**kwargs)


@delegates()
class _DataViewFromFileIterableSource(DataView):
    """A data view derived from a file-iterable datasource."""

    _datasource: FileSystemIterableSource

    def __init__(
        self,
        datasource: FileSystemIterableSource,
        source_dataset_name: str,
        data_splitter: Optional[DatasetSplitter] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            datasource=datasource,
            source_dataset_name=source_dataset_name,
            data_splitter=data_splitter,
            **kwargs,
        )

    @property
    def fast_load(self) -> bool:
        """Returns `fast_load` for the view."""
        raise NotImplementedError

    @property
    def cache_images(self) -> bool:
        """Returns `cache_images` for the view."""
        raise NotImplementedError

    @property
    def image_columns(self) -> Set[str]:
        """Returns `image_columns` for the view."""
        raise NotImplementedError

    @property
    def selected_file_names_override(self) -> List[str]:
        """Returns `selected_file_names_override` for the view."""
        raise NotImplementedError

    @selected_file_names_override.setter
    def selected_file_names_override(self, value: List[str]) -> None:
        """Sets `selected_file_names_override` for the view."""
        raise NotImplementedError

    @property
    def new_file_names_only_set(self) -> Union[Set[str], None]:
        """Returns `new_file_names_only_set` for the view."""
        raise NotImplementedError

    @new_file_names_only_set.setter
    def new_file_names_only_set(self, value: Union[Set[str], None]) -> None:
        """Sets `new_file_names_only_set` for the view."""
        raise NotImplementedError

    @property
    def selected_file_names(self) -> List[str]:
        """Returns `selected_file_names` for the view."""
        raise NotImplementedError

    @property
    def file_names(self) -> List[str]:
        """Get filenames for views generated from FileSystemIterableSource."""
        raise NotImplementedError

    def yield_data(
        self, file_names: Optional[List[str]] = None, **kwargs: Any
    ) -> Iterator[pd.DataFrame]:
        """Returns `file_names` for the view and the parent datasource."""
        raise NotImplementedError

    def _get_data(
        self, file_names: Optional[List[str]] = None, **kwargs: Any
    ) -> pd.DataFrame:
        """Returns data corresponding to the provided file names."""
        raise NotImplementedError


@delegates()
class _EmptyDataview(DataView):
    """A data view that presents no data.

    This internal class is used for retuning empty DataView
    when SQLDataView cannot be instantiated because of no
    connector provided.
    We return an _EmptyDataview object and log instead of
    raising an error.
    """

    _datasource: _EmptySource

    def get_values(
        self, col_names: List[str], **kwargs: Any
    ) -> Dict[str, Iterable[Any]]:
        """Returns empty dictionary as there are no columns to return."""
        return {}

    def get_column_names(self, **kwargs: Any) -> Iterable[str]:
        """Returns list as there are no columns to return."""
        return list()

    def get_column(self, col_name: str, **kwargs: Any) -> Union[np.ndarray, pd.Series]:
        """Returns empty np array as there are no columns to return."""
        return np.array([])

    def get_data(self, **kwargs: Any) -> None:
        """Returns None as there is no data."""
        return self._datasource.get_data()

    def get_dtypes(self, **kwargs: Any) -> _Dtypes:
        """Returns an empty dict as there is no data."""
        return self._datasource.get_dtypes()

    def __len__(self) -> int:
        """Returns zero as there is no data."""
        return len(self._datasource)


@delegates()
class DropColsDataview(DataView):
    """A data view that presents data with columns removed."""

    _datasource: BaseSource

    def __init__(
        self,
        datasource: BaseSource,
        drop_cols: _SingleOrMulti[str],
        source_dataset_name: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            datasource=datasource, source_dataset_name=source_dataset_name, **kwargs
        )
        self._drop_cols: List[str] = (
            [drop_cols] if isinstance(drop_cols, str) else list(drop_cols)
        )

    # TODO: [BIT-1780] Simplify referencing data in here and in other sources
    #       We want to avoid recalculating but we don't want to cache more
    #       than one result at a time to save memory
    @methodtools.lru_cache(maxsize=1)
    def get_data(self, **kwargs: Any) -> pd.DataFrame:
        """Loads and returns data from underlying dataset.

        Will handle drop columns specified in view.

        Returns:
            A DataFrame-type object which contains the data.

        Raises:
            ValueError: if no data is returned from the original datasource.
        """
        df: Optional[pd.DataFrame] = self._datasource.get_data(**kwargs)
        # Ensure we return a copy of the dataframe rather than mutating the original
        if isinstance(df, pd.DataFrame):
            drop_df = df.drop(columns=self._drop_cols)
            return drop_df
        else:
            raise ValueError("No data returned from the underlying datasource.")

    def get_values(
        self, col_names: List[str], **kwargs: Any
    ) -> Dict[str, Iterable[Any]]:
        """Get distinct values from columns in dataset.

        Args:
            col_names: The list of the columns whose distinct values should be
                returned.

        Returns:
            The distinct values of the requested column as a mapping from col name to
            a series of distinct values.

        """
        data: pd.DataFrame = self.get_data(**kwargs)
        return {col: data[col].unique() for col in col_names}

    def get_column_names(self, **kwargs: Any) -> Iterable[str]:
        """Get the column names as an iterable."""
        df: pd.DataFrame = self.get_data(**kwargs)
        return list(df.columns)

    def get_column(self, col_name: str, **kwargs: Any) -> Union[np.ndarray, pd.Series]:
        """Loads and returns single column from dataset.

        Args:
            col_name: The name of the column which should be loaded.

        Returns:
            The column request as a series.
        """
        df: pd.DataFrame = self.get_data(**kwargs)
        return df[col_name]

    def get_dtypes(self, **kwargs: Any) -> _Dtypes:
        """Loads and returns the columns and column types of the dataset.

        Returns:
            A mapping from column names to column types.
        """
        df: pd.DataFrame = self.get_data(**kwargs)
        return self._get_data_dtypes(df)

    def __len__(self) -> int:
        return len(self.get_data())


@delegates()
class DropColsFileSystemIterableDataview(
    DropColsDataview, _DataViewFromFileIterableSource
):
    """A data view that presents filesystem iterable data with columns removed.

    Raises:
        ValueError: if the underlying datasource is not of
            FileSystemIterableSource type.
    """

    _datasource: FileSystemIterableSource

    def __init__(
        self,
        datasource: BaseSource,
        drop_cols: _SingleOrMulti[str],
        source_dataset_name: str,
        **kwargs: Any,
    ) -> None:
        if not isinstance(datasource, FileSystemIterableSource):
            raise ValueError(
                "Underlying datasource is not a `FileSystemIterableSource`, "
                "which is the only compatible datasource for this view."
            )

        super().__init__(
            datasource=datasource,
            drop_cols=drop_cols,
            source_dataset_name=source_dataset_name,
            **kwargs,
        )

    @property
    def fast_load(self) -> bool:
        """Returns `fast_load` for the view."""
        return self._datasource.fast_load

    @property
    def cache_images(self) -> bool:
        """Returns `cache_images` for the view."""
        return self._datasource.cache_images

    @property
    def image_columns(self) -> Set[str]:
        """Returns `image_columns` for the view, excluding those in `drop_cols`."""
        return self._datasource.image_columns - set(self._drop_cols)

    @property
    def selected_file_names_override(self) -> List[str]:
        """Returns `selected_file_names_override` for the view."""
        return self._datasource.selected_file_names_override

    @selected_file_names_override.setter
    def selected_file_names_override(self, value: List[str]) -> None:
        """Sets `selected_file_names_override` for the view."""
        self._datasource.selected_file_names_override = value

    @property
    def new_file_names_only_set(self) -> Union[Set[str], None]:
        """Returns `new_file_names_only_set` for the view."""
        return self._datasource.new_file_names_only_set

    @new_file_names_only_set.setter
    def new_file_names_only_set(self, value: Union[Set[str], None]) -> None:
        """Sets `new_file_names_only_set` for the view."""
        self._datasource.new_file_names_only_set = value

    @property
    def selected_file_names(self) -> List[str]:
        """Returns `selected_file_names` for the view."""
        return self._datasource.selected_file_names

    @cached_property
    def file_names(self) -> List[str]:
        """Get filenames for views generated from FileSystemIterableSource."""
        return self._datasource.file_names

    @property
    def iterable(self) -> bool:
        """Returns `iterable` for the view and the parent datasource."""
        return self._datasource.iterable

    def yield_data(
        self, file_names: Optional[List[str]] = None, **kwargs: Any
    ) -> Iterator[pd.DataFrame]:
        """Returns `file_names` for the view and the parent datasource."""
        return self._datasource.yield_data(file_names=file_names, **kwargs)

    def _get_data(
        self, file_names: Optional[List[str]] = None, **kwargs: Any
    ) -> pd.DataFrame:
        """Returns data corresponding to the provided file names."""
        return self._datasource._get_data(file_names=file_names, **kwargs)


@delegates()
class SQLDataView(DataView):
    """A data view that presents data with SQL query applied.

    Raises:
        ValueError: if the underlying datasource is of
            IterableSource type.
    """

    _datasource: BaseSource
    _connector: PodDbConnector

    def __init__(
        self,
        datasource: BaseSource,
        query: str,
        pod_name: str,
        source_dataset_name: str,
        connector: PodDbConnector,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            datasource=datasource, source_dataset_name=source_dataset_name, **kwargs
        )
        self._connector = connector
        self.query = query
        self.pod_db_name = pod_name

    def _get_updated_query_with_metadata(self) -> str:
        """Get updated query with metadata columns included.

        For non-iterable datasources the `datapoint_hash`
        column is added.
        """
        metadata_cols_as_str = '"datapoint_hash",'
        if "datapoint_hash" not in self.query:
            return self.query.replace("SELECT", f"SELECT {metadata_cols_as_str}")
        return self.query

    @methodtools.lru_cache(maxsize=1)
    def get_data(self, **kwargs: Any) -> pd.DataFrame:
        """Loads and returns data from underlying dataset.

        Will handle sql query specified in view.

        Returns:
            A DataFrame-type object which contains the data.

        Raises:
            ValueError: if the table specified in the query is not found.
        """
        # Get tables and check that table requested in
        # the query matches at least one of the tables in the database.
        db_conn = self._connector.get_db_connection_from_name(self.pod_db_name)
        tables = self.get_tables()
        if not any(table in self.query for table in tables):
            db_conn.close()
            logger.warning("The table specified in the query does not exist.")
            # Return empty dataframe
            return pd.DataFrame()
        df = pd.read_sql_query(self.query, db_conn)
        db_conn.close()
        return df

    def get_tables(self) -> List[str]:
        """Get the datasource tables from the pod database."""
        db_conn = self._connector.get_db_connection_from_name(self.pod_db_name)
        cur = db_conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cur.fetchall()
        db_conn.close()
        # tables are returned as a list of tuples where the first tuple
        # is the table name, so we need to unpack them
        return [table[0] for table in tables]

    def get_values(
        self, col_names: List[str], table_name: Optional[str] = None, **kwargs: Any
    ) -> Dict[str, Iterable[Any]]:
        """Get distinct values from columns in the dataset.

        Args:
            col_names: The list of the columns whose distinct values should be
                returned.

        Returns:
            The distinct values of the requested column as a mapping from col name to
            a series of distinct values.

        """
        data: pd.DataFrame = self.get_data(**kwargs)
        return {col: data[col].unique() for col in col_names}

    def get_column_names(self, **kwargs: Any) -> Iterable[str]:
        """Get the column names as an iterable."""
        df: pd.DataFrame = self.get_data(**kwargs)
        return list(df.columns)

    def get_column(
        self, col_name: str, table_name: Optional[str] = None, **kwargs: Any
    ) -> Union[np.ndarray, pd.Series]:
        """Loads and returns single column from dataset.

        Args:
            col_name: The name of the column which should be loaded.

        Returns:
            The column request as a series.
        """

        df: pd.DataFrame = self.get_data(**kwargs)
        return df[col_name]

    def get_dtypes(self, table_name: Optional[str] = None, **kwargs: Any) -> _Dtypes:
        """Loads and returns the columns and column types of the dataset.

        Returns:
            A mapping from column names to column types.
        """
        df: pd.DataFrame = self.get_data(**kwargs)
        return self._get_data_dtypes(df)

    def __len__(self) -> int:
        return len(self.get_data())


@delegates()
class SQLFileSystemIterableDataView(SQLDataView, _DataViewFromFileIterableSource):
    """A data view that presents filesystem iterable data with SQL query applied.

    Raises:
        ValueError: if the underlying datasource is not of
            FileSystemIterableSource type.
    """

    _datasource: FileSystemIterableSource

    def __init__(
        self,
        datasource: BaseSource,
        query: str,
        pod_name: str,
        source_dataset_name: str,
        connector: PodDbConnector,
        **kwargs: Any,
    ) -> None:
        if not isinstance(datasource, FileSystemIterableSource):
            raise ValueError(
                "Underlying datasource is not a `FileSystemIterableSource`, "
                "which is the only compatible datasource for this view."
            )

        super().__init__(
            datasource=datasource,
            query=query,
            pod_name=pod_name,
            source_dataset_name=source_dataset_name,
            connector=connector,
            **kwargs,
        )

    @property
    def fast_load(self) -> bool:
        """Returns `fast_load` for the view."""
        return self._datasource.fast_load

    @property
    def cache_images(self) -> bool:
        """Returns `cache_images` for the view."""
        return self._datasource.cache_images

    @property
    def image_columns(self) -> Set[str]:
        """Returns `image_columns` for the view."""
        return self._datasource.image_columns

    @property
    def selected_file_names_override(self) -> List[str]:
        """Returns `selected_file_names_override` for the view."""
        return self._datasource.selected_file_names_override

    @selected_file_names_override.setter
    def selected_file_names_override(self, value: List[str]) -> None:
        """Sets `selected_file_names_override` for the view."""
        self._datasource.selected_file_names_override = value

    @property
    def new_file_names_only_set(self) -> Union[Set[str], None]:
        """Returns `new_file_names_only_set` for the view."""
        return self._datasource.new_file_names_only_set

    @new_file_names_only_set.setter
    def new_file_names_only_set(self, value: Union[Set[str], None]) -> None:
        """Sets `new_file_names_only_set` for the view."""
        self._datasource.new_file_names_only_set = value

    @property
    def selected_file_names(self) -> List[str]:
        """Returns `selected_file_names` for the view."""
        return [
            file
            for file in self._datasource.selected_file_names
            if file in self.file_names
        ]

    @cached_property
    def file_names(self) -> List[str]:
        """Get filenames for views generated from FileSystemIterableSource."""
        db_conn = self._connector.get_db_connection_from_name(self.pod_db_name)
        tables = self.get_tables()
        if not any(table in self.query for table in tables):
            logger.warning("The table specified in the query does not exist.")
        # We get the updated query that also includes the `_original_filename`
        # column, so we can obtain the list of filenames from the view.
        query_with_original_filename = self._get_updated_query_with_metadata()
        try:
            df = pd.read_sql_query(query_with_original_filename, db_conn)
            return df[ORIGINAL_FILENAME_METADATA_COLUMN].tolist()
        except Exception:
            logger.warning(
                "Could not obtain the filenames for the datasource. "
                "Make sure that your file-iterable datasource is properly defined."
            )
            return []

    @property
    def iterable(self) -> bool:
        """Returns `iterable` for the view and the parent datasource."""
        return self._datasource.iterable

    def yield_data(
        self, file_names: Optional[List[str]] = None, **kwargs: Any
    ) -> Iterator[pd.DataFrame]:
        """Returns `file_names` for the view and the parent datasource."""
        return self._datasource.yield_data(file_names=file_names, **kwargs)

    def _get_data(
        self, file_names: Optional[List[str]] = None, **kwargs: Any
    ) -> pd.DataFrame:
        """Returns data corresponding to the provided file names."""
        return self._datasource._get_data(file_names=file_names, **kwargs)

    def _get_updated_query_with_metadata(self) -> str:
        """Get updated query with metadata columns included.

        For FileSystemIterableSource the `datapoint_hash`,
        `_original_filename` and `_last_modified`
        columns are added.
        """
        metadata_cols = ["datapoint_hash"] + list(FILE_SYSTEM_ITERABLE_METADATA_COLUMNS)
        new_query = self.query
        for col in metadata_cols:
            if col not in self.query:
                new_query = new_query.replace("SELECT", f'SELECT "{col}",')
        return new_query
