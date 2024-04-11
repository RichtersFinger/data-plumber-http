from typing import Any
from dataclasses import dataclass
from types import UnionType
import abc


class _DPType(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def TYPE(self):
        raise NotImplementedError(
            "Property 'TYPE' needs to be defined when using abstract base '_DPType'."
        )

    @abc.abstractmethod
    def make(self, json, loc: str) -> tuple[Any, str, int]:
        raise NotImplementedError(
            "Method 'make' needs to be defined when using abstract base '_DPType'."
        )

    @property
    def __name__(self):
        return self.TYPE.__name__

    def __or__(self, other):
        class _(_DPType):
            _TYPES = [self, other]
            TYPE = self.TYPE | other.TYPE
            __name__ = f"{self.__name__} | {other.__name__}"
            def make(self, json, loc) -> tuple[Any, str, int]:
                _type = next(
                    (t for t in self._TYPES if isinstance(json, t.TYPE)),
                    None
                )
                if _type is None:
                    raise ValueError(
                        "Union type constructor called with bad type. "
                        + f"'{type(json).__name__}' not in '{self.__name__}'."
                    )
                if isinstance(_type.TYPE, UnionType):
                    return _type.make(json, loc)
                return (
                    _type.TYPE(json),
                    Responses.GOOD.msg,
                    Responses.GOOD.status
                )
        return _()


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
