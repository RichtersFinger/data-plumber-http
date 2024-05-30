from typing import Optional

from . import DPType, Integer, Float


class Number(DPType):
    """
    A `Number` corresponds to the JSON-type 'number'.

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
    TYPE = None
    def make(self, _, __):
        return None

    def __new__(
        cls,
        values: Optional[list[int | float]] = None,
        min_value: Optional[int | float] = None,
        min_value_inclusive: Optional[int | float] = None,
        max_value: Optional[int | float] = None,
        max_value_inclusive: Optional[int | float] = None
    ):
        return Integer(
            values=None
                if values is None
                else [v for v in values if isinstance(v, int)],
            min_value=min_value,
            min_value_inclusive=min_value_inclusive,
            max_value=max_value,
            max_value_inclusive=max_value_inclusive
        ) | Float(
            values=None
                if values is None
                else [v for v in values if isinstance(v, float)],
            min_value=min_value,
            min_value_inclusive=min_value_inclusive,
            max_value=max_value,
            max_value_inclusive=max_value_inclusive
        )
