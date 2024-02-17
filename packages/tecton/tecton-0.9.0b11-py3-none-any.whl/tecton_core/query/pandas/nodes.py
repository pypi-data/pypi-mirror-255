import itertools
import logging
import typing
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import attrs
import pandas
import pendulum
import pyarrow

from tecton_core import feature_set_config
from tecton_core import specs
from tecton_core.arrow import arrow_table_to_pandas_dataframe
from tecton_core.data_types import BoolType
from tecton_core.data_types import Float32Type
from tecton_core.data_types import Float64Type
from tecton_core.data_types import Int32Type
from tecton_core.data_types import Int64Type
from tecton_core.data_types import StringType
from tecton_core.data_types import TimestampType
from tecton_core.errors import TectonValidationError
from tecton_core.feature_definition_wrapper import FeatureDefinitionWrapper
from tecton_core.filter_context import FilterContext
from tecton_core.id_helper import IdHelper
from tecton_core.materialization_context import BoundMaterializationContext
from tecton_core.query.errors import UserCodeError
from tecton_core.query.node_interface import NodeRef
from tecton_core.query.pandas import pipeline_helper
from tecton_core.query.pandas.node import PandasExecNode
from tecton_core.query.pandas.node import SqlExecNode
from tecton_core.schema import Schema
from tecton_core.schema_validation import tecton_schema_to_arrow_schema
from tecton_core.schema_validation import validate_schema_arrow_table
from tecton_core.schema_validation import validate_schema_pandas_df
from tecton_proto.args.pipeline_pb2 import DataSourceNode
from tecton_proto.args.pipeline_pb2 import PipelineNode
from tecton_proto.args.pipeline_pb2 import TransformationNode
from tecton_proto.args.transformation_pb2 import TransformationMode
from tecton_proto.common.data_source_type_pb2 import DataSourceType


logger = logging.getLogger(__name__)

# Maps a tecton datatype to the correct pandas datatype which is to be used when an output schema is defined by the user
PRIMITIVE_TECTON_DATA_TYPE_TO_PANDAS_DATA_TYPE = {
    Int32Type(): "int32",
    Int64Type(): "int64",
    Float32Type(): "float32",
    Float64Type(): "float64",
    StringType(): "string",
    BoolType(): "bool",
    TimestampType(): "datetime64[ns]",
}


@attrs.frozen
class PandasDataSourceScanNode(PandasExecNode):
    ds: specs.DataSourceSpec
    ds_node: Optional[DataSourceNode]
    is_stream: bool = attrs.field()
    start_time: Optional[datetime]
    end_time: Optional[datetime]

    def _to_dataframe(self) -> pandas.DataFrame:
        batch_source = self.ds.batch_source
        assert isinstance(batch_source, specs.PandasBatchSourceSpec)

        df = self._get_ds_from_dsf(batch_source, self.ds.name)

        if self.ds.type == DataSourceType.STREAM_WITH_BATCH:
            schema = self.ds.stream_source.spark_schema
            cols = [field.name for field in schema.fields]
            df = df[cols]
        elif self.ds.type == DataSourceType.PUSH_WITH_BATCH:
            schema = self.ds.schema.tecton_schema
            cols = [field.name for field in schema.columns]
            df = df[cols]
        return df

    def _get_ds_from_dsf(self, batch_source: specs.PandasBatchSourceSpec, data_source_name: str) -> pandas.DataFrame:
        function_args = {}
        if batch_source.supports_time_filtering:
            function_args["filter_context"] = FilterContext(self.start_time, self.end_time)
        if batch_source.secrets:
            if self.secret_resolver is None:
                msg = "No secret resolver was provided. For Local Development, please set secrets to string literals."
                raise TectonValidationError(msg)
            function_args["secrets"] = self.secret_resolver.resolve(batch_source.secrets)
        try:
            ret = batch_source.function(**function_args)
        except Exception as exc:
            msg = f"Evaluating Pandas data source '{data_source_name}' failed with exception."
            raise UserCodeError(msg) from exc

        if not isinstance(ret, pandas.DataFrame):
            msg = (
                f"The function of Pandas data source '{data_source_name}' is expected to return result "
                f"with Pandas DataFrame type, but returned result with type {type(ret)} instead."
            )
            raise TectonValidationError(msg, can_drop_traceback=True)

        return ret


