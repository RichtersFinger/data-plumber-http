from typing import Optional, Callable, Any

from data_plumber import Pipeline, Stage

from data_plumber_http.output import Output
from data_plumber_http.settings import Responses
from . import DPKey


class Property(DPKey):
    """
    A `Property` is used to describe the key-related properties of a
    field in an `Object.properties`-mapping.

    Keyword arguments:
    origin -- key name in the input JSON
    name -- name of the key generated from this `Property`;
            (default `None`; corresponds to same as `origin`)
    default -- either static value or callable taking input kwargs; used
               as default if property is missing in request
               (default `None`)
    required -- if `True`, this property is marked as required
                (default `False`)
    validation_only -- skip exporting this property to the resulting
                       data and only perform validation
                       (default `False`)
    """
    def __init__(
        self,
        origin: str,
        name: Optional[str] = None,
        default: Optional[Callable[..., Any] | Any] = None,
        required: bool = False,
        validation_only: bool = False
    ) -> None:
        self.origin = origin
        if name is None:
            self._name = origin
        else:
            self._name = name
        if self._name == "":
            raise ValueError("Empty Property-name is not allowed.")
        self.default = default
        self.required = required
        self.validation_only = validation_only

    @property
    def name(self) -> str:
        """`Property`'s `name`."""
        return self._name

    @name.setter
    def name(self, value) -> None:
        if value == "":
            raise ValueError("Empty Property-name is not allowed.")
        self._name = value

    def get_origins(self, value):
        return [self.origin]

    @staticmethod
    def _arg_exists_hard(k, loc):
        return Stage(
            primer=lambda json, **kwargs: k.origin in json,
            status=lambda primer, **kwargs:
                Responses().GOOD.status if primer
                else Responses().MISSING_REQUIRED.status,
            message=lambda primer, **kwargs:
                Responses().GOOD.msg if primer
                else Responses().MISSING_REQUIRED.msg.format(
                    loc,
                    k.origin
                )
        )

    @staticmethod
    def _arg_exists_soft(k):
        return Stage(
            primer=lambda json, **kwargs: k.origin in json,
            status=lambda primer, **kwargs:
                Responses().GOOD.status if primer
                else Responses().MISSING_OPTIONAL.status,
            message=lambda primer, **kwargs:
                Responses().GOOD.msg if primer
                else Responses().MISSING_OPTIONAL.msg
        )

    @staticmethod
    def _arg_has_type(k, v, loc):
        return Stage(
            requires={k.name: Responses().GOOD.status},
            primer=lambda json, **kwargs: isinstance(json[k.origin], v.TYPE),
            status=lambda primer, **kwargs:
                Responses().GOOD.status if primer else Responses().BAD_TYPE.status,
            message=lambda primer, json, **kwargs:
                Responses().GOOD.msg if primer
                else Responses().BAD_TYPE.msg.format(
                    k.origin,
                    loc,
                    v.__name__,
                    type(json[k.origin]).__name__
                )
        )

    @staticmethod
    def _make_instance(k, v, loc):
        return Stage(
            requires={k.name: Responses().GOOD.status},
            primer=lambda json, **kwargs:
                v.make(json[k.origin], loc),
            export=lambda primer, **kwargs:
                {f"EXPORT_{k.name}": primer[0]}
                if primer[2] == Responses().GOOD.status
                else {},
            status=lambda primer, **kwargs: primer[2],
            message=lambda primer, **kwargs: primer[1]
        )

    @staticmethod
    def _set_default(k):
        return Stage(
            requires={k.name: Responses().MISSING_OPTIONAL.status},
            primer=k.default
                if callable(k.default)
                else lambda **kwargs: k.default,
            export=lambda primer, **kwargs:
                {f"EXPORT_{k.name}": primer},
            status=lambda **kwargs: Responses().GOOD.status,
            message=lambda **kwargs: Responses().GOOD.msg
        )

    @staticmethod
    def _output(k):
        return Stage(
            primer=lambda **kwargs:
                f"EXPORT_{k.name}" in kwargs,
            action=lambda out, primer, **kwargs:
                [
                    out.update({"kwargs": {}})
                    if "kwargs" not in out
                    else None,
                    out.kwargs.update(
                        {k.name: kwargs.get(f"EXPORT_{k.name}")}
                        if primer
                        else {}
                    )
                ],
            status=lambda **kwargs: Responses().GOOD.status,
            message=lambda **kwargs: Responses().GOOD.msg
        )

    def assemble(self, value, loc):
        def finalizer(data, records, **kwargs):
            if records[-1].status == Responses().GOOD.status:
                data.value = kwargs.get(f"EXPORT_{self.name}")
        p = Pipeline(
            exit_on_status=lambda status: status >= 400,
            initialize_output=Output,
            finalize_output=finalizer
        )
        _loc = loc or "."
        # k.name: validate existence
        if self.required and self.default is None:
            p.append(
                self.name,
                **{self.name: self._arg_exists_hard(self, _loc)}
            )
        else:
            p.append(self.name, **{self.name: self._arg_exists_soft(self)})
        # {k.name}[type]: validate type
        p.append(
            f"{self.name}[type]",
            **{f"{self.name}[type]": self._arg_has_type(self, value, _loc)}
        )
        # {k.name}[dptype]: validate, make, and export instance as
        #                   f"EXPORT_{k.name}" (if valid)
        p.append(
            f"{self.name}[dptype]",
            **{f"{self.name}[dptype]": self._make_instance(
                self, value, (loc or "") + "." + self.origin
            )}
        )
        if self.validation_only:
            return p
        # {k.name}[default]: apply default if required (or set None
        #   if property has fill_with_none set) and export as
        #   f"EXPORT_{k.name}"
        if self.default is not None:
            p.append(
                f"{self.name}[default]",
                **{f"{self.name}[default]": self._set_default(self)}
            )
        # {k.name}[output]: output to data
        p.append(
            f"{self.name}[output]",
            **{f"{self.name}[output]": self._output(self)}
        )
        return p
