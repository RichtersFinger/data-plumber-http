from typing import Any
from types import NoneType

from . import DPType, Responses


class Null(DPType):
    """
    A `Null`-object corresponds to the JSON 'null'-value.
    """
    TYPE = NoneType

    def make(self, json, loc: str) -> tuple[Any, str, int]:
        return (
            None,
            Responses.GOOD.msg,
            Responses.GOOD.status
        )
