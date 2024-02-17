from typing import Optional

import attrs
import pandas as pd
import pyarrow

from tecton_core import conf
from tecton_core.query.dialect import Dialect
from tecton_core.query.duckdb.compute import DuckDBCompute
from tecton_core.query.node_interface import NodeRef
from tecton_core.query.nodes import DataSourceScanNode
from tecton_core.query.pandas.nodes import PandasDataSourceScanNode
from tecton_core.query.query_tree_compute import QueryTreeCompute
from tecton_core.query.query_tree_compute import logger
from tecton_core.schema import Schema
from tecton_core.secrets import SecretResolver
from tecton_core.specs import FileSourceSpec


@attrs.frozen
class PandasCompute(QueryTreeCompute):
    # For executing pipelines, Pandas will execute only the data source scan + pipeline nodes. Other
    # logic e.g. around asof joins are executed using DuckDB.
    sql_compute: DuckDBCompute

    @staticmethod
    def from_context() -> "PandasCompute":
        return PandasCompute(sql_compute=DuckDBCompute.from_context())

    def run_sql(
        self, sql_string: str, return_dataframe: bool = False, expected_output_schema: Optional[Schema] = None
    ) -> Optional[pyarrow.Table]:
        with self.monitoring_ctx(sql_string) as progress_logger:
            progress_logger(0.0)
            res = self.sql_compute.run_sql(sql_string, return_dataframe)
            progress_logger(1.0)
            return res

    def get_dialect(self) -> Dialect:
        return Dialect.DUCKDB

    def register_temp_table_from_pandas(self, table_name: str, pandas_df: pd.DataFrame) -> None:
        self.sql_compute.register_temp_table_from_pandas(table_name, pandas_df)

    def register_temp_table(self, table_name: str, pa_table: pyarrow.Table) -> None:
        self.sql_compute.register_temp_table(table_name, pa_table)

    def register_temp_table_from_data_source(
        self, table_name: str, ds: DataSourceScanNode, secret_resolver: Optional[SecretResolver]
    ) -> None:
        if isinstance(ds.ds.batch_source, FileSourceSpec):
            return self.sql_compute.register_temp_table_from_data_source(table_name, ds, secret_resolver)

        with self.monitoring_ctx(None) as progress_logger:
            progress_logger(0.0)
            pandas_node = PandasDataSourceScanNode.from_node_inputs(
                query_node=ds, input_node=None, secret_resolver=secret_resolver
            )
            self.register_temp_table_from_pandas(table_name, pandas_node.to_dataframe())
            progress_logger(1.0)

    def load_table(self, table_name: str) -> pyarrow.Table:
        return self.sql_compute.load_table(table_name)

    def run_odfv(self, qt_node: NodeRef, input_df: pd.DataFrame) -> pd.DataFrame:
        from tecton_core.query.pandas.translate import pandas_convert_odfv_only

        if conf.get_bool("DUCKDB_DEBUG"):
            logger.warning(f"Input dataframe to ODFV execution: {input_df.dtypes}")

        with self.monitoring_ctx(None) as progress_logger:
            progress_logger(0.0)
            pandas_node = pandas_convert_odfv_only(qt_node, input_df)
            df = pandas_node.to_dataframe()
            progress_logger(1.0)
            return df
