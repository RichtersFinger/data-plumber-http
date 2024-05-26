
from data_plumber import Pipearray, Stage
from data_plumber.output import PipelineOutput

from data_plumber_http.output import Output
from data_plumber_http.settings import Responses
from . import DPKey, Property


class _ConditionalKey(DPKey):
    @staticmethod
    def _normalize(dpkey):
        """
        Returns normalized `DPKey` to be used inside `OneOf`.

        This measure is required to get insightful status-response from
        `Pipearray`.
        """
        if isinstance(dpkey, Property):
            return Property(
                origin=dpkey.origin, name=dpkey.name, required=True
            )
        return type(dpkey)(name=dpkey.name, required=True)

    def get_origins(self, value):
        origins = []
        for k, v in value.items():
            origins.extend(k.get_origins(v))
        return origins

    @classmethod
    def _run_options(cls, options, loc: str) -> Stage:
        pa = Pipearray(
            **{
                k.name: cls._normalize(k).assemble(v, loc)
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
                        if v.last_status == Responses().GOOD.status
                    ]
                },
            status=lambda **kwargs: Responses().GOOD.status,
            message=lambda **kwargs: Responses().GOOD.msg
        )

    @staticmethod
    def _set_default(k):
        return Stage(
            requires={
                f"{k.name}[exists]": Responses().MISSING_OPTIONAL.status
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
            status=lambda **kwargs: Responses().GOOD.status,
            message=lambda **kwargs: Responses().GOOD.msg
        )
