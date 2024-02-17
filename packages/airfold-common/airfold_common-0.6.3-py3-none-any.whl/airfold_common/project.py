import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml
from pydantic.main import BaseModel
from yaml import SafeLoader

from airfold_common.error import AirfoldError
from airfold_common.format import Format
from airfold_common.utils import STREAM_MARKER, find_files, is_path_stream

TRAILING_SPACE_RE = re.compile(r"[ \t]+$", flags=re.M)


class ProjectFile(BaseModel, frozen=True):
    name: str
    data: dict
    pulled: bool = False

    def __str__(self) -> str:
        return f"{self.name}({self.type})"

    @property
    def type(self):
        return self.data.get("type", "Unknown")


class LocalFile(ProjectFile, frozen=True):
    path: str


# see https://github.com/yaml/pyyaml/issues/121
def construct_yaml_str(loader, node):
    m = TRAILING_SPACE_RE.search(node.value)
    if m:
        raise AirfoldError(f"Trailing space found while loading yaml: '{node.value[:m.span(0)[1]]}'")
    return loader.construct_scalar(node)


class Loader(SafeLoader):
    pass


Loader.add_constructor("tag:yaml.org,2002:str", construct_yaml_str)


def find_project_files(path: list[str], file_ext: list[str] | None = None) -> list[Path]:
    if file_ext is None:
        file_ext = [".yaml", ".yml"]
    return find_files(path, file_ext)


def create_file(doc: Any, path: str) -> ProjectFile:
    name = doc.get("name")
    if not name:
        raise AirfoldError(f"No `name` in document from: {path}")
    return ProjectFile(name=name, data=doc)


def load_files(paths: list[Path], stream: Any | None = None) -> list[ProjectFile]:
    res: list[ProjectFile] = []
    for path in paths:
        if path == Path(STREAM_MARKER):
            res.extend(load_from_stream(stream or sys.stdin))
        else:
            docs = list(yaml.load_all(open(path), Loader))
            if len(docs) > 1:
                for doc in docs:
                    res.append(create_file(doc, str(path)))
            elif len(docs) == 1:
                res.append(ProjectFile(name=path.stem, data=docs[0]))
    return res


def load_from_stream(stream: Any) -> list[ProjectFile]:
    res: list[ProjectFile] = []
    for doc in yaml.load_all(stream, Loader):
        res.append(create_file(doc, str(stream)))
    return res


def get_local_files(formatter: Format, files: list[ProjectFile]) -> list[LocalFile]:
    res: list[LocalFile] = []
    for file in files:
        if formatter.is_pipe(file.data):
            prefix = "pipes"
        else:
            prefix = "sources"
        file_path = os.path.join(prefix, f"{file.name}.yaml")
        res.append(LocalFile(**file.dict(), path=file_path))
    return res


def str_presenter(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


yaml.representer.SafeRepresenter.add_representer(str, str_presenter)


class Dumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, *args, **kwargs):
        return super().increase_indent(flow=flow, indentless=False)


def sort_keys(key: str) -> str:
    if key == "version":
        return "0"
    if key == "type":
        return "1"
    if key == "name":
        return "2"
    return key


def dump_yaml(data: list[dict] | dict, remove_names=False) -> str:
    if not isinstance(data, list):
        data = [data]
    out = []
    for d in data:
        keys = sorted(d.keys(), key=sort_keys)
        for k in keys:
            if remove_names and k == "name":
                d.pop(k)
                continue
            d[k] = d.pop(k)
        out.append(d)
    return yaml.dump_all(out, Dumper=Dumper, sort_keys=False)


def dump_project_files(files: list[LocalFile], dst_path: str) -> None:
    for file in files:
        file_path = os.path.join(dst_path, file.path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        open(file_path, "w").write(dump_yaml(file.data, remove_names=True))
