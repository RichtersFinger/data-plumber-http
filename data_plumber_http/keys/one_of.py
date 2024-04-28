from typing import TypeAlias, Mapping, Optional, Callable, Any

from data_plumber import Pipearray, Pipeline, Stage
from data_plumber.output import PipelineOutput

from data_plumber_http.output import Output
from data_plumber_http.settings import Responses
from . import DPKey, Property


Options: TypeAlias = Mapping[DPKey, "DPType | Options"]


class OneOf(DPKey):
    """
    A `OneOf` paired with a `Mapping` can be passed to an `Object`
    constructor (`properties` argument) as a form of a conditional
    request body validation. It is processed such that only one of
    the properties in the associated `Mapping` are included in the
    output.

    Keyword arguments:
    name -- name identifier for this key
    exclusive -- if `True`, require that exactly one match is made
                 (default `True`)
    default -- either static value or callable taking input kwargs; used
               as default if property is missing in request
               (default `None`)
    required -- if `True`, this property is marked as required
                (default `False`)
    fill_with_none -- if `True`, fill fields of missing arguments
                      without default with `None`
                      (default `False`)
    validation_only -- skip exporting this property to the resulting
                       data and only perform validation
                       (default `False`)
    """

    def __init__(
        self,
        name: str,
        exclusive: bool = True,
        default: Optional[Callable[..., Any] | Any] = None,
        required: bool = False,
        fill_with_none: bool = False,
        validation_only: bool = False
    ) -> None:
        self.exclusive = exclusive
        self.name = name
        self.default = default
        self.required = required
        self.fill_with_none = fill_with_none
        self.validation_only = validation_only

    @staticmethod
    def _normalize(dpkey):
        """
        Returns normalized `DPKey` to be used inside `OneOf`.

        This measure is required to get insightful status-response from
        `Pipearray`.
        """
        # TODO: raise Error/warn if non-default settings for default
        # etc. are used
        if isinstance(dpkey, Property):
            return Property(
                origin=dpkey.origin, name=dpkey.name, required=True
            )
        return type(dpkey)(required=True)

    @classmethod
    def _run_options(cls, options: Options, loc: str) -> Stage:
        pa = Pipearray(
            **{
                k.origin: cls._normalize(k).assemble(v, loc)
                for k, v in options.items()
            }
        )
        return Stage(
            primer=lambda json, **kwargs: pa.run(json=json),
            export=lambda primer, **kwargs:
                {
                    "EXPORT_options": primer,
                    "EXPORT_matches": [
                        k for k, v in primer.items()
                        if v.last_status == Responses.GOOD.status
                    ]
                },
            status=lambda **kwargs: Responses.GOOD.status,
            message=lambda **kwargs: Responses.GOOD.msg
        )

    @staticmethod
    def _arg_exists_hard(loc, name):
        return Stage(
            status=lambda EXPORT_matches, **kwargs:
                Responses.GOOD.status if EXPORT_matches
                else Responses.MISSING_REQUIRED_ONEOF.status,
            message=lambda EXPORT_matches, **kwargs:
                Responses.GOOD.msg if EXPORT_matches
                else Responses.MISSING_REQUIRED_ONEOF.msg.format(
                    name,
                    loc
                )
        )

    @staticmethod
    def _arg_exists_soft():
        return Stage(
            status=lambda EXPORT_matches, **kwargs:
                Responses.GOOD.status if EXPORT_matches
                else Responses.MISSING_OPTIONAL.status,
            message=lambda EXPORT_matches, **kwargs:
                "" if EXPORT_matches else Responses.MISSING_OPTIONAL.msg
        )

    @staticmethod
    def _exclusive_match(loc, name):
        return Stage(
            requires={f"{name}[exists]": Responses.GOOD.status},
            status=lambda EXPORT_matches, **kwargs:
                Responses.GOOD.status if len(EXPORT_matches) == 1
                else Responses.MULTIPLE_ONEOF.status,
            message=lambda EXPORT_matches, **kwargs:
                Responses.GOOD.msg if len(EXPORT_matches) == 1
                else Responses.MULTIPLE_ONEOF.msg.format(
                    EXPORT_matches,
                    name,
                    loc
                )
        )

    @staticmethod
    def _set_default(k):
        if k.default is not None:
            # default is set
            return Stage(
                requires={
                    f"{k.name}[exists]": Responses.MISSING_OPTIONAL.status
                },
                primer=k.default
                    if callable(k.default)
                    else lambda **kwargs: k.default,
                export=lambda primer, **kwargs:
                    {
                        "EXPORT_options": {
                            "default": PipelineOutput(
                                [], {}, Output(kwargs={k.name: primer})
                            )
                        },
                        "EXPORT_matches": ["default"],
                    },
                status=lambda **kwargs: Responses.GOOD.status,
                message=lambda **kwargs: Responses.GOOD.msg
            )
        # default to None or omit completely
        return Stage(
            requires={
                f"{k.name}[exists]": Responses.MISSING_OPTIONAL.status
            },
            export=lambda primer, **kwargs:
                {
                    "EXPORT_options": {
                        "default": PipelineOutput(
                            [], {}, Output(kwargs={k.name: None})
                        )
                    },
                    "EXPORT_matches": ["default"],
                }
                if k.fill_with_none
                else {},
            status=lambda **kwargs: Responses.GOOD.status,
            message=lambda **kwargs: Responses.GOOD.msg
        )

    @staticmethod
    def _output():
        return Stage(
            primer=lambda EXPORT_options, EXPORT_matches, **kwargs:
                EXPORT_options[EXPORT_matches[0]].data.kwargs if EXPORT_matches
                else {},
            action=lambda out, primer, **kwargs:
                [
                    out.update({"kwargs": {}})
                    if "kwargs" not in out
                    else None,
                    out.kwargs.update(primer)
                ],
            status=lambda **kwargs: Responses.GOOD.status,
            message=lambda **kwargs: Responses.GOOD.msg
        )

    def assemble(self, value: Options, loc: Optional[str]) -> Pipeline:
        p = Pipeline()
        _loc = loc or "."

        # run options
        p.append(
            f"{self.name}[options]",
            **{f"{self.name}[options]": self._run_options(value, _loc)}
        )

        # evaluate options
        # validate existence
        if self.required and self.default is None:
            p.append(
                f"{self.name}[exists]",
                **{
                    f"{self.name}[exists]":
                        self._arg_exists_hard(_loc, self.name)
                }
            )
        else:
            p.append(
                f"{self.name}[exists]",
                **{f"{self.name}[exists]": self._arg_exists_soft()}
            )

        # validate exclusiveness
        if self.exclusive:
            p.append(
                f"{self.name}[exclusive]",
                **{
                    f"{self.name}[exclusive]":
                        self._exclusive_match(_loc, self.name)
                }
            )

        # stop here if requested
        if self.validation_only:
            return p

        # set default
        p.append(
            f"{self.name}[default]",
            **{f"{self.name}[default]": self._set_default(self)}
        )

        # output
        p.append(
            f"{self.name}[output]",
            **{f"{self.name}[output]": self._output()}
        )

        return p
