from typing import Any

from . import _DPType, Responses


class Array(_DPType):
    TYPE = list

    def __init__(self, items: _DPType):
        self._items = items

    def make(self, json, loc: str) -> tuple[Any, str, int]:
        array = []
        for element in json:
            if not isinstance(element, self._items.TYPE):
                return (
                    None,
                    f"Element in '{loc}' has bad type. Expected "
                    + f"'{self._items.__name__}' but found "
                    + f"'{type(element).__name__}'.",
                    Responses.BAD_TYPE.status
                )
            child = self._items.make(element, loc)
            if child[2] != Responses.GOOD.status:
                return (None, child[1], child[2])
            array.append(child[0])
        return (
            array,
            Responses.GOOD.msg,
            Responses.GOOD.status
        )
