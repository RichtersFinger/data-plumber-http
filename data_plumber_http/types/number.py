from typing import Optional

from . import _DPType, Integer, Float


class Number(_DPType):
    TYPE = None
    make = None

    def __new__(
        self,
        values: Optional[list[int | float]] = None,
        range_: Optional[tuple[int | float, int | float]] = None
    ):
        return Integer(
            values=None
                if values is None
                else [v for v in values if isinstance(v, int)],
            range_=range_
        ) | Float(
            values=None
                if values is None
                else [v for v in values if isinstance(v, float)],
            range_=range_
        )
