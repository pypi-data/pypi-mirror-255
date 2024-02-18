from enum import Enum
from typing import Any

from pydantic.main import BaseModel


# Spec models
class Spec(BaseModel):
    name: str
    spec: Any


class AISpec(BaseModel):
    system: str
    host: str


# Plan models
class CommandType(str, Enum):
    CREATE = "CREATE"
    DELETE = "DELETE"
    REPLACE = "REPLACE"
    RENAME = "RENAME"
    UNDELETE = "UNDELETE"
    FAIL = "FAIL"
    UPDATE = "UPDATE"

    def __str__(self):
        return self._name_


# Doctor models
class FixStatus(str, Enum):
    FIXED = "fixed"
    FAILED = "failed"

    def __str__(self):
        return self.value


class IssueSeverity(str, Enum):
    WARNING = "warning"
    ERROR = "error"

    def __str__(self):
        return self.value


class Issue(BaseModel, frozen=True):
    id: str
    description: str
    severity: IssueSeverity = IssueSeverity.ERROR


class FixResult(BaseModel, frozen=True):
    issue: Issue
    status: FixStatus
    message: str
