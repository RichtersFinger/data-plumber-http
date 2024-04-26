"""
Part of the test suite for data-plumber-flask.

Run with
pytest -v -s --cov=data_plumber_http.keys --cov=data_plumber_http.types --cov=data_plumber_http.decorators
"""

import pytest

from data_plumber_http.keys import Property
from data_plumber_http.types import Boolean, Object, String
from data_plumber_http.types import Responses


def test_object_additional_properties_accept_only():
    """
    Test conflict with `additional_properties` and `accept_only` in `Object`.
    """

    with pytest.raises(ValueError):
        Object(
            additional_properties=String(),
            accept_only=["string"]
        )


def test_object_additional_properties():
    """Test property `additional_properties` in `Object`."""

    json = {"string": "string1", "another-string": "string2"}
    output = Object(
        additional_properties=String(),
    ).assemble().run(json=json)
    assert output.last_status == Responses.GOOD.status
    assert output.data.value == json


def test_object_properties_and_additional_properties():
    """Test properties `properties` and `additional_properties` in `Object`."""

    json = {"string": "string1", "object": {"string": "string2"}}
    output = Object(
        properties={
            Property("object"): Object(
                properties={Property("string"): String()}
            )
        },
        additional_properties=String(),
    ).assemble().run(json=json)
    assert output.last_status == Responses.GOOD.status
    assert output.data.value == json


def test_object_additional_properties_none_given():
    """Test property `additional_properties` in `Object`."""

    json = {}
    output = Object(
        additional_properties=String(),
    ).assemble().run(json=json)
    assert output.last_status == Responses.GOOD.status
    assert output.data.value == json


def test_object_property_and_additional_properties_none_given():
    """Test property `additional_properties` in `Object`."""

    json = {"string": "string1"}
    output = Object(
        properties={
            Property("string"): String()
        },
        additional_properties=String(),
    ).assemble().run(json=json)
    assert output.last_status == Responses.GOOD.status
    assert output.data.value == json


def test_object_additional_properties_bad_types():
    """Test property `additional_properties` in `Object`."""

    json = {"string": "string1"}
    output = Object(
        additional_properties=Boolean(),
    ).assemble().run(json=json)
    print(output.last_message)
    assert output.last_status == Responses.BAD_TYPE.status


@pytest.mark.parametrize(
    ("pipeline", "status"),
    [
        (Object().assemble(), Responses.GOOD.status),
        (Object(additional_properties=True).assemble(), Responses.GOOD.status),
        (
            Object(additional_properties=False).assemble(),
            Responses.UNKNOWN_PROPERTY.status
        ),
    ],
    ids=["default", "True", "False"]
)
def test_object_additional_properties_boolean_minimal(pipeline, status):
    """
    Test boolean value for property `additional_properties` in `Object`.
    """

    output = pipeline.run(json={"string": "string1"})
    if output.last_status != Responses.GOOD.status:
        print(output.last_message)
    assert output.last_status == status


@pytest.mark.parametrize(
    "json",
    [
        {"string": "string1"},
        {"another-string": "string1"},
    ],
    ids=["string_in_json", "another_string_in_json"]
)
@pytest.mark.parametrize(
    "additional_properties",
    [True, False]
)
def test_object_additional_properties_boolean_non_empty(
    json, additional_properties
):
    """
    Test boolean value for property `additional_properties` in non-
    trivial `Object`.
    """

    output = Object(
        properties={
            Property("string"): String()
        },
        additional_properties=additional_properties
    ).assemble().run(json=json)

    if output.last_status != Responses.GOOD.status:
        print(output.last_message)
    if "string" in json or additional_properties:
        assert output.last_status == Responses.GOOD.status
    else:
        assert output.last_status == Responses.UNKNOWN_PROPERTY.status
