from typing import Any
from dataclasses import dataclass
import abc


class _DPType(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def make(self, json, loc: str) -> tuple[Any, str, int]:
        raise NotImplementedError(
            "Method 'make' needs to be defined when using abstract base '_DPType'."
        )


@dataclass
class _ProblemInfo:
    status: int
    msg: str


class Responses():
    GOOD = _ProblemInfo(0, "")
    MISSING_OPTIONAL = _ProblemInfo(1, "")
    UNKNOWN_PROPERTY = _ProblemInfo(
        400,
        "Argument '{}' in '{}' not allowed (accepted: {})."
    )
    MISSING_REQUIRED = _ProblemInfo(
        400,
        "Object '{}' missing required property '{}'."
    )
    BAD_TYPE = _ProblemInfo(
        422,
        "Argument '{}' in '{}' has bad type. Expected '{}' but found '{}'."
    )


from .array import Array
from .boolean import Boolean
from .float import Float
from .integer import Integer
from .number import Number
from .object import Object
from .string import String


__all__ = [
    "Responses",
    "Array", "Boolean", "Float", "Integer", "Number", "Object", "String",
]
