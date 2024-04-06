from typing import TypeAlias, Mapping, Optional
from dataclasses import dataclass
from functools import partial

from data_plumber import Pipeline, Stage

from data_plumber_flask.keys import _DPKey
from . import _DPType

Properties: TypeAlias = Mapping[_DPKey, "_DPType | Properties"]


@dataclass
class _ProblemInfo:
    status: int
    msg: str


class Responses():
    GOOD = _ProblemInfo(0, "")
    MISSING_OPTIONAL = _ProblemInfo(1, "")
    MISSING_REQUIRED = _ProblemInfo(400, "Missing required")
    BAD_TYPE = _ProblemInfo(422, "Bad type.")


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
                             this `Object`
                             (default `None`)
    """
    TYPE = dict

    def __init__(
        self,
        model: Optional[type] = None,
        properties: Optional[Properties] = None,
        additional_properties: Optional[_DPType] = None
    ) -> None:
        self._model = model or dict
        self._properties = properties

        if len(set(k.name for k in properties.keys())) < len(properties):
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

        self._additional_properties = additional_properties

    @staticmethod
    def _arg_exists_hard(k):
        return Stage(
            primer=lambda json, **kwargs: k.origin in json,
            status=lambda primer, **kwargs:
                0 if primer else Responses.MISSING_REQUIRED.status,
            message=lambda primer, **kwargs:
                "" if primer else Responses.MISSING_REQUIRED.msg
        )

    @staticmethod
    def _arg_exists_soft(k):
        return Stage(
            primer=lambda json, **kwargs: k.origin in json,
            status=lambda primer, **kwargs:
                0 if primer else Responses.MISSING_OPTIONAL.status,
            message=lambda primer, **kwargs:
                "" if primer else Responses.MISSING_OPTIONAL.msg
        )

    @staticmethod
    def _arg_has_type(k, v):
        return Stage(
            requires={k.origin: Responses.GOOD.status},
            primer=lambda json, **kwargs: isinstance(json[k.origin], v.TYPE),
            status=lambda primer, **kwargs:
                0 if primer else Responses.BAD_TYPE.status,
            message=lambda primer, **kwargs:
                "" if primer else Responses.BAD_TYPE.msg
        )

    @staticmethod
    def _output(k):
        return Stage(
            requires={k.origin: Responses.GOOD.status},
            action=lambda out, json, **kwargs:
                out.update({k.name: json[k.origin]})
        )

    @staticmethod
    def _set_default(k):
        if k.fill_with_none:
            return Stage(
                requires={k.origin: Responses.MISSING_OPTIONAL.status},
                primer=k.default
                    if callable(k.default)
                    else lambda **kwargs: k.default,
                action=lambda primer, out, json, **kwargs:
                    out.update({k.name: primer})
            )
        return Stage(
            requires={k.origin: Responses.MISSING_OPTIONAL.status},
            primer=k.default
                if callable(k.default)
                else lambda **kwargs: k.default,
            action=lambda primer, out, json, **kwargs:
                None if primer is None else out.update({k.name: primer})
        )

    def assemble(self) -> Pipeline:
        """
        Returns `Pipeline` that processes a `json`-input.
        """
        def finalizer(data, **kwargs):
            data = self._model(**data)
        p = Pipeline(
            exit_on_status=lambda status: status >= 400,
            finalize_output=finalizer
        )
        for k, v in self._properties.items():
            if k.required and k.default is None:
                p.append(k.origin, **{k.origin: self._arg_exists_hard(k)})
            else:
                p.append(k.origin, **{k.origin: self._arg_exists_soft(k)})
            p.append(self._arg_has_type(k, v))
            # TODO: add v.validate()-Stage
            # TODO: add model-specific validation
            p.append(self._output(k))
            p.append(self._set_default(k))
        return p
