from typing import TypeAlias, Mapping, Optional, Callable, Any

from data_plumber import Pipeline, Stage
from data_plumber.output import StageRecord

from data_plumber_http.output import Output
from data_plumber_http.keys import DPKey, Property
from . import DPType, Responses


Properties: TypeAlias = Mapping[DPKey, "DPType | Properties"]


class Object(DPType):
    """
    An `Object` corresponds to the JSON-type 'object'.

    Keyword arguments:
    model -- data model or factory for this `Object` (gets passed the
             entire output of a validation-run as kwargs)
             (default `None`; corresponds to dictionary)
    properties -- mapping for explicitly expected contents of this
                  `Object`
                  (default `None`)

    Mutually exclusive arguments:
    additional_properties -- either boolean or field type (`DPType`)
                             boolean: if `True`, ignore any additional
                             fields; if `False`, respond with
                             `Responses().UNKNOWN_PROPERTY` for fields
                             that are not listed in `properties`
                             type: required type specification for
                             implicitly expected contents of this
                             `Object`; corresponding fields in `json`
                             are added to the output
                             (default `None`; treated like `True`)
    accept_only -- if set, on execution a `json` is rejected with
                   `Responses().UNKNOWN_PROPERTY` if it contains a key
                   that is not in `accept_only`
                   (default `None`)
    free_form -- if `True`, accept and use any content that has not been
                 defined explicitly via `properties`
                 (default `False`)
    """
    TYPE = dict

    def __init__(
        self,
        model: Optional[type | Callable[..., Any]] = None,
        properties: Optional[Properties] = None,
        additional_properties: Optional[bool | DPType] = None,
        accept_only: Optional[list[str]] = None,
        free_form: bool = False
    ) -> None:
        self._model = model or dict
        self.properties = properties or {}

        if properties is not None:
            _properties: Optional[list[Property]] = list(
                k for k in properties.keys() if isinstance(k, Property)
            )
        else:
            _properties = properties
        if _properties is not None \
                and len(set(k.name for k in _properties)) < len(_properties):
            names = set()
            raise ValueError(
                "Conflicting property name(s) in Object: "
                + str(
                    [
                        k.name for k in _properties
                        if k.name in names or names.add(k.name)  # type: ignore [func-returns-value]
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
        self._free_form = free_form
        self._accept_only = accept_only
        if isinstance(additional_properties, bool):
            self._additional_properties = additional_properties
            self._additional_properties_typespec = None
            if not additional_properties:
                self._accept_only = list(set().union(
                    *[
                        k.get_origins(v)
                        for k, v in properties.items()
                    ]
                )) if properties is not None else []
        else:
            self._additional_properties = True
            self._additional_properties_typespec = additional_properties

    @staticmethod
    def _reject_unknown_args(accepted, loc):
        return Stage(
            primer=lambda json, **kwargs: next(
                (k for k in json.keys() if k not in accepted),
                None
            ),
            status=lambda primer, **kwargs:
                Responses().GOOD.status if not primer
                else Responses().UNKNOWN_PROPERTY.status,
            message=lambda primer, **kwargs:
                Responses().GOOD.msg if not primer
                else Responses().UNKNOWN_PROPERTY.msg.format(
                    origin=primer,
                    loc=loc,
                    accepted="accepted: " + ", ".join(map(lambda x: f"'{x}'", accepted))
                        if len(accepted) > 0 else "none accepted"
                )
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
        dptype -- `DPType` of the additional properties
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
                            # Responses().GOOD
            action=lambda out, primer, **kwargs:
                [
                    out.update({"kwargs": {}})
                    if "kwargs" not in out
                    else None,
                    out.kwargs.update(primer.data.get("kwargs", {}))
                ]
                if primer and primer.last_status == Responses().GOOD.status
                else None,
            status=lambda primer, **kwargs:
                primer.last_status if primer else Responses().GOOD.status,
            message=lambda primer, **kwargs:
                primer.last_message if primer else Responses().GOOD.msg,
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
            status=lambda **kwargs: Responses().GOOD.status,
            message=lambda **kwargs: Responses().GOOD.msg,
        )

    def make(self, json, loc: str) -> tuple[Any, str, int]:
        """
        Validate and instantiate type based on `json`.

        Returns with a tuple of
        * object if valid or None,
        * problem description if invalid,
        * status code (`Responses().GOOD` if valid)

        Keyword arguments:
        json -- data to generate object from
        loc -- current location in validation process for generating
               informative messages
        """
        output = self.assemble(loc).run(json=json)
        return (
            (
                output.data.value
                if output.last_status == Responses().GOOD.status
                else None
            ),
            output.last_message or Responses().GOOD.msg,
            output.last_status or Responses().GOOD.status
        )

    def assemble(self, _loc: Optional[str] = None) -> Pipeline:
        """
        Returns `Pipeline` that processes a `json`-input.
        """
        def finalizer(data, records, **kwargs):
            try:
                if records[-1].status == Responses().GOOD.status:
                    data.value = self._model(**data.kwargs)
            except IndexError:  # empty Object
                records.append(StageRecord(
                    0, "finalizer", Responses().GOOD.msg, Responses().GOOD.status
                ))
                data.value = self._model()
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
        if self._additional_properties_typespec is not None:
            # additional properties
            p.append(
                f"{__loc}[additionalProperties]",
                **{
                    f"{__loc}[additionalProperties]":
                        self._process_additional_properties(
                            list(set().union(
                                *[
                                    k.get_origins(v)
                                    for k, v in self.properties.items()
                                ]
                            )),
                            self._additional_properties_typespec,
                            _loc
                        )
                }
            )
        if self._free_form:
            # free-form
            p.append(
                f"{__loc}[freeForm]",
                **{
                    f"{__loc}[freeForm]":
                        self._process_free_form(
                            list(set().union(
                                *[
                                    k.get_origins(v)
                                    for k, v in self.properties.items()
                                ]
                            ))
                        )
                }
            )
        for k, v in self.properties.items():
            p.append(k.assemble(v, _loc))

        return p
