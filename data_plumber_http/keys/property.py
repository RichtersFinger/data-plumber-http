from typing import Optional, Callable, Any

from . import _DPKey


class Property(_DPKey):
    """
    A `Property` is used to describe the key-related properties of a
    field in an `Object.properties`-mapping.

    Keyword arguments:
    origin -- key name in the input json
    name -- name of the key generated from this `Property`;
            (default `None`; corresponds to same as `origin`)
    default -- either static value or callable taking input kwargs; used
               as default if property is missing in request
               (default `None`)
    required -- if `True`, this property is marked as required
                (default False)
    fill_with_none -- if `True`, fill fields of missing arguments
                      without default with `None`
                      (default `False`)
    validation_only -- skip exporting this property to the resulting
                       data but only perform validation
    """
    def __init__(
        self,
        origin: str,
        name: Optional[str] = None,
        default: Optional[Callable[[...], Any] | Any] = None,
        required: bool = False,
        fill_with_none: bool = False,
        validation_only: bool = False
    ) -> None:
        self.origin = origin
        self.name = name or origin
        self.default = default
        self.required = required
        self.fill_with_none = fill_with_none
        self.validation_only = validation_only
