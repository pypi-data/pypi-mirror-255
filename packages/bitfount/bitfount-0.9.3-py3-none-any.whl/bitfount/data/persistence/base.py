"""Base interface for data persistence implementations."""
from __future__ import annotations

from abc import ABC, abstractmethod
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from typing import Collection, Final, Optional, Union


_IMAGE_COL_PLACEHOLDER: Final = "<Image Data or File Path>"

_logger = logging.getLogger(__name__)


class DataPersister(ABC):
    """Abstract interface for data persistence/caching implementations."""

    def get(self, file: Union[str, Path]) -> Optional[pd.DataFrame]:
        """Get the persisted data for a given file.

        Returns None if no data has been persisted, if it is out of date, or an
        error was otherwise encountered.
        """
        # Catch underlying errors here.
        # Worst case scenario is that something cannot use the cached data.
        try:
            return self._get(file)
        except Exception as e:
            _logger.warning(f"Error whilst retrieving cache entry for {file}: {str(e)}")
            return None

    @abstractmethod
    def _get(self, file: Union[str, Path]) -> Optional[pd.DataFrame]:
        """Get the persisted data for a given file.

        Returns None if no data has been persisted or if it is out of date.
        """
        raise NotImplementedError

    def set(self, file: Union[str, Path], data: pd.DataFrame) -> None:
        """Set the persisted data for a given file.

        If existing data is already set, it will be overwritten.

        The data should only be the data that is related to that file.
        """
        # Catch underlying errors here.
        # Worst case scenario is that something cannot use the cached data later.
        try:
            self._set(file, data)
        except Exception as e:
            _logger.warning(f"Error whilst setting cache entry for {file}: {str(e)}")

    @abstractmethod
    def _set(self, file: Union[str, Path], data: pd.DataFrame) -> None:
        """Set the persisted data for a given file.

        If existing data is already set, it will be overwritten.

        The data should only be the data that is related to that file.
        """
        raise NotImplementedError

    @abstractmethod
    def unset(self, file: Union[str, Path]) -> None:
        """Deletes the persisted data for a given file."""
        # NOTE: We do _not_ implicitly catch underlying errors here.
        # The worst case scenario is that the cache fails to be invalidated, but
        # the calling code assumes it has been.
        raise NotImplementedError

    @staticmethod
    def prep_data_for_caching(
        data: pd.DataFrame, image_cols: Optional[Collection[str]] = None
    ) -> pd.DataFrame:
        """Prepares data ready for caching.

        This involves removing/replacing things that aren't supposed to be cached
        or that it makes no sense to cache, such as image data or file paths that
        won't be relevant except for when the files are actually being used.

        Does not mutate input dataframe.
        """
        data = data.copy()
        if image_cols:
            image_cols_present = set(image_cols).intersection(data.columns)
            # Replace every NON-NULL entry in every image col with
            # _IMAGE_COL_PLACEHOLDER
            for image_col in image_cols_present:
                row_mask = data[image_col].notnull()
                data.loc[row_mask, image_col] = _IMAGE_COL_PLACEHOLDER
        return data

    def bulk_set(
        self, data: pd.DataFrame, original_file_col: str = "_original_filename"
    ) -> None:
        """Bulk set a bunch of cache entries from a dataframe.

        The dataframe must indicate the original file that each row is associated
        with. This is the `_original_filename` column by default.
        """
        try:
            self._bulk_set(data, original_file_col)
        except Exception as e:
            _logger.warning(
                f"Error whilst bulk setting cache entries for data;"
                f" some or all cache entries may not have been set."
                f" Error was: {str(e)}"
            )
            return None

    def _bulk_set(
        self, data: pd.DataFrame, original_file_col: str = "_original_filename"
    ) -> None:
        """Bulk set a bunch of cache entries from a dataframe.

        The dataframe must indicate the original file that each row is associated
        with. This is the `_original_filename` column by default.
        """
        if original_file_col not in data.columns:
            _logger.warning(
                f'Original file specifying column, "{original_file_col}",'
                f" was not found in the dataframe."
                f" Unable to bulk cache entries."
            )
            return None

        # Work on copy so we can manipulate the file paths without affecting the
        # original
        data = data.copy()

        # Remove any entries without original_col path
        if not data[data[original_file_col].isnull()].empty:
            _logger.warning(
                f'Some entries are missing entries in column "{original_file_col}";'
                f" removing these before continuing."
            )
            data = data[data[original_file_col].notnull()]

        # Replace the file paths with the canonical versions of those paths
        data[original_file_col] = data[original_file_col].map(
            lambda p: str(Path(p).resolve())
        )

        # Group the data by the original file path and submit each of these to
        # `set()` individually
        file_path_str: str
        file_data: pd.DataFrame
        for file_path, file_data in data.groupby(original_file_col):
            file_path_str = str(file_path)
            self.set(file_path_str, file_data)
