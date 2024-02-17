import logging
import threading
import typing
from typing import Optional
from urllib.parse import urlparse

import attrs
import pandas as pd
import pyarrow
import snowflake.connector
import snowflake.snowpark
import sqlparse
from snowflake.connector import pandas_tools

from tecton_core import compute_mode
from tecton_core import conf
from tecton_core.errors import TectonValidationError
from tecton_core.query.dialect import Dialect
from tecton_core.query.errors import SQLCompilationError
from tecton_core.query.errors import UserDefinedTransformationError
from tecton_core.query.node_interface import NodeRef
from tecton_core.query.node_utils import get_batch_data_sources
from tecton_core.query.nodes import DataSourceScanNode
from tecton_core.query.query_tree_compute import QueryTreeCompute
from tecton_core.query.sql_compat import CompatFunctions
from tecton_core.schema import Schema
from tecton_core.schema_validation import tecton_schema_to_arrow_schema
from tecton_core.schema_validation import validate_schema_arrow_table
from tecton_core.secrets import SecretResolver
from tecton_core.snowflake_context import SnowflakeContext
from tecton_core.specs import SnowflakeSourceSpec
from tecton_core.time_utils import convert_pandas_df_for_snowflake_upload


_SNOWFLAKE_HOST_SUFFIX = ".snowflakecomputing.com"


def _get_single_field(sources: typing.List[SnowflakeSourceSpec], field_name: str) -> str:
    values = set()
    for spec in sources:
        field = getattr(spec, field_name)
        if field is None:
            msg = f"`{field_name}` field must be specified for a Snowflake data source"
            raise TectonValidationError(msg, can_drop_traceback=True)
        values.add(field)
    if len(values) != 1:
        msg = f"Conflicting values for `{field_name}` among Snowflake data sources: {values}"
        raise TectonValidationError(msg, can_drop_traceback=True)
    return values.pop()


