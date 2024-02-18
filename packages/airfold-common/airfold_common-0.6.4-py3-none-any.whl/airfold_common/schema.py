import copy
from typing import Any

import sqlglot
from sqlglot.expressions import (
    ColumnConstraint,
    ColumnDef,
    DataType,
    DefaultColumnConstraint,
    Expression,
    Identifier,
    Literal,
)

from airfold_common.error import AirfoldError


class AirfoldCastError(AirfoldError):
    pass


class AirfoldParseError(AirfoldError, sqlglot.ParseError):
    pass


def parse_one(sql: str, dialect: str = "clickhouse") -> Expression:
    try:
        return sqlglot.parse_one(sql, read=dialect)
    except sqlglot.ParseError as e:
        raise AirfoldParseError(str(e)) from e


CH_TO_JSON_MAP: dict[str, Any] = {
    "UInt8": {"type": "integer", "minimum": 0, "maximum": 255},
    "UInt16": {"type": "integer", "minimum": 0},
    "UInt32": {"type": "integer", "minimum": 0},
    "UInt64": {"type": "integer", "minimum": 0},
    "Int8": {"type": "integer"},
    "Int16": {"type": "integer"},
    "Int32": {"type": "integer"},
    "Int64": {"type": "integer"},
    "Float32": {"type": "number"},
    "Float64": {"type": "number"},
    "DOUBLE": {"type": "number"},
    # "Decimal": {"type": "number"}, # Precision/Scale handled separately
    "Boolean": {"type": "boolean"},
    "BOOLEAN": {"type": "boolean"},
    "String": {"type": "string"},
    # "FixedString": {"type": "string"},  # Length handled separately
    "Date": {"type": "string", "format": "date"},
    "DATE": {"type": "string", "format": "date"},
    "Date32": {"type": "string", "format": "date"},
    "DateTime": {"type": "string", "format": "date-time"},
    "DATETIME": {"type": "string", "format": "date-time"},
    "DateTime64": {"type": "string", "format": "date-time"},
    "DateTime64(3)": {"type": "string", "format": "date-time"},
    "DateTime64(6)": {"type": "string", "format": "date-time"},
    "DateTime64(9)": {"type": "string", "format": "date-time"},
    "JSON": {"type": "object"},
    "UUID": {"type": "string", "format": "uuid"},
    # "Enum": {"type": "string"},  # Enum values handled separately
    "LowCardinality": {"type": "string"},
    # "Array": {"type": "array"},  # Element type handled separately
    # "Map": {"type": "object"},  # Key/Value types handled separately
    # "Nested": {"type": "object"},  # Nested structure handled separately
    # "Tuple": {"type": "array"},  # Tuple items handled separately
    # "Nullable": {"type": "null"},  # Nullable type handled separately
    "IPv4": {"type": "string", "format": "ipv4"},
    "IPv6": {"type": "string", "format": "ipv6"},
}


def convert_type(
    data_type: Expression, constraints: list[ColumnConstraint], dialect: str = "clickhouse"
) -> dict[str, Any]:
    default: Any | None = None
    if (
        constraints
        and isinstance(constraints[0].kind, DefaultColumnConstraint)
        and isinstance(constraints[0].kind.this, Literal)
    ):
        default = constraints[0].kind.this.this
    dt = CH_TO_JSON_MAP.get(data_type.sql(dialect))
    res: dict[str, Any]
    if dt:
        res = copy.deepcopy(dt)
    elif data_type.this == DataType.Type.LOWCARDINALITY:
        value_type = data_type.expressions[0]
        res = convert_type(value_type, constraints, dialect)
    elif data_type.this == DataType.Type.FIXEDSTRING:
        length = int(data_type.expressions[0].this.sql(dialect))
        res = {"type": "string", "minLength": length, "maxLength": length}
    elif data_type.this == DataType.Type.DECIMAL:
        # TODO: theres "exclusiveMaximum" in the spec, but it's limited to Int32 (decimals can be Int64)
        # p = 10
        # if len(data_type.expressions) > 0:
        #     p = int(data_type.expressions[0].sql(dialect))
        s = 0
        if len(data_type.expressions) > 1:
            s = int(data_type.expressions[1].sql(dialect))
        multiple = 10 ** (-s)
        res = {"type": "number", "multipleOf": multiple}
    elif data_type.this in [DataType.Type.ENUM, DataType.Type.ENUM8, DataType.Type.ENUM16]:
        enum = []
        for item in data_type.expressions:
            if isinstance(item, Literal):
                name = item.this
            else:
                name = item.this.this
            enum.append(name)
        res = {"type": "string", "enum": enum}
    elif data_type.this == DataType.Type.ARRAY:
        array_type = data_type.expressions[0]
        res = {"type": "array", "items": convert_type(array_type, [], dialect)}
    elif data_type.this == DataType.Type.MAP:
        key_type = data_type.expressions[0]
        if key_type.this != DataType.Type.TEXT:
            raise AirfoldCastError(f"Unsupported map with non-string keys: {data_type.sql(dialect)}")
        value_type = data_type.expressions[1]
        res = {"type": "object", "additionalProperties": convert_type(value_type, [], dialect)}
    elif data_type.this == DataType.Type.STRUCT:
        items = []
        for item in data_type.expressions:
            if isinstance(item, Identifier):
                str_type = item.this
                expr = parse_one(f"CREATE TABLE t (a {str_type})", dialect=dialect)
                col = expr.this.expressions[0]
                items.append(convert_type(col.args["kind"], [], dialect))
            elif isinstance(item, DataType):
                items.append(convert_type(item, [], dialect))
        # TODO: maybe {"items": false} is needed
        res = {"type": "array", "prefixItems": items}
    elif data_type.this == DataType.Type.NULLABLE:
        value_type = data_type.expressions[0]
        res = {"oneOf": [{"type": "null"}, convert_type(value_type, [], dialect)]}
    else:
        raise AirfoldCastError(f"Unsupported data type: {data_type.sql(dialect)}")
    if default:
        res["default"] = default
    return res


def convert_schema(schema: str | dict[str, str], dialect: str = "clickhouse") -> dict[str, Any]:
    res: dict[str, Any] = {"type": "object", "properties": {}}
    str_schema = schema if isinstance(schema, str) else ", ".join([" ".join([f"`{n}`", t]) for n, t in schema.items()])
    create_table = f"CREATE TABLE t ({str_schema})"
    sql_exp = parse_one(create_table, dialect=dialect)
    required = []
    for col in sql_exp.this.expressions:
        if isinstance(col, ColumnDef):
            name = str(col.this.this)
            required.append(name)
            data_type = col.args["kind"]
            constraints = col.args["constraints"]
            if data_type.this == DataType.Type.NESTED:
                nested_types = ", ".join([t.sql(dialect) for t in data_type.expressions])
                res["properties"][name] = convert_schema(nested_types, dialect)
            else:
                res["properties"][name] = convert_type(data_type, constraints)
        else:
            raise AirfoldCastError(f"Unsupported data type: {col.sql(dialect)}")
    res["required"] = required
    return res
