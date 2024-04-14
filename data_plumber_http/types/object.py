from typing import TypeAlias, Mapping, Optional, Any

from data_plumber import Pipeline, Stage

from data_plumber_http.keys import _DPKey, Property
from . import _DPType, Responses, Output


Properties: TypeAlias = Mapping[_DPKey, "_DPType | Properties"]


class Object(_DPType):
    """
    An `Object` corresponds to the json-type 'object'.

    Keyword arguments:
    model -- data model for this `Object` (gets passed all properties
             and additional properties as kwargs)
             (default `None`; corresponds to dictionary)
    properties -- mapping for explicitly expected contents of this
                  `Object`
                  (default `None`)
    additional_properties -- type for implicitly expected contents of
                             this `Object` (mutually exclusive with
                             `accept_only`)
                             (default `None`)
    accept_only -- if set, on execution a `json` is rejected with 400
                   status if it contains a key that is not in
                   `accept_only` (mutually exclusive with
                   `additional_properties`)
                   (default `None`)
    free_form -- if `True`, accept and use any content that has not been
                 defined explicitly via `properties`
                 (default `False`)
    """
    TYPE = dict

    def __init__(
        self,
        model: Optional[type] = None,
        properties: Optional[Properties] = None,
        additional_properties: Optional[_DPType] = None,
        accept_only: Optional[list[str]] = None,
        free_form: bool = False
    ) -> None:
        self._model = model or dict
        self._properties = properties or {}

        if properties is not None \
                and len(set(k.name for k in properties.keys())) < len(properties):
            names = set()
            raise ValueError(
                "Conflicting property name(s) in Object: "
                + str(
                    [
                        k.name for k in properties.keys()
                        if k.name in names or names.add(k.name)
                    ]
                )
            )

        if additional_properties and accept_only:
            raise ValueError(
                f"Value of 'additional_properties' ({additional_properties}) "
                + f"conflicts with value of 'accept_only' ({accept_only})."
            )
        if additional_properties and free_form:
            raise ValueError(
                f"Value of 'additional_properties' ({additional_properties}) "
                + f"conflicts with value of 'free_form' ({free_form})."
            )
        if accept_only and free_form:
            raise ValueError(
                f"Value of 'accept_only' ({accept_only}) "
                + f"conflicts with value of 'free_form' ({free_form})."
            )
        self._additional_properties = additional_properties
        self._accept_only = accept_only
        self._free_form = free_form

    @staticmethod
    def _reject_unknown_args(accepted, loc):
        return Stage(
            primer=lambda json, **kwargs: next(
                (k for k in json.keys() if k not in accepted),
                None
            ),
            status=lambda primer, **kwargs:
                Responses.GOOD.status if not primer
                else Responses.UNKNOWN_PROPERTY.status,
            message=lambda primer, **kwargs:
                Responses.GOOD.msg if not primer
                else Responses.UNKNOWN_PROPERTY.msg.format(
                    primer,
                    loc,
                    ", ".join(map(lambda x: f"'{x}'", accepted))
                )
        )

    @staticmethod
    def _arg_exists_hard(k, loc):
        return Stage(
            primer=lambda json, **kwargs: k.origin in json,
            status=lambda primer, **kwargs:
                Responses.GOOD.status if primer
                else Responses.MISSING_REQUIRED.status,
            message=lambda primer, **kwargs:
                Responses.GOOD.msg if primer
                else Responses.MISSING_REQUIRED.msg.format(
                    loc,
                    k.origin
                )
        )

    @staticmethod
    def _arg_exists_soft(k):
        return Stage(
            primer=lambda json, **kwargs: k.origin in json,
            status=lambda primer, **kwargs:
                Responses.GOOD.status if primer
                else Responses.MISSING_OPTIONAL.status,
            message=lambda primer, **kwargs:
                "" if primer else Responses.MISSING_OPTIONAL.msg
        )

    @staticmethod
    def _arg_has_type(k, v, loc):
        return Stage(
            requires={k.name: Responses.GOOD.status},
            primer=lambda json, **kwargs: isinstance(json[k.origin], v.TYPE),
            status=lambda primer, **kwargs:
                Responses.GOOD.status if primer else Responses.BAD_TYPE.status,
            message=lambda primer, json, **kwargs:
                Responses.GOOD.msg if primer
                else Responses.BAD_TYPE.msg.format(
                    k.origin,
                    loc,
                    v.__name__,
                    type(json[k.origin]).__name__
                )
        )

    @staticmethod
    def _make_instance(k, v, loc):
        return Stage(
            requires={k.name: Responses.GOOD.status},
            primer=lambda json, **kwargs:
                v.make(json[k.origin], loc),
            export=lambda primer, **kwargs:
                {f"EXPORT_{k.name}": primer[0]}
                if primer[2] == Responses.GOOD.status
                else {},
            status=lambda primer, **kwargs: primer[2],
            message=lambda primer, **kwargs: primer[1]
        )

    @staticmethod
    def _set_default(k):
        if k.default is not None:
            # default is set
            return Stage(
                requires={k.name: Responses.MISSING_OPTIONAL.status},
                primer=k.default
                    if callable(k.default)
                    else lambda **kwargs: k.default,
                export=lambda primer, **kwargs:
                    {f"EXPORT_{k.name}": primer},
                status=lambda **kwargs: Responses.GOOD.status,
                message=lambda **kwargs: Responses.GOOD.msg
            )
        # default to None or omit completely
        return Stage(
            requires={k.name: Responses.MISSING_OPTIONAL.status},
            export=lambda primer, **kwargs:
                {f"EXPORT_{k.name}": None}
                if k.fill_with_none
                else {},
            status=lambda **kwargs: Responses.GOOD.status,
            message=lambda **kwargs: Responses.GOOD.msg
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
            status=lambda **kwargs: Responses.GOOD.status,
            message=lambda **kwargs: Responses.GOOD.msg
        )

    @staticmethod
    def _process_additional_properties(keys, dptype, loc):
        """
        Defines a `Stage` in which an `Object`-based `Pipeline` is built
        and executed. The `Object` contains `Properties` which appear in
        the `json` but not as `Property` in the original `Object`. This
        way, the given fields in the `json` can be validated regarding
        their type.

        Keyword arguments:
        keys -- list of field names defined in the original `Object`
        dptype -- `_DPType` of the additional properties
        loc -- position in original `json`
        """
        return Stage(
            primer=lambda json, **kwargs: Object(
                    properties={
                        Property(k): dptype for k in additional
                    }
                ).assemble(loc).run(json=json)
                if len(
                    additional := [k for k in json.keys() if k not in keys]
                ) > 0
                else None,  # return None if Object is empty > simply return with
                            # Responses.GOOD
            action=lambda out, primer, **kwargs:
                [
                    out.update({"kwargs": {}})
                    if "kwargs" not in out
                    else None,
                    out.kwargs.update(primer.data.get("kwargs", {}))
                ]
                if primer and primer.last_status == Responses.GOOD.status
                else None,
            status=lambda primer, **kwargs:
                primer.last_status if primer else Responses.GOOD.status,
            message=lambda primer, **kwargs:
                primer.last_message if primer else Responses.GOOD.msg,
        )

    @staticmethod
    def _process_free_form(keys):
        """
        Defines a `Stage` that collects the json-content that is not
        defined as `Properties` in the original `Object` and adds those
        to the output `kwargs`.

        Keyword arguments:
        keys -- list of field names defined in the original `Object`
        """
        return Stage(
            primer=lambda json, **kwargs:
                {k: v for k, v in json.items() if k not in keys},
            action=lambda out, primer, **kwargs:
                [
                    out.update({"kwargs": {}})
                    if "kwargs" not in out
                    else None,
                    out.kwargs.update(primer)
                ],
            status=lambda **kwargs: Responses.GOOD.status,
            message=lambda **kwargs: Responses.GOOD.msg,
        )

    def make(self, json, loc: str) -> tuple[Any, str, int]:
        """
        Validate and instantiate type based on `json`.

        Returns with a tuple of
        * object if valid or None,
        * problem description if invalid,
        * status code (`Responses.GOOD` if valid)

        Keyword arguments:
        json -- data to generate object from
        loc -- current location in validation process for generating
               informative messages
        """
        output = self.assemble(loc).run(json=json)
        return (
            (
                output.data.value
                if output.last_status == Responses.GOOD.status
                else None
            ),
            output.last_message or Responses.GOOD.msg,
            output.last_status or Responses.GOOD.status
        )

    def assemble(self, _loc: Optional[str] = None) -> Pipeline:
        """
        Returns `Pipeline` that processes a `json`-input.
        """
        def finalizer(data, **kwargs):
            data.value = self._model(**data.kwargs)
        p = Pipeline(
            exit_on_status=lambda status: status >= 400,
            initialize_output=Output,
            finalize_output=finalizer
        )
        __loc = _loc or "."
        if self._accept_only is not None:
            p.append(
                __loc,
                **{__loc: self._reject_unknown_args(self._accept_only, __loc)}
            )
        elif self._additional_properties is not None:
            # additional properties
            p.append(
                f"{__loc}[additionalProperties]",
                **{
                    f"{__loc}[additionalProperties]":
                        self._process_additional_properties(
                            [k.origin for k in self._properties.keys()],
                            self._additional_properties,
                            _loc
                        )
                }
            )
        elif self._free_form:
            # free-form
            p.append(
                f"{__loc}[freeForm]",
                **{
                    f"{__loc}[freeForm]":
                        self._process_free_form(
                            [k.origin for k in self._properties.keys()]
                        )
                }
            )
        for k, v in self._properties.items():
            # k.name: validate existence
            if k.required and k.default is None:
                p.append(
                    k.name,
                    **{k.name: self._arg_exists_hard(k, __loc)}
                )
            else:
                p.append(k.name, **{k.name: self._arg_exists_soft(k)})
            # {k.name}[type]: validate type
            p.append(
                f"{k.name}[type]",
                **{f"{k.name}[type]": self._arg_has_type(k, v, __loc)}
            )
            # {k.name}[dptype]: validate, make, and export instance as
            #                   f"EXPORT_{k.name}" (if valid)
            p.append(
                f"{k.name}[dptype]",
                **{f"{k.name}[dptype]": self._make_instance(
                    k, v, (_loc or "") + "." + k.origin
                )}
            )
            if k.validation_only:
                continue
            # {k.name}[default]: apply default if required (or set None
            #   if property has fill_with_none set) and export as
            #   f"EXPORT_{k.name}"
            p.append(
                f"{k.name}[default]",
                **{f"{k.name}[default]": self._set_default(k)}
            )
            # {k.name}[output]: output to data
            p.append(
                f"{k.name}[output]",
                **{f"{k.name}[output]": self._output(k)}
            )

        return p
