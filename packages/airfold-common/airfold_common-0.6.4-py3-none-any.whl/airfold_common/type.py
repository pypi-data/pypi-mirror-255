from typing import Literal

Lookup = dict[str, str]
Schema = dict[str, str]

ParamType = Literal["string", "int", "float", "bool", "date", "datetime"]
ParamTypeMap: dict[ParamType, str] = {
    "string": "String",
    "int": "Int64",
    "float": "Float64",
    "bool": "Boolean",
    "date": "Date32",
    "datetime": "DateTime64",
}
