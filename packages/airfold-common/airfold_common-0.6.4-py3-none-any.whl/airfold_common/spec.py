from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, TypeVar

from pydantic import BaseModel

from airfold_common.error import AirfoldError
from airfold_common.format import Format
from airfold_common.models import Spec
from airfold_common.parse import SpecParser

TSpec = TypeVar("TSpec")

Parser = Callable[[dict], Spec]


class SpecContainer(ABC):
    @abstractmethod
    def get(self, name: str) -> Optional[Spec]:
        pass

    @abstractmethod
    def get_as(self, name: str, type: type[TSpec]) -> Optional[TSpec]:
        pass

    @abstractmethod
    def list(self) -> list[Spec]:
        pass

    @abstractmethod
    def __getitem__(self, key_or_index) -> Spec:
        pass

    def __setitem__(self, key, value):
        raise AirfoldError("Cannot set spec directly")

    @abstractmethod
    def __contains__(self, item):
        pass

    @abstractmethod
    def __len__(self):
        pass

    def __bool__(self):
        return len(self) > 0


class InMemorySpecContainer(SpecContainer):
    def __init__(self) -> None:
        self.specs: Dict[str, Spec] = {}

    def get(self, name: str) -> Optional[Spec]:
        return self.specs.get(name)

    def list(self) -> list[Spec]:
        return list(self.specs.values())

    def __getitem__(self, key_or_index):
        if isinstance(key_or_index, int):
            list_specs = self.list()
            return list_specs[key_or_index]
        elif isinstance(key_or_index, str):
            return self.specs[key_or_index]
        else:
            raise AirfoldError(f"Invalid key type: {type(key_or_index)}")

    def __len__(self):
        return len(self.specs)

    def __contains__(self, item):
        return item in self.specs

    def get_as(self, name: str, type: type[TSpec]) -> Optional[TSpec]:
        spec = self.specs.get(name)
        if spec is None:
            return None
        return type(**(spec.spec.dict() if isinstance(spec.spec, BaseModel) else spec.spec))

    @classmethod
    def from_dict(
        cls, specs: dict[str, dict], formatter: Optional[Format] = None, parser: Optional[Parser] = None
    ) -> "InMemorySpecContainer":
        container = cls()
        formatter = formatter or Format()
        parser = parser or SpecParser(formatter).parse
        container.specs = {name: parser(formatter.normalize(data, name)) for name, data in specs.items()}
        return container
