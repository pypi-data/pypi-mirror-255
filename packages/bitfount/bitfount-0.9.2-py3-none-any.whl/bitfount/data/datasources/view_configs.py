"""Support for different "views" over existing datasets.

These allow constraining the usable data that is exposed to a modeller, or only
presenting a transformed view to the modeller rather than the raw underlying data.
"""
from abc import ABC, abstractmethod
import logging
from typing import (
    Any,
    Generic,
    List,
    Mapping,
    MutableMapping,
    Optional,
    TypeVar,
    Union,
    cast,
    overload,
)

from bitfount.data.datasources.base_source import BaseSource, FileSystemIterableSource
from bitfount.data.datasources.views import (
    DataView,
    DropColsDataview,
    DropColsFileSystemIterableDataview,
    SQLDataView,
    SQLFileSystemIterableDataView,
    _EmptyDataview,
)
from bitfount.data.schema import BitfountSchema
from bitfount.data.types import _ForceStypeValue, _SemanticTypeValue, _SingleOrMulti
from bitfount.utils import _add_this_to_list, delegates
from bitfount.utils.db_connector import PodDbConnector

logger = logging.getLogger(__name__)

_DS = TypeVar("_DS", bound=BaseSource)


class ViewDatasourceConfig(ABC, Generic[_DS]):
    """A class dictating the configuration of a view.

    Args:
        source_dataset: The name of the underlying datasource.
    """

    def __init__(self, source_dataset: str, *args: Any, **kwargs: Any) -> None:
        self.source_dataset_name = source_dataset

    @abstractmethod
    def generate_schema(self, *args: Any, **kwargs: Any) -> BitfountSchema:
        """Schema generation for views."""

    @abstractmethod
    def build(
        self, underlying_datasource: _DS, connector: Optional[PodDbConnector] = None
    ) -> DataView:
        """Build a view instance corresponding to this config."""


