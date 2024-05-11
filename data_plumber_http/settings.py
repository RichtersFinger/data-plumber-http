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
    warn_on_change = False
    GOOD = ProblemInfo(
        "OK", 0
    )
    MISSING_OPTIONAL = ProblemInfo(
        "Missing optional arg.", 1
    )
    UNKNOWN_PROPERTY = ProblemInfo(
        "Argument '{origin}' in '{loc}' not allowed ({accepted}).",
        400
    )
    MISSING_REQUIRED = ProblemInfo(
        "Object '{loc}' missing required property '{origin}'.",
        400
    )
    BAD_TYPE = ProblemInfo(
        "Argument '{origin}' in '{loc}' has bad type. Expected '{xp_type}' but found '{fnd_type}'.",
        422
    )
    BAD_VALUE = ProblemInfo(
        "Value '{origin}' in '{loc}' not allowed (expected {expected}).",
        422
    )
    RESOURCE_NOT_FOUND = ProblemInfo(
        "Could not find requested resource '{res}' given in '{loc}'.",
        404
    )
    CONFLICT = ProblemInfo(
        "Resource '{res}' given in '{loc}' conflicts with existing resource.",
        409
    )
    MISSING_REQUIRED_ONEOF = ProblemInfo(
        "Expected at least one match for one of {options} in '{loc}' ({details}).",
        400
    )
    BAD_VALUE_IN_ONEOF = ProblemInfo(
        "{child}",  # filled with child's message
        2  # gets overridden by child's status
    )
    MULTIPLE_ONEOF = ProblemInfo(
        "Expected exclusive match among {property} {options} in '{loc}' (got matches {matches}).",
        400
    )
    MISSING_REQUIRED_ALLOF = ProblemInfo(
        "Missing or invalid required {property} {missing} in '{loc}' ({details}).",
        400
    )
    BAD_VALUE_IN_ALLOF = ProblemInfo(
        "{child}",  # filled with child's message
        2  # gets overridden by child's status
    )

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
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

    def get(self, name: str) -> ProblemInfo:
        """
        Returns the `ProblemInfo`-object associated with `name`.

        Keyword arguments:
        name -- response name identifier
        """
        return getattr(self, name)


# finalize initialization of singleton
Responses()
