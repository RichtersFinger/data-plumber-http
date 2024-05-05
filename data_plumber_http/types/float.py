from typing import Any, Optional

from . import DPType, Responses


class Float(DPType):
    """
    A `Float` represents a floating point number.

    Keyword arguments:
    values -- list of values allowed in this field
              (default `None`)
    range_ -- tuple of lower and upper bound for values in this field
              (default `None`)
    """
    TYPE = float

    def __init__(
        self,
        values: Optional[list[float]] = None,
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
                Responses().BAD_VALUE.msg.format(
                    json,
                    loc,
                    "one of " + ", ".join(f"'{v}'" for v in self._values)
                ),
                Responses().BAD_VALUE.status
            )
        # validate range
        if self._range is not None \
                and (json < self._range[0] or json > self._range[1]):
            return (
                None,
                Responses().BAD_VALUE.msg.format(
                    json,
                    loc,
                    f"a number in the range [{self._range[0]}, {self._range[1]}]"
                ),
                Responses().BAD_VALUE.status
            )
        return (
            self.TYPE(json),
            Responses().GOOD.msg,
            Responses().GOOD.status
        )
