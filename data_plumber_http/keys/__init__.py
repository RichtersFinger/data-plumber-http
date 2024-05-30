from typing import TypeAlias, Mapping, Optional
import abc

from data_plumber import Pipeline


Values: TypeAlias = "DPType" | Mapping["DPKey", "Values"]  # type: ignore[name-defined]


class DPKey(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_origins(self, value: Values) -> list[str]:
        """
        Returns list of origins involved with this key and `value`.
        """
        raise NotImplementedError(
            "Method 'get_origins' needs to be defined when using abstract base 'DPKey'."
        )

    @abc.abstractmethod
    def assemble(self, value: Values, loc: Optional[str]) -> Pipeline:
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
