from dataclasses import dataclass


@dataclass
class ProblemInfo:
    status: int
    msg: str


class Responses:
    GOOD = ProblemInfo(0, "OK")
    MISSING_OPTIONAL = ProblemInfo(1, "Missing optional arg.")
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
    MISSING_REQUIRED_ONEOF = ProblemInfo(
        400,
        "No match for required OneOf '{}' in '{}' ({})."
    )
    BAD_VALUE_IN_ONEOF = ProblemInfo(
        0,  # gets overridden by child-status
        "Bad value encountered in OneOf '{}' in '{}' ({})."
    )
    MULTIPLE_ONEOF = ProblemInfo(
        400,
        "Multiple matches ('{}') for OneOf '{}' in '{}'."
    )
    MISSING_REQUIRED_ALLOF = ProblemInfo(
        400,
        "Missing parts for required AllOf '{}' in '{}' ({})."
    )
    BAD_VALUE_IN_ALLOF = ProblemInfo(
        0,  # gets overridden by child-status
        "Bad value encountered in AllOf '{}' in '{}' ({})."
    )