@attrs.define
class SnowflakeCompute(QueryTreeCompute):
    connection: snowflake.connector.SnowflakeConnection
    lock: threading.RLock = threading.RLock()
    is_debug: bool = attrs.field(init=False)

    def __attrs_post_init__(self):
        self.is_debug = conf.get_bool("DUCKDB_DEBUG")

    @staticmethod
    def from_context() -> "SnowflakeCompute":
        return SnowflakeCompute(connection=SnowflakeContext.get_instance().get_connection())

    @staticmethod
    def for_connection(connection: snowflake.connector.SnowflakeConnection) -> "SnowflakeCompute":
        return SnowflakeCompute(connection=connection)

    @staticmethod
    def for_query_tree(root: NodeRef) -> "SnowflakeCompute":
        """Initializes a connection based on the warehouse/url specified in the batch sources in the tree, and the
        user/password from tecton.conf.
        """
        user = conf.get_or_none("SNOWFLAKE_USER")
        password = conf.get_or_none("SNOWFLAKE_PASSWORD")
        if not user or not password:
            msg = "Snowflake user and password not configured. Instructions at https://docs.tecton.ai/docs/setting-up-tecton/connecting-data-sources/connecting-to-a-snowflake-data-source-using-spark"
            raise TectonValidationError(msg, can_drop_traceback=True)

        snowflake_sources: typing.List[SnowflakeSourceSpec] = get_batch_data_sources(root, SnowflakeSourceSpec)

        url = _get_single_field(snowflake_sources, "url")
        host = urlparse(url).hostname
        if not host.endswith(_SNOWFLAKE_HOST_SUFFIX):
            msg = f"Snowflake URL host must end in {_SNOWFLAKE_HOST_SUFFIX}, but was {url}"
            raise TectonValidationError(msg, can_drop_traceback=True)
        account = host[: -len(_SNOWFLAKE_HOST_SUFFIX)]

        warehouse = _get_single_field(snowflake_sources, "warehouse")

        # The "database" parameter is not needed by the query itself,
        # but it's useful for error retrieval.
        # See `self.session.table_function("information_schema.query_history")` below.
        database = _get_single_field(snowflake_sources, "database")

        # Needed for register temp tables
        schema = _get_single_field(snowflake_sources, "schema")

        connection = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            warehouse=warehouse,
            schema=schema,
            database=database,
        )
        return SnowflakeCompute.for_connection(connection)

    def run_sql(
        self, sql_string: str, return_dataframe: bool = False, expected_output_schema: Optional[Schema] = None
    ) -> Optional[pyarrow.Table]:
        sql_string = sqlparse.format(sql_string, reindent=True)
        if self.is_debug:
            logging.warning(f"SNOWFLAKE QT: run SQL {sql_string}")

        with self.monitoring_ctx(sql_string) as progress_logger:
            progress_logger(0.0)
            cursor = self.connection.cursor()
            cursor.execute("ALTER SESSION SET TIMEZONE = 'UTC'")
            try:
                cursor.execute(sql_string)
            except snowflake.connector.DatabaseError as exc:
                if "SQL compilation error" in exc.msg:
                    raise SQLCompilationError(exc.msg.replace("\n", " "), sql_string) from None

                msg = f"Snowflake query failed with: {exc.msg}"
                raise UserDefinedTransformationError(msg) from None

            if not return_dataframe:
                progress_logger(1.0)
                return

            table = cursor.fetch_arrow_all()
            progress_logger(1.0)

            if table is None:
                if not expected_output_schema:
                    msg = "An expected output schema is required to cast an empty dataframe."
                    raise RuntimeError(msg)
                schema = tecton_schema_to_arrow_schema(expected_output_schema)
                return pyarrow.Table.from_pylist([], schema=schema)

            output = self._post_process(table)
            if expected_output_schema:
                diff = validate_schema_arrow_table(table=output, schema=expected_output_schema)
                if diff:
                    msg = "Result from Snowflake transformation does not match expected schema.\n"
                    msg += diff.as_str()
                    raise TectonValidationError(msg, can_drop_traceback=True)

                # Cast to fix some small discrepancies, ie snowflake returns int16 instead of int32.
                # If output passed the validation above we don't expect any other changes
                output = output.cast(tecton_schema_to_arrow_schema(expected_output_schema))

            return output

    @staticmethod
    def _post_process(table: pyarrow.Table) -> pyarrow.Table:
        """Fixes Snowflake output before it can be returned"""

        def unquote(field_name: str) -> str:
            """If a column name was quoted, remove the enclosing quotes. Otherwise, return the original column name.

            The Snowpark schema may contain either quoted or unquoted identifiers. In general, Unified Tecton uses
            quoted identifiers. However, certain queries (e.g. a data source scan) do a SELECT *, which results
            in unquoted identifiers. The Pandas dataframe will not have quoted identifiers, and so sometimes need
            to strip the surrounding double quotes.

            NOTE: that an unquoted column name cannot contain double quotes, so it is safe to return the original
            column name if it is not wrapped in double quotes.
            See https://docs.snowflake.com/en/sql-reference/identifiers-syntax for more details.

            NOTE: The condition (field_name[0] == field_name[-1] == '"') is not actually accurate.
            For example if a user has a column that starts and ends with a double quote, and we do a SELECT *, that column will be returned as an unquoted
            identifier. However, this condition will mistakenly consider it a quoted identifier and strip the
            surrounding double quotes, which is wrong. In order to correctly address this, we would need to
            know whether the identifier was quoted or unquoted. However, this case is sufficiently rare that
            we will ignore it for now.

            """
            return field_name[1:-1] if field_name[0] == field_name[-1] == '"' else field_name

        schema_w_unquoted_names = pyarrow.schema([field.with_name(unquote(field.name)) for field in table.schema])

        return table.cast(schema_w_unquoted_names)

    def get_dialect(self) -> Dialect:
        return Dialect.SNOWFLAKE

    def run_odfv(self, qt_node: NodeRef, input_df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError

    def register_temp_table_from_pandas(self, table_name: str, pandas_df: pd.DataFrame) -> None:
        # Not quoting identifiers / keeping the upload case-insensitive to be consistent with the query tree sql
        # generation logic, which is also case-insensitive. (i.e. will upper case selected fields).
        df_to_write = pandas_df.copy()
        convert_pandas_df_for_snowflake_upload(df_to_write)
        pandas_tools.write_pandas(
            conn=self.connection,
            df=df_to_write,
            table_name=table_name,
            auto_create_table=True,
            table_type="temporary",
            quote_identifiers=compute_mode.offline_retrieval_compute_mode(None) != compute_mode.ComputeMode.SNOWFLAKE,
            overwrite=True,
        )

    def register_temp_table(self, table_name: str, pa_table: pyarrow.Table) -> None:
        types_mapper = {pyarrow.int64(): pd.Int64Dtype()}
        self.register_temp_table_from_pandas(table_name, pa_table.to_pandas(types_mapper=types_mapper.get))

    def register_temp_table_from_data_source(
        self, table_name: str, ds: DataSourceScanNode, secret_resolver: Optional[SecretResolver]
    ) -> None:
        assert isinstance(
            ds.ds.batch_source, SnowflakeSourceSpec
        ), "Snowflake compute supports only Snowflake data sources"

        self.run_sql(f'CREATE OR REPLACE TEMP VIEW "{table_name}" AS ({ds.with_dialect(Dialect.SNOWFLAKE).to_sql()})')

    def load_table(self, table_name: str) -> pyarrow.Table:
        return self.run_sql(
            CompatFunctions.for_dialect(Dialect.SNOWFLAKE).query().from_(table_name).select("*").get_sql(),
            return_dataframe=True,
        )
