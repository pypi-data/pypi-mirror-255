from airfold_common.error import AirfoldError
from airfold_common.utils import is_uuid


class FormatError(AirfoldError):
    pass


class Format:
    def __init__(self) -> None:
        self.AIRFOLD_CORE: str = "core.airfold.co"
        self.DEFAULT_VERSION: str = f"{self.AIRFOLD_CORE}/v1"
        self.SUPPORTED_VERSIONS: list[str] = [f"{self.AIRFOLD_CORE}/v1"]
        self.SOURCE_TYPES: list[str] = ["Table"]
        self.PIPE_TYPES: list[str] = ["Pipe"]
        self.SPEC_TYPES: list[str] = ["Spec"]

    @property
    def SUPPORTED_TYPES(self) -> list[str]:
        return self.SOURCE_TYPES + self.PIPE_TYPES + self.SPEC_TYPES

    def normalize(self, data: dict, name: str) -> dict:
        data["version"] = self.normalize_version(data)
        data["type"] = self.normalize_type(data)
        data["name"] = self.normalize_name(data, name)
        return data

    def normalize_version(self, data: dict) -> str:
        ver: str | None = data.get("version")
        if ver is None or ver == "":
            ver = self.DEFAULT_VERSION
        assert ver
        res = ver.split("/", 1)
        if len(res) == 1:
            res.insert(0, self.AIRFOLD_CORE)
        elif len(res) > 2:
            raise FormatError(f"Error parsing version: {ver}")
        norm_ver = "/".join(res)
        if norm_ver not in self.SUPPORTED_VERSIONS:
            raise FormatError(f"Unknown or not supported version: {norm_ver}")
        return norm_ver

    def guess_type(self, data: dict) -> str:
        data_type: str = ""
        if "spec" in data:
            data_type = "Spec"
        elif "cols" in data or "sql" in data:
            data_type = "Table"
        elif "nodes" in data:
            data_type = "Pipe"
        if not data_type:
            raise FormatError("Type is not set, and failed to guess it")
        return data_type

    def normalize_type(self, data: dict) -> str:
        data_type: str | None = data.get("type")
        if data_type is None or data_type == "":
            data_type = self.guess_type(data)
        if data_type not in self.SUPPORTED_TYPES:
            raise FormatError(f"Unknown or not supported type definition: {data_type}")
        return data_type

    def normalize_name(self, data: dict, name: str) -> str:
        norm_name = data.get("name", name)
        if not norm_name or is_uuid(norm_name):
            raise FormatError(f"Object name is invalid: '{norm_name}'")
        return norm_name

    def is_source(self, data: dict) -> bool:
        return data["type"] in self.SOURCE_TYPES

    def is_pipe(self, data: dict) -> bool:
        return data["type"] in self.PIPE_TYPES

    def is_spec(self, data: dict) -> bool:
        return data["type"] in self.SPEC_TYPES

    def get_version(self, data: dict) -> str:
        return data.get("version", self.normalize_version(data))

    def get_type(self, data: dict) -> str:
        return data.get("type", self.normalize_type(data))


class ChFormat(Format):
    def __init__(self):
        super().__init__()
        self.DEFAULT_VERSION = "clickhouse.airfold.co/v1"
        self.SUPPORTED_VERSIONS += ["clickhouse.airfold.co/v1"]
        self.SOURCE_TYPES += ["Dictionary", "AITable"]
        self.SPEC_TYPES += ["AISpec"]

    def guess_type(self, data: dict) -> str:
        data_type: str = ""
        if "cols" in data and ("message" in data or "added_cols" in data):
            data_type = "AITable"
        if data_type:
            return data_type
        return super().guess_type(data)
