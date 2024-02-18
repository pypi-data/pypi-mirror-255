import logging
import typing
from typing import Optional

import attrs
import pandas as pd
import pyarrow
import pyarrow.dataset
import pyarrow.fs
import sqlparse
from duckdb import DuckDBPyConnection

from tecton_core import conf
from tecton_core.duckdb_context import DuckDBContext
from tecton_core.offline_store import BotoOfflineStoreOptionsProvider
from tecton_core.query.dialect import Dialect
from tecton_core.query.errors import SQLCompilationError
from tecton_core.query.node_interface import NodeRef
from tecton_core.query.nodes import DataSourceScanNode
from tecton_core.query.query_tree_compute import QueryTreeCompute
from tecton_core.schema import Schema
from tecton_core.secrets import SecretResolver
from tecton_core.specs import FileSourceSpec
from tecton_proto.data import batch_data_source_pb2


@attrs.define
class DuckDBCompute(QueryTreeCompute):
    session: "DuckDBPyConnection"
    is_debug: bool = attrs.field(init=False)
    created_views: typing.List[str] = attrs.field(init=False)

    @staticmethod
    def from_context() -> "DuckDBCompute":
        return DuckDBCompute(session=DuckDBContext.get_instance().get_connection())

    def __attrs_post_init__(self):
        self.is_debug = conf.get_bool("DUCKDB_DEBUG")
        self.created_views = []

    def run_sql(
        self, sql_string: str, return_dataframe: bool = False, expected_output_schema: Optional[Schema] = None
    ) -> Optional[pyarrow.Table]:
        # Notes on case sensitivity:
        # 1. DuckDB is case insensitive when referring to column names, though preserves the
        #    underlying data casing when exporting to e.g. parquet.
        #    See https://duckdb.org/2022/05/04/friendlier-sql.html#case-insensitivity-while-maintaining-case
        #    This means that when using Snowflake for pipeline compute, the view + m13n schema is auto upper-cased
        # 2. When there is a spine provided, the original casing of that spine is used (since DuckDB separately
        #    registers the spine).
        # 3. When exporting values out of DuckDB (to user, or for ODFVs), we coerce the casing to respect the
        #    explicit schema specified. Thus ODFV definitions should reference the casing specified in the dependent
        #    FV's m13n schema.
        sql_string = sqlparse.format(sql_string, reindent=True)
        if self.is_debug:
            logging.warning(f"DUCKDB: run SQL {sql_string}")

        with self.monitoring_ctx(sql_string) as progress_loger:
            progress_loger(0.0)

            # Need to use DuckDB cursor (which creates a new connection based on the original connection)
            # to be thread-safe. It avoids a mysterious "unsuccessful or closed pending query result" error too.
            try:
                cursor = self.session.cursor()
                cursor.sql("SET TimeZone='UTC'")
                duckdb_relation = cursor.sql(sql_string)
            except Exception as e:
                raise SQLCompilationError(str(e), sql_string) from None

            if return_dataframe:
                res = duckdb_relation.arrow()
                progress_loger(1.0)
                return res

        return None

    def get_dialect(self) -> Dialect:
        return Dialect.DUCKDB

    def register_temp_table_from_pandas(self, table_name: str, pandas_df: pd.DataFrame) -> None:
        self.session.from_df(pandas_df).create_view(table_name)
        self.created_views.append(table_name)

    def register_temp_table(self, table_name: str, pa_table: pyarrow.Table) -> None:
        self.session.from_arrow(pa_table).create_view(table_name)
        self.created_views.append(table_name)

    def register_temp_table_from_data_source(
        self, table_name: str, ds: DataSourceScanNode, secret_resolver: Optional[SecretResolver]
    ) -> None:
        assert isinstance(ds.ds.batch_source, (FileSourceSpec,)), "DuckDB compute supports only File data sources"

        batch_source_spec = ds.ds.batch_source
        with self.monitoring_ctx(None) as progress_logger:
            progress_logger(0.0)
            file_uri = batch_source_spec.uri
            timestamp_field = batch_source_spec.timestamp_field

            proto_format = batch_source_spec.file_format
            if proto_format == batch_data_source_pb2.FILE_DATA_SOURCE_FORMAT_CSV:
                arrow_format = "csv"
            elif proto_format == batch_data_source_pb2.FILE_DATA_SOURCE_FORMAT_JSON:
                arrow_format = "json"
            elif proto_format == batch_data_source_pb2.FILE_DATA_SOURCE_FORMAT_PARQUET:
                arrow_format = "parquet"
            else:
                raise ValueError(batch_data_source_pb2.FileDataSourceFormat.Name(batch_source_spec.file_format))

            fs, path = pyarrow.fs.FileSystem.from_uri(file_uri)
            if isinstance(fs, pyarrow.fs.S3FileSystem):
                options = BotoOfflineStoreOptionsProvider.static_options()
                if options is not None:
                    fs = pyarrow.fs.S3FileSystem(
                        access_key=options.access_key_id,
                        secret_key=options.secret_access_key,
                        session_token=options.session_token,
                    )
            file_ds = pyarrow.dataset.dataset(source=path, filesystem=fs, format=arrow_format)
            relation = self.session.from_arrow(file_ds)
            if ds.start_time:
                relation = relation.filter(f"{timestamp_field} >= CAST('{ds.start_time}' AS TIMESTAMP)")
            if ds.end_time:
                relation = relation.filter(f"{timestamp_field} < CAST('{ds.end_time}' AS TIMESTAMP)")

            relation.create_view(table_name)
            progress_logger(1.0)
            self.created_views.append(table_name)

    def load_table(self, table_name: str) -> pyarrow.Table:
        return self.session.view(table_name).arrow()

    def run_odfv(self, qt_node: NodeRef, input_df: pd.DataFrame) -> pd.DataFrame:
        # TODO: leverage duckdb udfs
        pass

    def cleanup_temp_tables(self):
        for view in self.created_views:
            self.session.unregister(view)
        self.created_views = []
