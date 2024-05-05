from typing import Any, Optional
import re

from . import DPType, Responses


class String(DPType):
    """
    A `String` corresponds to the JSON-type 'string'.

    Keyword arguments:
    pattern -- regex-pattern that the value of this field has to match
               (default `None`)
    enum -- list of allowed values for this field
            (default `None`)
    """
    TYPE = str

    def __init__(
        self,
        pattern: Optional[str] = None,
        enum: Optional[list[str]] = None
    ):
        self._pattern = pattern
        self._enum = enum

    def make(self, json, loc: str) -> tuple[Any, str, int]:
        # validate pattern
        if self._pattern is not None \
                and not re.fullmatch(self._pattern, json):
            return (
                None,
                Responses().BAD_VALUE.msg.format(
                    json, loc, f"pattern '{self._pattern}'"
                ),
                Responses().BAD_VALUE.status
            )
        # validate enum
        if self._enum is not None \
                and json not in self._enum:
            return (
                None,
                Responses().BAD_VALUE.msg.format(
                    json,
                    loc,
                    "one of " + ", ".join(f"'{v}'" for v in self._enum)
                ),
                Responses().BAD_VALUE.status
            )
        return (
            self.TYPE(json),
            Responses().GOOD.msg,
            Responses().GOOD.status
        )
