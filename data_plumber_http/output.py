from typing import Any


class Output(dict):
    """
    Type of the data-object in `Pipeline` generated from
    `Object.assemble`.

    Inherits from `dict` but provides the two properties
    kwargs -- `kwargs`-dictionary which has been generated by the
              `Object.assemble`-`Pipeline`
    value -- `Object.model`-object instantiated using `kwargs`
    """
    @property
    def value(self) -> Any:
        return self.get("value", None)

    @value.setter
    def value(self, value):
        self["value"] = value

    @property
    def kwargs(self) -> dict:
        return self.get("kwargs", {})

    @kwargs.setter
    def kwargs(self, kwargs):
        self["kwargs"] = kwargs
