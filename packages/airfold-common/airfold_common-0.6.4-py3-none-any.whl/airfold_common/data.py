import io
import json
from typing import Any, Union

from airfold_common.error import AirfoldError

JSON_EACH_ROW_FORMAT = "JSONEachRow"


def to_ndjson(data: list[dict[str, Any]]) -> str:
    return "\n".join([json.dumps(row, default=str) for row in data])


def to_format(data: list[dict[str, Any]], format: str = JSON_EACH_ROW_FORMAT) -> str:
    """Convert data to ClickHouse format."""
    if format == JSON_EACH_ROW_FORMAT:
        return to_ndjson(data)
    else:
        raise AirfoldError(f"Wrong format: {format}")


def parse_data(data: Union[bytes, str], format: str = JSON_EACH_ROW_FORMAT) -> list[dict[str, Any]]:
    """Parse data from ClickHouse format."""
    if format == JSON_EACH_ROW_FORMAT:
        return parse_json_each_row(data)
    else:
        raise AirfoldError(f"Wrong format: {format}")


def parse_json_each_row(data: Union[bytes, str]) -> list[dict[str, Any]]:
    lines: str = data.decode() if isinstance(data, bytes) else data
    buf = io.StringIO(lines)
    line = buf.readline().strip()
    res: list[dict[str, Any]] = []
    while line:
        res.append(json.loads(line))
        line = buf.readline().strip()
    return res