@attrs.frozen
class PandasFeatureViewPipelineNode(PandasExecNode):
    inputs_map: Dict[str, NodeRef]
    feature_definition_wrapper: FeatureDefinitionWrapper
    feature_time_limits: Optional[pendulum.Period]

    # `check_view_schema` is not actually used in pandas node. Having it here to keep all QT node can be intialized consistently.
    check_view_schema: bool

    def to_arrow(self) -> pyarrow.Table:
        table = self._node_to_value(self.feature_definition_wrapper.pipeline.root)
        return table

    def _to_dataframe(self):
        return self.to_arrow().to_pandas()

    def _node_to_value(self, pipeline_node: PipelineNode) -> Union[pyarrow.Table, BoundMaterializationContext]:
        if pipeline_node.HasField("transformation_node"):
            return self._transformation_node_to_dataframe(pipeline_node.transformation_node)
        elif pipeline_node.HasField("data_source_node"):
            ds_query_node = self.inputs_map[pipeline_node.data_source_node.input_name].node
            assert isinstance(
                ds_query_node, PandasDataNode
            ), "A PandasFeatureViewPipelineNode cannot operate on standard DataSourceScanNodes. They must have been replaced by PandasDataNodes."
            return ds_query_node.to_arrow()
        elif pipeline_node.HasField("materialization_context_node"):
            return BoundMaterializationContext.create(self.feature_time_limits.start, self.feature_time_limits.end)
        else:
            msg = f"Pipeline node of kind {pipeline_node.WhichOneof('node_type')} is not supported in Pandas mode"
            raise NotImplementedError(msg)

    def _transformation_node_to_dataframe(self, transformation_node: TransformationNode) -> pyarrow.Table:
        """Recursively translates inputs to values and then passes them to the transformation."""
        args: List[Any] = []
        kwargs = {}
        id_to_transformation = {t.id: t for t in self.feature_definition_wrapper.transformations}
        transformation = id_to_transformation[IdHelper.to_string(transformation_node.transformation_id)]
        user_function = transformation.user_function
        for transformation_input in transformation_node.inputs:
            node_value = self._node_to_value(transformation_input.node)
            if transformation_input.HasField("arg_index"):
                assert len(args) == transformation_input.arg_index
                args.append(node_value)
            elif transformation_input.HasField("arg_name"):
                kwargs[transformation_input.arg_name] = node_value
            else:
                msg = f"Unknown argument type for Input node: {transformation_input}"
                raise KeyError(msg)

        if transformation.transformation_mode == TransformationMode.TRANSFORMATION_MODE_PANDAS:
            return self._call_pandas_udf_and_verify_result(
                user_function, args, kwargs, self.feature_definition_wrapper.view_schema
            )

        if transformation.transformation_mode == TransformationMode.TRANSFORMATION_MODE_PYTHON:
            return self._call_python_udf_and_verify_result(
                user_function, args, kwargs, self.feature_definition_wrapper.view_schema
            )

        msg = (
            f"Unknown transformation mode {transformation.transformation_mode} "
            f"in feature view {self.feature_definition_wrapper.fv_spec.name}"
        )
        raise TectonValidationError(msg)

    def _call_pandas_udf_and_verify_result(
        self,
        user_function: typing.Callable,
        args: List[Any],
        kwargs: Dict[str, Any],
        expected_schema: Schema,
    ) -> pyarrow.Table:
        args = [arrow_table_to_pandas_dataframe(arg) if isinstance(arg, pyarrow.Table) else arg for arg in args]
        kwargs = {
            key: arrow_table_to_pandas_dataframe(arg) if isinstance(arg, pyarrow.Table) else arg
            for key, arg in kwargs.items()
        }

        try:
            ret = user_function(*args, **kwargs)
        except Exception as exc:
            msg = (
                "Pandas pipeline function (feature view "
                f"'{self.feature_definition_wrapper.fv_spec.name}') "
                f"failed with exception"
            )
            raise UserCodeError(msg) from exc

        if not isinstance(ret, pandas.DataFrame):
            msg = (
                f"Pandas pipeline function (feature view '{self.feature_definition_wrapper.fv_spec.name}') is expected "
                f"to return result with Pandas DataFrame type, but returned result with type {type(ret)} instead."
            )
            raise TectonValidationError(msg, can_drop_traceback=True)

        validation_msg = (
            f"Result from pipeline function (feature view '{self.feature_definition_wrapper.fv_spec.name}') "
            "does not match expected schema.\n"
        )

        # We don't check struct fields order at this point, since it will most probably be incorrect.
        # Instead, we will try to cast pandas dataframe to expected schema and fix the order there.
        diff = validate_schema_pandas_df(ret, expected_schema, strict_struct_order=False)
        if diff:
            validation_msg += diff.as_str()
            raise TectonValidationError(validation_msg, can_drop_traceback=True)

        try:
            table = pyarrow.Table.from_pandas(ret, schema=tecton_schema_to_arrow_schema(expected_schema))
        except pyarrow.lib.ArrowInvalid as exc:
            validation_msg += "\n".join(exc.args)
            raise TectonValidationError(validation_msg, can_drop_traceback=True)
        else:
            return table

    def _call_python_udf_and_verify_result(
        self,
        user_function: typing.Callable,
        args: List[Any],
        kwargs: Dict[str, Any],
        expected_schema: Schema,
    ) -> pyarrow.Table:
        args_it = itertools.product(*[arg.to_pylist() if isinstance(arg, pyarrow.Table) else [arg] for arg in args])
        kwargs_it = itertools.product(
            *[arg.to_pylist() if isinstance(arg, pyarrow.Table) else [arg] for arg in kwargs.values()]
        )

        try:
            ret = [
                user_function(*args, **dict(zip(kwargs.keys(), kwargs_values)))
                for args, kwargs_values in itertools.product(args_it, kwargs_it)
            ]
        except Exception as exc:
            msg = (
                "Python pipeline function (feature view "
                f"'{self.feature_definition_wrapper.fv_spec.name}') "
                f"failed with exception"
            )
            raise UserCodeError(msg) from exc

        if any(not isinstance(item, dict) for item in ret):
            other_type = next(type(item) for item in ret if not isinstance(item, dict))
            msg = (
                f"Python pipeline function (feature view '{self.feature_definition_wrapper.fv_spec.name}') is expected "
                f"to return a Python dict, but returned result with type {other_type} instead."
            )
            raise TectonValidationError(msg, can_drop_traceback=True)

        validation_msg = (
            f"Result from pipeline function (feature view '{self.feature_definition_wrapper.fv_spec.name}') "
            "does not match expected schema.\n"
        )

        try:
            table = pyarrow.Table.from_pylist(ret, schema=tecton_schema_to_arrow_schema(expected_schema))
        except (pyarrow.lib.ArrowInvalid, pyarrow.lib.ArrowTypeError) as exc:
            diff = validate_schema_arrow_table(
                pyarrow.Table.from_pylist(ret), expected_schema, strict_struct_order=False
            )
            if diff:
                validation_msg += diff.as_str()
            else:
                validation_msg += "\n".join(exc.args)
            raise TectonValidationError(validation_msg, can_drop_traceback=True) from None
        else:
            return table


