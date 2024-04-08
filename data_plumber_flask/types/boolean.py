from typing import Any

from . import _DPType, Responses


class Boolean(_DPType):
    TYPE = bool

    def make(self, json, loc: str) -> tuple[Any, str, int]:
        return (
            self.TYPE(json),
            Responses.GOOD.msg,
            Responses.GOOD.status
        )
