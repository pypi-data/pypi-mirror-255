import contextlib
import logging
import typing
from abc import ABC
from abc import abstractmethod
from typing import Optional

import attrs
import pandas as pd
import pyarrow

from tecton_core.query.dialect import Dialect
from tecton_core.query.node_interface import NodeRef
from tecton_core.query.nodes import DataSourceScanNode
from tecton_core.schema import Schema
from tecton_core.secrets import SecretResolver


logger = logging.getLogger(__name__)

ProgressLogger = typing.Callable[[float], None]
SQLParam = typing.Optional[str]
MonitoringContextProvider = typing.Callable[[SQLParam], typing.ContextManager[ProgressLogger]]


@contextlib.contextmanager
def dummy_context(sql: str) -> ProgressLogger:
    yield lambda _: None


@attrs.define
class QueryTreeCompute(ABC):
    """
    Base class for compute (e.g. DWH compute or Python compute) which can be
    used for different stages of executing the query tree.
    """

    monitoring_ctx: Optional[MonitoringContextProvider] = attrs.field(kw_only=True, default=dummy_context)

    @staticmethod
    def for_dialect(dialect: Dialect) -> "QueryTreeCompute":
        # Conditional imports are used so that optional dependencies such as the Snowflake connector are only imported
        # if they're needed for a query
        if dialect == Dialect.SNOWFLAKE:
            from tecton_core.query.snowflake.compute import SnowflakeCompute

            return SnowflakeCompute.from_context()
        if dialect == Dialect.DUCKDB:
            from tecton_core.query.duckdb.compute import DuckDBCompute

            return DuckDBCompute.from_context()
        if dialect == Dialect.PANDAS:
            from tecton_core.query.pandas.compute import PandasCompute

            return PandasCompute.from_context()

    @abstractmethod
    def get_dialect(self) -> Dialect:
        pass

    @abstractmethod
    def run_sql(
        self, sql_string: str, return_dataframe: bool = False, expected_output_schema: Optional[Schema] = None
    ) -> Optional[pyarrow.Table]:
        pass

    @abstractmethod
    def run_odfv(self, qt_node: NodeRef, input_df: pd.DataFrame) -> pd.DataFrame:
        pass

    @abstractmethod
    def register_temp_table(self, table_name: str, pa_table: pyarrow.Table) -> None:
        pass

    # TODO(danny): remove this once we convert connectors to return arrow tables instead of pandas dataframes
    @abstractmethod
    def register_temp_table_from_pandas(self, table_name: str, pandas_df: pd.DataFrame) -> None:
        pass

    @abstractmethod
    def register_temp_table_from_data_source(
        self, table_name: str, ds: DataSourceScanNode, secret_resolver: Optional[SecretResolver]
    ) -> None:
        pass

    @abstractmethod
    def load_table(self, table_name: str) -> pyarrow.Table:
        pass

    def cleanup_temp_tables(self):
        pass

    def with_monitoring_ctx(self, m: MonitoringContextProvider) -> "QueryTreeCompute":
        """Returns a copy of the instance with updated monitoring_ctx attribute"""
        return attrs.evolve(self, monitoring_ctx=m)
