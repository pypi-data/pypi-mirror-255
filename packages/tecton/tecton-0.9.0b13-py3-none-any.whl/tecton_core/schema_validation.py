from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Optional

import pandas as pd
import pyarrow as pa

from tecton_core import data_types
from tecton_core.schema import Schema


@dataclass
class FieldTypeDiff:
    field: str
    # ToDo (pyalex) support non-arrow types as well
    expected: pa.DataType
    actual: pa.DataType


@dataclass
class DiffResult:
    missing_fields: List[str]
    excessive_fields: List[str]
    missmatch_types: List[FieldTypeDiff]

    def __bool__(self):
        return len(self.missing_fields) > 0 or len(self.excessive_fields) > 0 or len(self.missmatch_types) > 0

    def as_str(self):
        def lines():
            if self.missing_fields:
                yield f"Missing fields: {', '.join(self.missing_fields)}."

            if self.excessive_fields:
                yield f"Unexpected fields: {', '.join(self.excessive_fields)}."

            if self.missmatch_types:
                yield "Types do not match:"
                yield ""
                for item in self.missmatch_types:
                    yield f"  Field: {item.field}"
                    yield f"  Expected: {item.expected}"
                    yield f"  Actual: {item.actual}"
                    yield ""

        return "\n".join(lines())


def validate_schema_arrow_table(
    table: pa.Table, schema: Schema, allow_null: bool = True, strict_struct_order: bool = True
) -> Optional[DiffResult]:
    expected_schema = tecton_schema_to_arrow_schema(schema)
    actual_schema = table.schema

    diff = _diff_arrow_schemas(
        expected_schema, actual_schema, allow_null=allow_null, strict_struct_order=strict_struct_order
    )
    if not diff:
        # return None instead of empty diff
        return

    return diff


def validate_schema_pandas_df(
    df: pd.DataFrame, schema: Schema, allow_null: bool = True, strict_struct_order: bool = True
) -> Optional[DiffResult]:
    return validate_schema_arrow_table(
        pa.Table.from_pandas(df), schema, allow_null=allow_null, strict_struct_order=strict_struct_order
    )


_PRIMITIVE_TECTON_TYPE_TO_ARROW_TYPE: Dict[data_types.DataType, pa.DataType] = {
    data_types.Int32Type(): pa.int32(),
    data_types.Int64Type(): pa.int64(),
    data_types.Float32Type(): pa.float32(),
    data_types.Float64Type(): pa.float64(),
    data_types.StringType(): pa.string(),
    data_types.TimestampType(): pa.timestamp("ns"),
    data_types.BoolType(): pa.bool_(),
}


def _tecton_type_to_arrow_type(tecton_type: data_types.DataType) -> pa.DataType:
    if tecton_type in _PRIMITIVE_TECTON_TYPE_TO_ARROW_TYPE:
        return _PRIMITIVE_TECTON_TYPE_TO_ARROW_TYPE[tecton_type]

    if isinstance(tecton_type, data_types.ArrayType):
        return pa.list_(_tecton_type_to_arrow_type(tecton_type.element_type))

    if isinstance(tecton_type, data_types.MapType):
        return pa.map_(
            _tecton_type_to_arrow_type(tecton_type.key_type),
            _tecton_type_to_arrow_type(tecton_type.value_type),
        )

    if isinstance(tecton_type, data_types.StructType):
        fields = []
        for tecton_field in tecton_type.fields:
            fields.append(pa.field(tecton_field.name, _tecton_type_to_arrow_type(tecton_field.data_type)))
        return pa.struct(fields)

    msg = f"Tecton type {tecton_type} can't be converted to arrow type"
    raise ValueError(msg)


def tecton_schema_to_arrow_schema(schema: Schema) -> pa.Schema:
    fields = []
    for column, data_type in schema.column_name_and_data_types():
        fields.append(pa.field(column, _tecton_type_to_arrow_type(data_type)))
    return pa.schema(fields)


_SAFE_CAST = {
    (pa.int8(), pa.int32()),
    (pa.int8(), pa.int64()),
    (pa.int16(), pa.int32()),
    (pa.int16(), pa.int64()),
    (pa.int32(), pa.int64()),
    (pa.float32(), pa.float64()),
}


def _arrow_types_equal(
    expected: pa.DataType, actual: pa.DataType, allow_null: bool = True, strict_struct_order: bool = True
) -> bool:
    # We ignore timezones, as immediately after the feature view transformation is executed, a ConvertTimestampToUTCNode
    # will convert any timestamps to UTC and then remove all timezone information.
    if isinstance(actual, pa.TimestampType):
        # convert into timezone naive
        actual = pa.timestamp(actual.unit)

    # The actual schema can be a struct even though the expected schema is a map. This is because pyarrow.Table.from_pandas()
    # converts maps to structs. For example, the dict {"a": 1, "b": 2} will be converted into the pyarrow struct
    # struct<a: int64, b: int64>.
    if isinstance(expected, pa.MapType) and isinstance(actual, pa.StructType):
        if expected.key_type == pa.string():
            struct_field_types = set()
            for field in actual:
                # The struct may contain a null field, whose type is pa.null(). This type should be ignored.
                if field.type != pa.null():
                    struct_field_types.add(field.type)
            if len(struct_field_types) == 0:
                # The struct only contains nulls.
                return True
            if len(struct_field_types) == 1 and _arrow_types_equal(expected.item_type, struct_field_types.pop()):
                return True

    if expected == actual:
        return True

    if (actual, expected) in _SAFE_CAST:
        return True

    if allow_null and actual == pa.null():
        # most probably there's no data in this column in user dataset,
        # so the inferred type is null, but it will be casted to the expected type just fine.
        return True

    if isinstance(expected, pa.ListType) and isinstance(actual, pa.ListType):
        return _arrow_types_equal(expected.value_type, actual.value_type, allow_null)

    if isinstance(expected, pa.StructType) and isinstance(actual, pa.StructType):
        if strict_struct_order:
            expected_fields = [expected[i] for i in range(expected.num_fields)]
            actual_fields = [actual[i] for i in range(actual.num_fields)]
        else:
            expected_fields = sorted([expected[i] for i in range(expected.num_fields)], key=lambda f: f.name)
            actual_fields = sorted([actual[i] for i in range(actual.num_fields)], key=lambda f: f.name)

        if len(expected_fields) != len(actual_fields):
            return False

        return all(
            e.name == a.name and _arrow_types_equal(e.type, a.type, allow_null)
            for e, a in zip(expected_fields, actual_fields)
        )

    if isinstance(expected, pa.MapType) and isinstance(actual, pa.MapType):
        return _arrow_types_equal(expected.key_type, actual.key_type, allow_null) and _arrow_types_equal(
            expected.item_type, actual.item_type, allow_null
        )

    return False


def _diff_arrow_schemas(
    expected: pa.Schema, actual: pa.Schema, allow_null: bool = True, strict_struct_order: bool = True
) -> DiffResult:
    missing = set(expected.names) - set(actual.names)
    excessive = set(actual.names) - set(expected.names)
    missmatch_types = []
    for column in set(expected.names) & set(actual.names):
        expected_field = expected.field(column)
        actual_field = actual.field(column)
        if _arrow_types_equal(
            expected_field.type, actual_field.type, allow_null=allow_null, strict_struct_order=strict_struct_order
        ):
            continue

        missmatch_types.append(FieldTypeDiff(field=column, expected=expected_field.type, actual=actual_field.type))

    return DiffResult(
        missing_fields=list(missing),
        excessive_fields=list(excessive),
        missmatch_types=missmatch_types,
    )