@attrs.frozen
class PandasDataNode(PandasExecNode):
    input_table: pyarrow.Table

    def to_arrow(self):
        return self.input_table

    def _to_dataframe(self):
        return self.to_arrow().to_pandas()


@attrs.frozen
class PandasMultiOdfvPipelineNode(PandasExecNode):
    input_node: Union[PandasExecNode, SqlExecNode]
    feature_definition_wrappers_namespaces: List[Tuple[FeatureDefinitionWrapper, str]]
    use_namespace_feature_prefix: bool

    def _to_dataframe(self):
        if isinstance(self.input_node, PandasExecNode):
            output_df = arrow_table_to_pandas_dataframe(self.input_node.to_arrow())
        else:
            output_df = self.input_node._to_dataframe()
        # Apply each ODFV sequentially. Note that attempting to apply ODFV
        # udfs in parallel as we traverse data rows does not meaningfully
        # speed up execution on Athena (unlike in Spark).
        for fdw, namespace in self.feature_definition_wrappers_namespaces:
            output_df = self._get_odfv_output_df(output_df, fdw, namespace)
        return output_df

    def _get_odfv_output_df(
        self, input_df: pandas.DataFrame, fdw: FeatureDefinitionWrapper, namespace: str
    ) -> pandas.DataFrame:
        odfv_result_df = self._run_odfv(input_df, fdw)
        rename_map = {}
        datatypes = {}
        # Namespace ODFV outputs to this FV to avoid conflicts in output schemas
        # with other FV
        output_schema = fdw.view_schema.column_name_and_data_types()
        for column_name, datatype in output_schema:
            if self.use_namespace_feature_prefix:
                mapped_name = self.column_name_updater(f"{namespace}{fdw.namespace_separator}{column_name}")
            else:
                mapped_name = column_name
            rename_map[column_name] = mapped_name
            if datatype in PRIMITIVE_TECTON_DATA_TYPE_TO_PANDAS_DATA_TYPE:
                datatypes[mapped_name] = PRIMITIVE_TECTON_DATA_TYPE_TO_PANDAS_DATA_TYPE[datatype]
        odfv_result_df = odfv_result_df.rename(columns=rename_map)[[*rename_map.values()]].astype(datatypes)
        data_df = input_df.merge(odfv_result_df, left_index=True, right_index=True)
        return data_df

    def _run_odfv(self, data_df: pandas.DataFrame, odfv: FeatureDefinitionWrapper) -> pandas.DataFrame:
        transformation_mode = odfv.transformations[0].transformation_mode

        odfv_pipeline = pipeline_helper.build_odfv_execution_pipeline(
            pipeline=odfv.pipeline, transformations=odfv.transformations, name=odfv.name
        )

        odfv_transformation_node = odfv.pipeline.root.transformation_node
        odfv_inputs = self._extract_inputs_for_odfv_from_data(
            transformation_node=odfv_transformation_node, data_df=data_df, odfv_invocation_inputs={}, odfv=odfv
        )

        if transformation_mode == TransformationMode.TRANSFORMATION_MODE_PANDAS:
            odfv_result_df = odfv_pipeline.execute_with_inputs(odfv_inputs)
            return odfv_result_df
        elif transformation_mode == TransformationMode.TRANSFORMATION_MODE_PYTHON:
            # The inputs are currently a mapping of input_name to pandas DF
            # We need turn the ODFV inputs from a pandas DF to a list of dictionaries
            # Then we need to iterate through all rows of the input data set, pass the input dicts into the ODFV
            # And finally convert the resulting list of dicts into a pandas DF
            for input_name in odfv_inputs.keys():
                # Map pandas DFs to List of dicts (one dict per row)
                odfv_inputs[input_name] = odfv_inputs[input_name].to_dict("records")

            odfv_result_list = []

            for row_index in range(len(data_df)):
                # Iterate through all rows of the data and invoke the ODFV
                row_odfv_inputs = {}
                for input_name in odfv_inputs.keys():
                    row_odfv_inputs[input_name] = odfv_inputs[input_name][row_index]

                odfv_result_dict = odfv_pipeline.execute_with_inputs(row_odfv_inputs)
                odfv_result_list.append(odfv_result_dict)
            return pandas.DataFrame.from_dict(odfv_result_list)
        else:
            msg = f"ODFV {odfv.name} has an unexpected transformation mode: {transformation_mode}"
            raise TectonValidationError(msg)

    def _extract_inputs_for_odfv_from_data(
        self,
        transformation_node: TransformationNode,
        data_df: pandas.DataFrame,
        odfv_invocation_inputs: Dict[str, pandas.DataFrame],
        odfv: FeatureDefinitionWrapper,
    ) -> Dict[str, pandas.DataFrame]:
        for input in transformation_node.inputs:
            if input.node.HasField("request_data_source_node"):
                input_name = input.node.request_data_source_node.input_name
                request_context_schema = input.node.request_data_source_node.request_context.tecton_schema
                request_context_fields = [self.column_name_updater(c.name) for c in request_context_schema.columns]

                for f in request_context_fields:
                    if f not in data_df.columns:
                        msg = f"ODFV {odfv.name} has a dependency on the Request Data Source named '{input_name}'. Field {f} of this Request Data Source is not found in the spine. Available columns: {list(data_df.columns)}"
                        raise TectonValidationError(msg)

                input_df = data_df[request_context_fields]
                odfv_invocation_inputs[input_name] = input_df
            elif input.node.HasField("feature_view_node"):
                input_name = input.node.feature_view_node.input_name
                fv_features = feature_set_config.find_dependent_feature_set_items(
                    odfv.fco_container, input.node, {}, odfv.id
                )[0]
                # Generate dependent column mappings since dependent FV have
                # internal column names with _udf_internal
                select_columns_and_rename_map = {}
                for f in fv_features.features:
                    column_name = self.column_name_updater(f"{fv_features.namespace}__{f}")
                    mapped_name = self.column_name_updater(f)
                    select_columns_and_rename_map[column_name] = mapped_name
                for f in select_columns_and_rename_map.keys():
                    if f not in data_df.columns:
                        msg = f"ODFV {odfv.name} has a dependency on the Feature View '{input_name}'. Feature {f} of this Feature View is not found in the retrieved historical data. Available columns: {list(data_df.columns)}"
                        raise TectonValidationError(msg)
                # Let's select all of the features of the input FV from data_df
                input_df = data_df.rename(columns=select_columns_and_rename_map)[
                    [*select_columns_and_rename_map.values()]
                ]
                odfv_invocation_inputs[input_name] = input_df
            elif input.node.HasField("transformation_node"):
                self._extract_inputs_for_odfv_from_data(
                    transformation_node=input.node.transformation_node,
                    data_df=data_df,
                    odfv_invocation_inputs=odfv_invocation_inputs,
                    odfv=odfv,
                )
            else:
                msg = f"Unexpected input found ({input.arg_name}) on ODFV {odfv.name}"
                raise Exception(msg)
        return odfv_invocation_inputs


@attrs.frozen
class PandasRenameColsNode(PandasExecNode):
    input_node: Union[PandasExecNode, SqlExecNode]
    mapping: Optional[Dict[str, str]]
    drop: Optional[List[str]]

    def _to_dataframe(self) -> pandas.DataFrame:
        input_df = self.input_node._to_dataframe()
        output_df = input_df
        if self.drop:
            columns_to_drop = [self.column_name_updater(name) for name in self.drop]
            output_df = input_df.drop(columns=columns_to_drop)
        if self.mapping:
            output_df = input_df.rename(self.mapping)
        return output_df
