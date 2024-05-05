from typing import Optional, Callable, Any

from data_plumber import Pipeline, Stage

from data_plumber_http.output import Output
from data_plumber_http.settings import Responses
from .conditional_key import _ConditionalKey


class AllOf(_ConditionalKey):
    """
    An `AllOf` paired with a `Mapping` can be passed to an `Object`
    constructor (`properties` argument) as a form of conditional
    request body validation. It is processed such that only one of
    the properties in the associated `Mapping` are included in the
    output.

    Keyword arguments:
    name -- name identifier for this key
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
        name: str,
        default: Optional[Callable[..., Any] | Any] = None,
        required: bool = False,
        validation_only: bool = False
    ) -> None:
        self.name = name
        self.default = default
        self.required = required
        self.validation_only = validation_only

    def get_origins(self, value):
        origins = []
        for k, v in value.items():
            origins.extend(k.get_origins(v))
        return origins

    @staticmethod
    def _arg_exists_hard(loc, name):
        def status(primer, json, EXPORT_options, **kwargs):
            if len(primer) == 0:
                return Responses().GOOD.status
            for k in json:
                if k in EXPORT_options \
                        and EXPORT_options[k].last_status != Responses().GOOD.status:
                    return EXPORT_options[k].last_status
            return Responses().MISSING_REQUIRED_ALLOF.status

        return Stage(
            primer=lambda EXPORT_options, EXPORT_matches, **kwargs:
                set(EXPORT_options.keys()).difference(set(EXPORT_matches)),
            status=status,
            message=lambda primer, EXPORT_options, **kwargs:
                Responses().GOOD.msg if len(primer) == 0
                else Responses().MISSING_REQUIRED_ALLOF.msg.format(
                    name,
                    loc,
                    ", ".join(
                        map(
                            lambda x: f"'{x}': \"{EXPORT_options[x].last_message}\"",
                            primer
                        )
                    )
                )
        )

    @staticmethod
    def _arg_exists_soft(loc, name):
        def status(primer, json, EXPORT_options, **kwargs):
            if len(primer) == 0:
                return Responses().GOOD.status
            for k in json:
                if k in EXPORT_options \
                        and EXPORT_options[k].last_status != Responses().GOOD.status:
                    return EXPORT_options[k].last_status
            return Responses().MISSING_OPTIONAL.status

        def message(primer, json, EXPORT_options, **kwargs):
            if len(primer) == 0:
                return Responses().GOOD.msg
            for k in json:
                if k in EXPORT_options:
                    return Responses().BAD_VALUE_IN_ALLOF.msg.format(
                        name,
                        loc,
                        EXPORT_options[k].last_message
                    )
            return Responses().MISSING_OPTIONAL.msg

        return Stage(
            primer=lambda EXPORT_options, EXPORT_matches, **kwargs:
                set(EXPORT_options.keys()).difference(set(EXPORT_matches)),
            status=status,
            message=message
        )

    @staticmethod
    def _output():
        return Stage(
            action=lambda out, EXPORT_options, EXPORT_matches, **kwargs:
                [
                    out.update({"kwargs": {}})
                    if "kwargs" not in out
                    else None,
                    [
                        out.kwargs.update(EXPORT_options[v].data.kwargs)
                        for v in EXPORT_matches
                    ]
                ],
            status=lambda **kwargs: Responses().GOOD.status,
            message=lambda **kwargs: Responses().GOOD.msg
        )

    def assemble(self, value, loc):
        p = Pipeline(
            exit_on_status=lambda status: status >= 400,
            initialize_output=Output
        )
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
                **{
                    f"{self.name}[exists]":
                        self._arg_exists_soft(_loc, self.name)
                }
            )

        # stop here if requested
        if self.validation_only:
            return p

        # set default
        if self.default is not None:
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
