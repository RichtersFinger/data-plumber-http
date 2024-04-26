class DPKey:
    pass


_DPKey = DPKey  # legacy


#from .all_of import AllOf
#from .one_of import OneOf
from .property import Property

__all__ = [
    #"AllOf", "OneOf",
    "DPKey",
    "Property",
]
