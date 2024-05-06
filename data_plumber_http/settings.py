from typing import Optional
from dataclasses import dataclass
import warnings


@dataclass
class ProblemInfo:
    msg: str
    status: int


class Responses:
    """
    Responses-singleton that stores a catalog of messages and status
    values for various occurrences during validation.
    """

    # pylint: disable=no-member
    _instance = None
    # define placeholders to prevent pylint's no-member-errors
    warn_on_change = False
    GOOD = ProblemInfo("", 0)
    MISSING_OPTIONAL = ProblemInfo("", 0)
    UNKNOWN_PROPERTY = ProblemInfo("", 0)
    MISSING_REQUIRED = ProblemInfo("", 0)
    BAD_TYPE = ProblemInfo("", 0)
    BAD_VALUE = ProblemInfo("", 0)
    RESOURCE_NOT_FOUND = ProblemInfo("", 0)
    CONFLICT = ProblemInfo("", 0)
    MISSING_REQUIRED_ONEOF = ProblemInfo("", 0)
    BAD_VALUE_IN_ONEOF = ProblemInfo("", 0)
    MULTIPLE_ONEOF = ProblemInfo("", 0)
    MISSING_REQUIRED_ALLOF = ProblemInfo("", 0)
    BAD_VALUE_IN_ALLOF = ProblemInfo("", 0)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.warn_on_change = False
            cls._instance.update(
                "GOOD", "OK", 0
            )
            cls._instance.update(
                "MISSING_OPTIONAL", "Missing optional arg.", 1
            )
            cls._instance.update(
                "UNKNOWN_PROPERTY",
                "Argument '{origin}' in '{loc}' not allowed ({accepted}).",
                400
            )
            cls._instance.update(
                "MISSING_REQUIRED",
                "Object '{loc}' missing required property '{origin}'.",
                400
            )
            cls._instance.update(
                "BAD_TYPE",
                "Argument '{origin}' in '{loc}' has bad type. Expected '{xp_type}' but found '{fnd_type}'.",
                422
            )
            cls._instance.update(
                "BAD_VALUE",
                "Value '{origin}' in '{loc}' not allowed (expected {expected}).",
                422
            )
            cls._instance.update(
                "RESOURCE_NOT_FOUND",
                "Could not find requested resource '{res}' given in '{loc}'.",
                404
            )
            cls._instance.update(
                "CONFLICT",
                "Resource '{res}' given in '{loc}' conflicts with existing resource.",
                409
            )
            cls._instance.update(
                "MISSING_REQUIRED_ONEOF",
                "Expected at least one match for one of {options} in '{loc}' ({details}).",
                400
            )
            cls._instance.update(
                "BAD_VALUE_IN_ONEOF",
                "{child}",  # filled with child's message
                2  # gets overridden by child's status
            )
            cls._instance.update(
                "MULTIPLE_ONEOF",
                "Expected exclusive match among {property} {options} in '{loc}' (got matches {matches}).",
                400
            )
            cls._instance.update(
                "MISSING_REQUIRED_ALLOF",
                "Missing or invalid required {property} {missing} in '{loc}' ({details}).",
                400
            )
            cls._instance.update(
                "BAD_VALUE_IN_ALLOF",
                "{child}",  # filled with child's message
                2  # gets overridden by child's status
            )
            cls._instance.warn_on_change = False
            cls._instance.INTERNAL_RESPONSES = list(
                k for k, v in cls.__dict__.items()
                if isinstance(v, ProblemInfo)
            )
            cls._instance.warn_on_change = True
        return cls._instance

    def _warn(self, name: str) -> None:
        if self.warn_on_change and name in self.INTERNAL_RESPONSES:
            warnings.warn(
                f"Changing internally defined response '{name}' can break "
                + "functionality. (Set 'Responses().warn_on_change' to 'False'"
                + " to remove this message.)"
            )

    def new(
        self, name: str, msg: str, status: int, override: bool = False
    ) -> None:
        """
        Register new type of response.

        Keyword arguments:
        name -- response name identifier
        msg -- (unformatted) response message
        status -- response status
        override -- if `True`, override existing response
                    (default `False`)
        """
        if not override and hasattr(self, name):
            raise KeyError(
                f"Tried to create existing Response '{name}'. (Set 'override'"
                + " to 'True' to update existing.)"
            )
        self._warn(name)
        setattr(self, name, ProblemInfo(msg=msg, status=status))

    def update(
        self,
        name: str,
        msg: Optional[str] = None,
        status: Optional[int] = None
    ) -> None:
        """
        Update details of existing response.

        Keyword arguments:
        name -- response name identifier
        msg -- new (unformatted) response message
               (default `None`; leave unchanged)
        status -- new response status
                  (default `None`; leave unchanged)
        """
        if msg is not None:
            getattr(self, name).msg = msg
        if status is not None:
            self._warn(name)
            getattr(self, name).status = status


# finalize initialization of singleton
Responses()
