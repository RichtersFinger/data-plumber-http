from . import _DPType, Integer, Float


class Number(_DPType):
    TYPE = None
    make = None
    def __new__(self):
        return Integer() | Float()
