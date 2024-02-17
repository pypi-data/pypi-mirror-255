import contextlib
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict
from typing import Iterable
from typing import Iterator
from typing import Optional
from typing import Tuple

import attrs
import pandas as pd
import pyarrow

from tecton_core import conf
from tecton_core.offline_store import OfflineStoreOptionsProvider
from tecton_core.query.dialect import Dialect
from tecton_core.query.duckdb.rewrite import DuckDBTreeRewriter
from tecton_core.query.executor_params import QueryTreeStep
from tecton_core.query.executor_utils import detect_interactive_shell
from tecton_core.query.executor_utils import display_timer
from tecton_core.query.node_interface import NodeRef
from tecton_core.query.node_interface import QueryNode
from tecton_core.query.node_interface import recurse_query_tree
from tecton_core.query.node_utils import get_first_input_node_of_class
from tecton_core.query.node_utils import get_pipeline_dialect
from tecton_core.query.node_utils import get_staging_nodes
from tecton_core.query.nodes import DataSourceScanNode
from tecton_core.query.nodes import MockDataSourceScanNode
from tecton_core.query.nodes import MultiOdfvPipelineNode
from tecton_core.query.nodes import OfflineStoreScanNode
from tecton_core.query.nodes import StagedTableScanNode
from tecton_core.query.nodes import StagingNode
from tecton_core.query.nodes import UserSpecifiedDataNode
from tecton_core.query.pandas.rewrite import OfflineScanTreeRewriter
from tecton_core.query.pandas.rewrite import PandasTreeRewriter
from tecton_core.query.query_tree_compute import QueryTreeCompute
from tecton_core.secrets import SecretResolver


logger = logging.getLogger(__name__)


def _pyarrow_type_contains_map_type(pyarrow_type: pyarrow.DataType) -> bool:
    if isinstance(pyarrow_type, pyarrow.MapType):
        return True
    elif isinstance(pyarrow_type, pyarrow.StructType):
        return any(_pyarrow_type_contains_map_type(field.type) for field in pyarrow_type)
    elif isinstance(pyarrow_type, pyarrow.ListType):
        return _pyarrow_type_contains_map_type(pyarrow_type.value_type)
    return False


@dataclass
class QueryTreeOutput:
    # Maps table name to pyarrow table containing a data source
    data_source_tables: Dict[str, pyarrow.Table]
    # Maps table name to pyarrow table containing a feature view
    feature_view_tables: Dict[str, pyarrow.Table]
    odfv_input: Optional[pyarrow.Table] = None
    odfv_output: Optional[pd.DataFrame] = None

    @property
    def result_df(self) -> pd.DataFrame:
        if self.odfv_output is not None:
            return self.odfv_output
        assert self.odfv_input is not None

        contains_map_type = any(_pyarrow_type_contains_map_type(field.type) for field in self.odfv_input.schema)
        if contains_map_type:
            # The `maps_as_pydicts` parameter for pyarrow.Table.to_pandas is only supported starting in pyarrow 13.0.0.
            if pyarrow.__version__ < "13.0.0":
                msg = f"Rift requires pyarrow>=13.0.0 to perform feature retrieval for Map features. You have version {pyarrow.__version__}."
                raise RuntimeError(msg)
            return self.odfv_input.to_pandas(maps_as_pydicts="strict")

        return self.odfv_input.to_pandas()

    @property
    def result_table(self) -> pyarrow.Table:
        assert self.odfv_output is None, "Can't retrieve ODFV output as a pyarrow table"
        return self.odfv_input


