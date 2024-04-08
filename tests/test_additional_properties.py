"""
Part of the test suite for data-plumber-flask.

Run with
pytest -v -s --cov=data_plumber_flask.keys --cov=data_plumber_flask.types
"""

import pytest

from data_plumber_flask.keys import AllOf, OneOf, Property
from data_plumber_flask.types \
    import Array, Boolean, Float, Integer, Number, Object, String
from data_plumber_flask.types import Responses


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
    assert output.data["value"] == json


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
    assert output.data["value"] == json


def test_object_additional_properties_none_given():
    """Test property `additional_properties` in `Object`."""

    json = {}
    output = Object(
        additional_properties=String(),
    ).assemble().run(json=json)
    assert output.last_status == Responses.GOOD.status
    assert output.data["value"] == json


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
    assert output.data["value"] == json


def test_object_additional_properties_bad_types():
    """Test property `additional_properties` in `Object`."""

    json = {"string": "string1"}
    output = Object(
        additional_properties=Boolean(),
    ).assemble().run(json=json)
    print(output.last_message)
    assert output.last_status == Responses.BAD_TYPE.status
