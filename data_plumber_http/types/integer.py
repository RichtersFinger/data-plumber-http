from typing import Any, Optional

from . import DPType, Responses


class Integer(DPType):
    """
    An `Integer` represents an integer number.

    Keyword arguments:
    values -- list of values allowed in this field
              (default `None`)
    min_value -- lower bound for accepted values (exclusive)
                 (default `None`)
    max_value -- upper bound for accepted values (exclusive)
                 (default `None`)
    min_value_inclusive -- lower bound for accepted values (inclusive)
                           (default `None`)
    max_value_inclusive -- upper bound for accepted values (inclusive)
                           (default `None`)
    """
    TYPE = int

    def __init__(
        self,
        values: Optional[list[int]] = None,
        min_value: Optional[int | float] = None,
        min_value_inclusive: Optional[int | float] = None,
        max_value: Optional[int | float] = None,
        max_value_inclusive: Optional[int | float] = None
    ):
        self._values = values
        if min_value is not None and min_value_inclusive is not None:
            raise ValueError(
                "Conflicting options for 'Integer', 'min_value' and "
                + "'min_value_inclusive' are incompatible."
            )
        self._min_value = min_value
        self._min_value_inclusive = min_value_inclusive
        if max_value is not None and max_value_inclusive is not None:
            raise ValueError(
                "Conflicting options for 'Integer', 'max_value' and "
                + "'max_value_inclusive' are incompatible."
            )
        self._max_value = max_value
        self._max_value_inclusive = max_value_inclusive
        self._verbose_interval = (
            ("[" if min_value_inclusive is not None else "(")
            + str(
                min_value_inclusive if min_value_inclusive is not None else
                min_value if min_value is not None else "-"
            )
            + ", "
            + str(
                max_value_inclusive if max_value_inclusive is not None else
                max_value if max_value is not None else "-"
            )
            + ("]" if max_value_inclusive is not None else ")")
        )

    def make(self, json, loc: str) -> tuple[Any, str, int]:
        # validate values
        if self._values is not None \
                and json not in self._values:
            return (
                None,
                Responses().BAD_VALUE.msg.format(
                    origin=json,
                    loc=loc,
                    expected="one of " + ", ".join(f"'{v}'" for v in self._values)
                ),
                Responses().BAD_VALUE.status
            )
        # validate range
        if any(
            (
                self._min_value is not None and json <= self._min_value,
                self._max_value is not None and json >= self._max_value,
                self._min_value_inclusive is not None
                    and json < self._min_value_inclusive,
                self._max_value_inclusive is not None
                    and json > self._max_value_inclusive
            )
        ):
            return (
                None,
                Responses().BAD_VALUE.msg.format(
                    origin=json,
                    loc=loc,
                    expected=f"number in the interval {self._verbose_interval}"
                ),
                Responses().BAD_VALUE.status
            )
        return (
            self.TYPE(json),
            Responses().GOOD.msg,
            Responses().GOOD.status
        )
