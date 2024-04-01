from data_plumber import Pipeline

from . import _DPType

class Object(_DPType):
    def assemble(self) -> Pipeline:
        return Pipeline()