@delegates()
class DropColViewConfig(ViewDatasourceConfig[BaseSource]):
    """Config class for DropColsDropColView.

    Args:
        drop_cols: The columns to drop.
    """

    def __init__(
        self, drop_cols: _SingleOrMulti[str], *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self._drop_cols: List[str] = (
            [drop_cols] if isinstance(drop_cols, str) else list(drop_cols)
        )

    def generate_schema(
        self,
        underlying_datasource: BaseSource,
        name: str,
        force_stypes: Optional[
            MutableMapping[Union[_ForceStypeValue, _SemanticTypeValue], List[str]]
        ] = None,
        schema: Optional[BitfountSchema] = None,
    ) -> BitfountSchema:
        """Schema generation for DropColViewConfig.

        Args:
            underlying_datasource: The underlying datasource for the view.
            name: The name of the DropColViewConfig.
            force_stypes: A mapping of table names to a mapping of semantic types to
                a list of column names.
            schema: A BitfountSchema object. If provided, the schema will not be
                re-generated.

        Returns:
            A BitfountSchema object.
        """
        # Actually generate the schema
        if not schema:
            view = self.build(underlying_datasource)
            view_columns = view.get_dtypes().keys()
            if force_stypes:
                view_force_stypes = {}
                # adapt force stypes from underlying datasource to fit the drop view
                for k, v in force_stypes.items():
                    # We need special handling for `image_prefix`. This is because
                    # `image_prefix` is not part of the schema features, but just an
                    # easier way for a user to specify (especially in the YAML format).
                    # the image columns of a datasource.
                    if k not in ["image_prefix", "image"]:
                        # Extract only the columns present in the datasource.
                        view_force_stypes[k] = [col for col in v if col in view_columns]
                    elif k == "image_prefix":
                        # If `image_prefix` is in `force_stypes`, we need to add the
                        # columns that start with that prefix to the image features
                        # in the schema.
                        img_cols = [
                            col
                            for col in view_columns
                            if any(
                                col.startswith(stype)
                                for stype in force_stypes["image_prefix"]
                            )
                        ]
                        if len(img_cols) > 0:
                            # The image features might have processed so we don't
                            # want to overwrite them if that is the case
                            if "image" in view_force_stypes:
                                view_force_stypes["image"] = _add_this_to_list(
                                    img_cols, view_force_stypes["image"]
                                )
                            else:
                                view_force_stypes["image"] = img_cols
                    else:  # if k == "image"
                        # Similarly, image features might have been
                        # already added so we don't want to overwrite them
                        if "image" in view_force_stypes:
                            img_cols = [col for col in v if col in view_columns]
                            view_force_stypes["image"] = _add_this_to_list(
                                img_cols, view_force_stypes["image"]
                            )
                        else:
                            view_force_stypes["image"] = [
                                col for col in v if col in view_columns
                            ]
                view_force_stype = {name: view_force_stypes}
            else:
                view_force_stype = None
            logger.info(f"Generating schema for DropColView {name}")
            schema = BitfountSchema()
            schema.add_datasource_tables(
                datasource=view,
                table_name=name,
                force_stypes=cast(
                    Optional[
                        Mapping[
                            str,
                            MutableMapping[
                                Union[_SemanticTypeValue, _ForceStypeValue], List[str]
                            ],
                        ]
                    ],
                    view_force_stype,
                ),
            )
        return schema

    @overload
    def build(
        self,
        underlying_datasource: FileSystemIterableSource,
        connector: Optional[PodDbConnector] = None,
    ) -> DropColsFileSystemIterableDataview:
        ...

    @overload
    def build(
        self,
        underlying_datasource: BaseSource,
        connector: Optional[PodDbConnector] = None,
    ) -> DropColsDataview:
        ...

    def build(
        self,
        underlying_datasource: Union[BaseSource, FileSystemIterableSource],
        connector: Optional[PodDbConnector] = None,
    ) -> Union[DropColsDataview, DropColsFileSystemIterableDataview]:
        """Build a DropColsCSVDropColView from this configuration.

        Args:
            underlying_datasource: The underlying datasource for the view.
            connector: An optional PodDbConnector object.

        Returns:
            A DropColsDataview object.
        """
        klass = (
            DropColsFileSystemIterableDataview
            if isinstance(underlying_datasource, FileSystemIterableSource)
            else DropColsDataview
        )
        return klass(
            datasource=underlying_datasource,
            drop_cols=self._drop_cols,
            source_dataset_name=self.source_dataset_name,
        )


@delegates()
class SQLViewConfig(ViewDatasourceConfig[BaseSource]):
    """Config class for SQLDataViewConfig.

    Args:
        query: The SQL query for the view.

    Raises:
        ValueError: if the query does not start with SELECT.
    """

    def __init__(self, query: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        # Raise error at the beginning if query does not start with `SELECT`.
        # TODO: [NO_TICKET: Reason] Add better checking of the query after the query parser is built on the platform side. # noqa: B950
        if not query.lstrip().startswith("SELECT"):
            raise ValueError(
                "Unsupported query. We currently support only "
                "`SELECT ... FROM ...` queries for defining "
                "dataset views."
            )
        self.query = query

    def initialize(self, pod_name: str) -> None:
        """Initialize the view by providing the pod name for the database."""
        self.pod_name = pod_name

    def generate_schema(
        self,
        underlying_datasource: BaseSource,
        name: str,
        force_stypes: Optional[
            MutableMapping[Union[_ForceStypeValue, _SemanticTypeValue], List[str]]
        ] = None,
        schema: Optional[BitfountSchema] = None,
        connector: Optional[PodDbConnector] = None,
    ) -> BitfountSchema:
        """Schema generation for SQLDataViewConfig.

        Args:
            underlying_datasource: The underlying datasource for the view.
            name: The name of the SQLDataViewConfig.
            force_stypes: A mapping of table names to a mapping of semantic types to
                a list of column names.
            schema: A BitfountSchema object. If provided, the schema will not be
                re-generated.
            connector: An optional PodDbConnector object.

        Returns:
            A BitfountSchema object.
        """
        if not schema:
            view = self.build(underlying_datasource, connector)
            data = view.get_data()
            if data is not None:
                view_columns = data.columns.to_list()
            else:
                view_columns = []
            if force_stypes:
                view_force_stypes = {}
                # adapt force stypes from underlying datasource to fit the drop view
                for k, v in force_stypes.items():
                    # We need special handling for `image_prefix`. This is because
                    # `image_prefix` is not part of the schema features, but just an
                    # easier way for a user to specify (especially in the YAML format).
                    # the image columns of a datasource.
                    if k not in ["image_prefix", "image"]:
                        # Extract only the columns present in the datasource.
                        view_force_stypes[k] = [col for col in v if col in view_columns]
                    elif k == "image_prefix":
                        # If `image_prefix` is in `force_stypes`, we need to add the
                        # columns that start with that prefix to the image features
                        # in the schema.
                        img_cols = [
                            col
                            for col in view_columns
                            if any(
                                col.startswith(stype)
                                for stype in force_stypes["image_prefix"]
                            )
                        ]
                        if len(img_cols) > 0:
                            # The image features might have processed, so we don't
                            # want to overwrite them if that is the case
                            if "image" in view_force_stypes:
                                view_force_stypes["image"] = _add_this_to_list(
                                    img_cols, view_force_stypes["image"]
                                )
                            else:
                                view_force_stypes["image"] = img_cols
                    else:  # if k == "image"
                        # Similarly, image features might have been
                        # already added, so we don't want to overwrite them
                        if "image" in view_force_stypes:
                            img_cols = [col for col in v if col in view_columns]
                            view_force_stypes["image"] = _add_this_to_list(
                                img_cols, view_force_stypes["image"]
                            )
                        else:
                            view_force_stypes["image"] = [
                                col for col in v if col in view_columns
                            ]
                view_force_stype = {name: view_force_stypes}
            else:
                view_force_stype = None
            # Actually generate schema
            logger.info(f"Generating schema for SQLDataView {name}")
            schema = BitfountSchema()
            schema.add_datasource_tables(
                datasource=view,
                table_name=name,
                force_stypes=cast(
                    Optional[
                        Mapping[
                            str,
                            MutableMapping[
                                Union[_SemanticTypeValue, _ForceStypeValue], List[str]
                            ],
                        ]
                    ],
                    view_force_stype,
                ),
            )
        return schema

    @overload
    def build(
        self,
        underlying_datasource: FileSystemIterableSource,
        connector: Optional[PodDbConnector] = None,
    ) -> Union[SQLFileSystemIterableDataView, DataView]:
        ...

    @overload
    def build(
        self,
        underlying_datasource: BaseSource,
        connector: Optional[PodDbConnector] = None,
    ) -> Union[SQLDataView, DataView]:
        ...

    def build(
        self,
        underlying_datasource: Union[BaseSource, FileSystemIterableSource],
        connector: Optional[PodDbConnector] = None,
    ) -> Union[SQLDataView, SQLFileSystemIterableDataView, DataView]:
        """Build a SQLDataViewConfig from this configuration.

        Args:
            underlying_datasource: The underlying datasource for the view.
            connector: An optional PodDbConnector object.

        Returns:
            A SQLDataView when connector is provided or
            An empty DataView when connector is not provided.
        """
        # TODO: [BIT-3402]: Replace tmp return of EmptyDataview with exception
        # This currently causes the schema for the view to completely change
        # and match the parent datasource's schema instead when the schema is
        # updated after a task.
        if connector is None:
            logger.warning(
                "SQLViews are only supported with pods that "
                + "have the pod database enabled."
            )
            return _EmptyDataview(underlying_datasource, self.source_dataset_name)

        klass = (
            SQLFileSystemIterableDataView
            if isinstance(underlying_datasource, FileSystemIterableSource)
            else SQLDataView
        )

        return klass(
            datasource=underlying_datasource,
            source_dataset_name=self.source_dataset_name,
            query=self.query,
            pod_name=self.pod_name,
            connector=connector,
        )
