from typing import Any, Optional

from . import _DPType, Responses


class Integer(_DPType):
    TYPE = int

    def __init__(
        self,
        values: Optional[list[int]] = None,
        range_: Optional[tuple[int | float, int | float]] = None
    ):
        self._values = values
        self._range = range_

    def make(self, json, loc: str) -> tuple[Any, str, int]:
        # validate values
        if self._values is not None \
                and json not in self._values:
            return (
                None,
                Responses.BAD_VALUE.msg.format(
                    json,
                    loc,
                    "one of " + ", ".join(f"'{v}'" for v in self._values)
                ),
                Responses.BAD_VALUE.status
            )
        # validate range
        if self._range is not None \
                and (json < self._range[0] or json > self._range[1]):
            return (
                None,
                Responses.BAD_VALUE.msg.format(
                    json,
                    loc,
                    f"a number in the range [{self._range[0]}, {self._range[1]}]"
                ),
                Responses.BAD_VALUE.status
            )
        return (
            self.TYPE(json),
            Responses.GOOD.msg,
            Responses.GOOD.status
        )
