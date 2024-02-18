import asyncio
import json
import os
import re
import typing
from glob import glob
from pathlib import Path
from types import GenericAlias
from typing import Any, Iterable, Tuple, TypeVar
from urllib.parse import urlparse
from uuid import uuid4

from pydantic.main import BaseModel

from airfold_common.type import ParamType

OBJ_ID_RE = re.compile(r"^af[0-9a-f]{32}$")
STREAM_MARKER = "-"


def uuid() -> str:
    return "af" + uuid4().hex


def is_uuid(obj_id: str) -> bool:
    if obj_id:
        if OBJ_ID_RE.match(obj_id):
            return True
    return False


def model_hierarchy(model) -> dict[str, Any]:
    def _model_hierarchy(model: BaseModel) -> dict[str, Any]:
        hints = typing.get_type_hints(model)
        fields: dict[str, Any] = {}
        for field in model.__fields__.values():
            # `typing.Any` is "not a class" in python<=3.10, lol
            if not field.type_ == typing.Any and issubclass(field.type_, BaseModel):
                fields[field.name] = _model_hierarchy(field.type_)
            else:
                fields[field.name] = hints[field.name]
        return fields

    return _model_hierarchy(model)


def config_from_env(prefix: str) -> dict[str, str]:
    return {k.lower().replace(f"{prefix.lower()}_", ""): v for k, v in os.environ.items() if k.startswith(prefix)}


def dict_from_env(schema: dict, prefix: str) -> dict:
    _prefix: str = f"{prefix}_" if prefix else ""

    def _dict_from_env(schema: dict, prefix: str = "") -> dict:
        result: dict = {}
        for key, value in schema.items():
            if isinstance(value, dict):
                v = _dict_from_env(value, prefix + key + "_")
                if v:
                    result[key] = v
            else:
                env_key: str = f"{prefix}{key}".upper()
                if env_key in os.environ:
                    if isinstance(value, list) or (isinstance(value, GenericAlias) and value.__origin__ == list):
                        result[key] = json.loads(os.environ[env_key])
                    elif isinstance(value, dict) or (isinstance(value, GenericAlias) and value.__origin__ == dict):
                        result[key] = json.loads(os.environ[env_key])
                    else:
                        result[key] = os.environ[env_key]
                elif value == dict:
                    v = config_from_env(env_key)
                    if v:
                        result[key] = v
        return result

    return _dict_from_env(schema, _prefix)


def model_from_env(model, prefix: str) -> Any:
    schema: dict = model_hierarchy(model)
    data: dict = dict_from_env(schema, prefix)

    try:
        return model(**data)
    except Exception:
        return None


T = TypeVar("T")


def grouped(iterable: Iterable[T], n=2) -> Iterable[Tuple[T, ...]]:
    """s -> (s0,s1,s2,...sn-1), (sn,sn+1,sn+2,...s2n-1), ..."""
    return zip(*[iter(iterable)] * n)


def is_kind(obj: dict, kind: str) -> bool:
    return obj.get("kind") == kind


class S3Url(object):
    def __init__(self, url):
        self._parsed = urlparse(url, allow_fragments=False)

    @property
    def bucket(self):
        return self._parsed.netloc

    @property
    def key(self):
        if self._parsed.query:
            return self._parsed.path.lstrip("/") + "?" + self._parsed.query
        else:
            return self._parsed.path.lstrip("/")

    @property
    def url(self):
        return self._parsed.geturl()


def cast(v: str | None, data_type: ParamType) -> Any:
    if v is not None:
        try:
            if data_type == "int":
                return int(v, 10)
            if data_type == "float":
                return float(v)
            if data_type == "bool":
                return bool(v)
        except ValueError:
            pass
    return v


def find_files(path: typing.Union[str, list[str]], file_ext: list[str] | None = None) -> list[Path]:
    res: list[Path] = []

    if isinstance(path, str):
        path = [path]
    for ipath in path:
        if ipath == STREAM_MARKER:
            res.append(Path(STREAM_MARKER))
            continue
        resolved = [os.path.abspath(p) for p in glob(ipath)]
        for p in resolved:
            if os.path.isdir(p):
                for root, dirs, files in os.walk(p):
                    for f in files:
                        file_path = Path(os.path.join(root, f))
                        if not file_ext or file_path.suffix.lower() in file_ext:
                            res.append(file_path)
            elif os.path.exists(p):
                file_path = Path(p)
                if not file_ext or file_path.suffix.lower() in file_ext:
                    res.append(file_path)
    return res


def is_path_stream(path: typing.Union[str, Path, list[Path], list[str], list[Path | str], None]) -> bool:
    if not path:
        return False
    if isinstance(path, list):
        return is_path_stream(path[0]) if path else False
    if isinstance(path, Path):
        path = str(path)
    return path == STREAM_MARKER


def ensure_event_loop():
    """Ensures an asyncio event loop exists for the current thread."""
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop
