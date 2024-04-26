from dataclasses import dataclass


@dataclass
class ProblemInfo:
    status: int
    msg: str


class Responses:
    GOOD = ProblemInfo(0, "")
    MISSING_OPTIONAL = ProblemInfo(1, "")
    UNKNOWN_PROPERTY = ProblemInfo(
        400,
        "Argument '{}' in '{}' not allowed (accepted: {})."
    )
    MISSING_REQUIRED = ProblemInfo(
        400,
        "Object '{}' missing required property '{}'."
    )
    BAD_TYPE = ProblemInfo(
        422,
        "Argument '{}' in '{}' has bad type. Expected '{}' but found '{}'."
    )
    BAD_VALUE = ProblemInfo(
        422,
        "Value '{}' in '{}' not allowed (expected {})."
    )
    RESOURCE_NOT_FOUND = ProblemInfo(
        404,
        "Could not find requested resource '{}' given in '{}'."
    )
    CONFLICT = ProblemInfo(
        409,
        "Resource '{}' given in '{}' conflicts with existing resource."
    )
