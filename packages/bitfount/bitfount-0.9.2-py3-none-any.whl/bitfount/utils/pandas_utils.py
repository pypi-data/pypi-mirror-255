"""Utility functions for interacting with pandas."""
import logging
from typing import Callable, Generator, Iterable

from pandas import RangeIndex
import pandas as pd

_logger = logging.getLogger(__name__)


def conditional_dataframe_yielder(
    dfs: Iterable[pd.DataFrame],
    condition: Callable[[pd.DataFrame], pd.DataFrame],
    reset_index: bool = True,
) -> Generator[pd.DataFrame, None, None]:
    """Create a generator that conditionally yields rows from a set of dataframes.

    This replicates the standard `.loc` conditional indexing that can be used on
    a whole dataframe in a manner that can be applied to an iterable of dataframes
    such as is returned when chunking a CSV file.

    Args:
        dfs: An iterable of dataframes to conditionally yield rows from.
        condition: A callable that takes in a dataframe, applied a condition, and
            returns the edited/filtered dataframe.
        reset_index: Whether the index of the yielded dataframes should be reset.
            If True, a standard integer index is used that is consistent between
            the yielded dataframes (e.g. if yielded dataframe 10 ends with index
            42, yielded dataframe 11 will start with index 43).

    Yields:
        Dataframes from the iterable with rows included/excluded based on the
        condition. Empty dataframes, post-condition, are skipped.
    """
    curr_idx = 0
    for i, df in enumerate(dfs):
        tmp_df = condition(df)

        if tmp_df.empty:
            _logger.debug(
                f"Empty dataframe from applying {condition=} to dataframe {i}"
                f" of dataframe iterable;"
                f" skipping..."
            )
            continue
        else:
            new_rows = len(tmp_df)
            next_idx = curr_idx + new_rows

            if reset_index:
                print(f"{curr_idx=}, {new_rows=}")
                idx = RangeIndex(curr_idx, next_idx)
                tmp_df = tmp_df.set_index(idx)

            yield tmp_df

            curr_idx = next_idx


def dataframe_iterable_join(
    joiners: Iterable[pd.DataFrame],
    joinee: pd.DataFrame,
    reset_joiners_index: bool = False,
) -> Generator[pd.DataFrame, None, None]:
    """Performs a dataframe join against a collection of dataframes.

    This replicates the standard `.join()` method that can be used on a whole
    dataframe in a manner that can be applied to an iterable of dataframes such
    as is returned when chunking a CSV file.

    This is equivalent to:
    ```
    joiner.join(joinee)
    ```

    Args:
        joiners: The collection of dataframes that should be joined against the joinee.
        joinee: The single dataframe that the others should be joined against.
        reset_joiners_index: Whether the index of the joiners dataframes should
            be reset as they are processed. If True, a standard integer index is
            used that is consistent between the yielded dataframes (e.g. if yielded
            dataframe 10 ends with index 42, yielded dataframe 11 will start with
            index 43).

    Yields:
        Dataframes from the iterable joined against the joineee. Empty dataframes
        are skipped.
    """
    curr_joiner_idx = 0
    for i, joiner in enumerate(joiners):
        if reset_joiners_index:
            new_joiner_rows = len(joiner)
            next_joiner_idx = curr_joiner_idx + new_joiner_rows

            idx = RangeIndex(curr_joiner_idx, next_joiner_idx)
            joiner = joiner.set_index(idx)

            curr_joiner_idx = next_joiner_idx

        joined: pd.DataFrame = joiner.join(joinee)

        if joined.empty:
            _logger.debug(
                f"Empty dataframe from joining joinee dataframe to dataframe {i}"
                f" of dataframe iterable;"
                f" skipping..."
            )
            continue
        else:
            yield joined