@attrs.define
class QueryTreeExecutor:
    data_source_compute: QueryTreeCompute
    pipeline_compute: QueryTreeCompute
    agg_compute: QueryTreeCompute
    # TODO(danny): Consider separating aggregation from AsOfJoin, so we can process sub nodes and delete old
    #  tables in duckdb when doing `from_source=True`
    odfv_compute: QueryTreeCompute
    offline_store_options_providers: Iterable[OfflineStoreOptionsProvider]
    is_debug: bool = attrs.field(init=False)
    is_inside_interactive_shell: bool = attrs.field(init=False)
    # Used to track temp tables per dialect so we can clean them up appropriately & avoid re-registering duplicates
    _dialect_to_temp_table_name: Optional[Dict[Dialect, set]] = attrs.field(init=False)

    def __attrs_post_init__(self):
        # TODO(danny): Expose as configs
        self.is_debug = conf.get_bool("DUCKDB_DEBUG")
        self.is_inside_interactive_shell = detect_interactive_shell()
        self._dialect_to_temp_table_name = None

    @contextlib.contextmanager
    def _measure_stage(self, step: str, node: NodeRef) -> Iterator[None]:
        start_time = datetime.now()
        if self.is_debug:
            logger.warning(f"------------- Executing stage: {step} -------------")
            logger.warning(f"QT: \n{node.pretty_str(description=False)}")

            def stop_clock():
                stage_done_time = datetime.now()
                logger.warning(f"{step} took time (sec): {(stage_done_time - start_time).total_seconds()}")

        elif self.is_inside_interactive_shell:
            stop_clock = display_timer(f"---- Executing stage: {step:<50} {{clock}}")
        else:

            def stop_clock():
                pass

        try:
            yield
        finally:
            stop_clock()

    def exec_qt(self, qt_root: NodeRef, secret_resolver: Optional[SecretResolver]) -> QueryTreeOutput:
        # Make copy so the execution doesn't mutate the original QT visible to users
        qt_root = qt_root.deepcopy()
        try:
            if self.is_debug:
                logger.warning(
                    "---------------------------------- Executing overall QT ----------------------------------"
                )
                logger.warning(f"QT: \n{qt_root.pretty_str(columns=True)}")

            if get_first_input_node_of_class(qt_root, OfflineStoreScanNode) is not None:
                with self._measure_stage("Reading offline store", qt_root):
                    rewriter = OfflineScanTreeRewriter(options_providers=self.offline_store_options_providers)
                    rewriter.rewrite(qt_root, self.pipeline_compute)

                # StagingNodes are present in only two scenarios. First, a materialization querytree is required,
                # i.e. materialization or from_source=True retrieval. Second, an ODFV is present. Thus during
                # from_source=False retrieval, i.e. when an OfflineStoreScanNode is present, a StagingNode will exist
                # if and only if an ODFV is present. If no StagingNode is present, the below logic might not execute the
                # querytree, so we immediately execute it here.
                if get_first_input_node_of_class(qt_root, StagingNode) is None:
                    with self._measure_stage("Evaluating consolidating query", qt_root):
                        self._maybe_register_temp_tables(qt_root=qt_root, compute=self.pipeline_compute)
                        table = self.pipeline_compute.run_sql(qt_root.to_sql(), return_dataframe=True)
                    return QueryTreeOutput(
                        data_source_tables={},
                        feature_view_tables={},
                        odfv_input=table,
                    )

            output = self._execute_data_source_step(qt_root, secret_resolver)
            rewriter = DuckDBTreeRewriter()
            rewriter.rewrite(qt_root, QueryTreeStep.DATA_SOURCE)

            # This can only happen if the initial query tree was a single DataSourceScanNode followed by a
            # StagingNode. In that case, we can skip the rest of the query tree.
            if len(output.data_source_tables) == 1 and isinstance(qt_root.node, StagedTableScanNode):
                table_name, pa_table = output.data_source_tables.popitem()
                pa_table = pa_table or self.data_source_compute.load_table(table_name)
                return QueryTreeOutput(data_source_tables={}, feature_view_tables={}, odfv_input=pa_table)

            # Executes the feature view pipeline and stages into memory or S3
            output = self._execute_pipeline_step(output, qt_root)
            rewriter = DuckDBTreeRewriter()
            rewriter.rewrite(qt_root, QueryTreeStep.PIPELINE)

            # Does partial aggregations (if applicable) and spine joins
            qt_root.node = qt_root.node.with_dialect(Dialect.DUCKDB)
            output = self._execute_agg_step(output, qt_root)
            rewriter = DuckDBTreeRewriter()
            rewriter.rewrite(qt_root, QueryTreeStep.AGGREGATION)

            # Runs ODFVs (if applicable)
            output = self._execute_odfv_step(output, qt_root)
            return output
        finally:
            self.pipeline_compute.cleanup_temp_tables()
            self.agg_compute.cleanup_temp_tables()
            self.odfv_compute.cleanup_temp_tables()

    def _execute_data_source_step(self, qt_root: NodeRef, secret_resolver: Optional[SecretResolver]) -> QueryTreeOutput:
        with self._measure_stage("Reading Data Sources", qt_root):
            staging_nodes_to_process = get_staging_nodes(qt_root, QueryTreeStep.DATA_SOURCE)
            if len(staging_nodes_to_process) == 0:
                # This is possible if, for example, the querytree is reading from the offline store instead from a data source.
                return QueryTreeOutput(data_source_tables={}, feature_view_tables={})
            data_source_tables = {}
            for name, staging_node in staging_nodes_to_process.items():
                data_source_node_ref = staging_node.input_node
                data_source_node = data_source_node_ref.node
                assert isinstance(data_source_node, (DataSourceScanNode, MockDataSourceScanNode))

                if not isinstance(data_source_node, MockDataSourceScanNode):
                    self.data_source_compute.register_temp_table_from_data_source(
                        name, data_source_node, secret_resolver
                    )
                    if (
                        self.data_source_compute == self.pipeline_compute
                        and self.pipeline_compute.get_dialect() not in (Dialect.PANDAS, Dialect.DUCKDB)
                    ):
                        # No need to export from compute, it will be shared between stages
                        output_pa = None
                    else:
                        output_pa = self.data_source_compute.load_table(name)
                else:
                    self._maybe_register_temp_tables(qt_root=qt_root, compute=self.data_source_compute)
                    output_pa = self.data_source_compute.run_sql(data_source_node.to_sql(), return_dataframe=True)
                data_source_tables[name] = output_pa
            return QueryTreeOutput(data_source_tables=data_source_tables, feature_view_tables={})

    def _execute_pipeline_step(self, output: QueryTreeOutput, qt_node: NodeRef) -> QueryTreeOutput:
        with self._measure_stage("Evaluating Feature View pipelines", qt_node):
            for table_name, pa_table in output.data_source_tables.items():
                if not pa_table:
                    # assuming that we're sharing computes and table is already loaded
                    continue

                if self.is_debug:
                    logger.warning(
                        f"Registering staged table {table_name} to pipeline compute with schema:\n{pa_table.schema}"
                    )
                self.pipeline_compute.register_temp_table(table_name, pa_table)

            pipeline_dialect = get_pipeline_dialect(qt_node)
            if pipeline_dialect == Dialect.PANDAS:
                pd_rewrite_start = datetime.now()
                rewriter = PandasTreeRewriter()
                rewriter.rewrite(qt_node, self.pipeline_compute, output.data_source_tables)
                if self.is_debug:
                    logger.warning(f"PANDAS PRE INIT: \n{qt_node.pretty_str(description=False)}")

            self._maybe_register_temp_tables(qt_root=qt_node, compute=self.pipeline_compute)

            # For STAGING: concurrently stage nodes matching the QueryTreeStep.PIPELINE filter
            staging_nodes_to_process = get_staging_nodes(qt_node, QueryTreeStep.PIPELINE)
            if len(staging_nodes_to_process) == 0:
                # This is possible if, for example, the querytree contains only ODFVs that do not depend on any feature views.
                return QueryTreeOutput(data_source_tables={}, feature_view_tables={})
            feature_view_tables = self._stage_tables_and_load_pa(
                nodes_to_process=staging_nodes_to_process,
                compute=self.pipeline_compute,
            )
            return QueryTreeOutput(data_source_tables={}, feature_view_tables=feature_view_tables)

    def _execute_agg_step(self, output: QueryTreeOutput, qt_node: NodeRef) -> QueryTreeOutput:
        with self._measure_stage("Computing aggregated features & joining results", qt_node):
            # The AsOfJoins need access to a spine, which are registered here.
            self._maybe_register_temp_tables(qt_root=qt_node, compute=self.agg_compute)

            # Register staged pyarrow tables in agg compute
            for table_name, pa_table in output.feature_view_tables.items():
                if self.is_debug:
                    logger.warning(
                        f"Registering staged table {table_name} to agg compute with schema:\n{pa_table.schema}"
                    )
                self.agg_compute.register_temp_table(table_name, pa_table)

            return self._process_agg_join(output, self.agg_compute, qt_node)

    def _execute_odfv_step(self, prev_step_output: QueryTreeOutput, qt_node: NodeRef) -> QueryTreeOutput:
        assert prev_step_output
        assert prev_step_output.odfv_input is not None
        has_odfvs = get_first_input_node_of_class(qt_node, node_class=MultiOdfvPipelineNode) is not None
        if has_odfvs:
            # TODO(meastham): Use pyarrow typemapper after upgrading pandas
            with self._measure_stage("Evaluating On-Demand Feature Views", qt_node):
                output_df = self.odfv_compute.run_odfv(qt_node, prev_step_output.odfv_input.to_pandas())
        else:
            output_df = None
        return QueryTreeOutput(
            data_source_tables={},
            feature_view_tables=prev_step_output.feature_view_tables,
            odfv_input=prev_step_output.odfv_input,
            odfv_output=output_df,
        )

    def _process_agg_join(
        self, output: QueryTreeOutput, compute: QueryTreeCompute, qt_node: NodeRef
    ) -> QueryTreeOutput:
        # TODO(danny): change the "stage" in the StagingNode to be more for the destination stage
        staging_nodes_to_process = get_staging_nodes(qt_node, QueryTreeStep.AGGREGATION)

        if len(staging_nodes_to_process) > 0:
            # There should be a single StagingNode. It is either there for materialization or ODFVs.
            assert len(staging_nodes_to_process) == 1
            tables = self._stage_tables_and_load_pa(
                nodes_to_process=staging_nodes_to_process,
                compute=self.agg_compute,
            )
            assert len(tables) == 1
            pa_table = next(iter(tables.values()))
            return QueryTreeOutput(
                data_source_tables={}, feature_view_tables=output.feature_view_tables, odfv_input=pa_table
            )

        # There are no StagingNodes, so we can execute the remainder of the query tree.
        output_df_pa = compute.run_sql(qt_node.to_sql(), return_dataframe=True)
        return QueryTreeOutput(
            data_source_tables={}, feature_view_tables=output.feature_view_tables, odfv_input=output_df_pa
        )

    def _stage_tables_and_load_pa(
        self,
        nodes_to_process: Dict[str, QueryNode],
        compute: QueryTreeCompute,
    ) -> Dict[str, pyarrow.Table]:
        tables = {}
        for _, node in nodes_to_process.items():
            if isinstance(node, StagingNode):
                name, table = self._process_staging_node(node, compute)
                tables[name] = table
        return tables

    def _process_staging_node(self, qt_node: StagingNode, compute: QueryTreeCompute) -> Tuple[str, pyarrow.Table]:
        start_time = datetime.now()
        staging_table_name = qt_node.staging_table_name_unique()
        sql_string = qt_node.with_dialect(compute.get_dialect())._to_staging_query_sql()
        memory_table = compute.run_sql(sql_string, return_dataframe=True, expected_output_schema=qt_node.output_schema)
        staging_done_time = datetime.now()
        if self.is_debug:
            elapsed_staging_time = (staging_done_time - start_time).total_seconds()
            logger.warning(f"STAGE_{staging_table_name}_TIME_SEC: {elapsed_staging_time}")

        return staging_table_name, memory_table

    def _maybe_register_temp_tables(self, qt_root: NodeRef, compute: QueryTreeCompute) -> None:
        self._dialect_to_temp_table_name = self._dialect_to_temp_table_name or {}

        dialect = compute.get_dialect()
        if dialect not in self._dialect_to_temp_table_name:
            self._dialect_to_temp_table_name[dialect] = set()

        def maybe_register_temp_table(node):
            if isinstance(node, UserSpecifiedDataNode):
                tmp_table_name = node.data._temp_table_name
                if tmp_table_name in self._dialect_to_temp_table_name[dialect]:
                    return
                df = node.data.to_pandas()
                if self.is_debug:
                    logger.warning(
                        f"Registering user specified data {tmp_table_name} to {compute.get_dialect()} with schema:\n{df.dtypes}"
                    )
                compute.register_temp_table_from_pandas(tmp_table_name, df)
                self._dialect_to_temp_table_name[dialect].add(tmp_table_name)

        recurse_query_tree(
            qt_root,
            maybe_register_temp_table,
        )
