from typing import Optional

from . import DPType, Integer, Float


class Number(DPType):
    """
    A `Number` corresponds to the JSON-type 'number'.

    Keyword arguments:
    values -- list of values allowed in this field
              (default `None`)
    range_ -- tuple of lower and upper bound for values in this field
              (default `None`)
    """
    TYPE = None
    def make(self, _, __):
        return None

    def __new__(
        cls,
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
