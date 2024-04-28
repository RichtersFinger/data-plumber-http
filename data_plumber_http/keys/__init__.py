import abc

from data_plumber import Pipeline, Stage

from data_plumber_http.settings import Responses


class DPKey(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def assemble(self, value, loc: str) -> Pipeline:
        """
        Returns `Pipeline` that processes the given `value` for this key.
        """
        raise NotImplementedError(
            "Method 'assemble' needs to be defined when using abstract base 'DPKey'."
        )


_DPKey = DPKey  # legacy


from .property import Property
from .one_of import OneOf
from .all_of import AllOf

__all__ = [
    "DPKey",
    "Property", "AllOf", "OneOf",
]
