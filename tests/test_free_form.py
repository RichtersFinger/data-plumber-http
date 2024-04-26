"""
Part of the test suite for data-plumber-flask.

Run with
pytest -v -s --cov=data_plumber_http.keys --cov=data_plumber_http.types --cov=data_plumber_http.decorators
"""

import pytest

from data_plumber_http.keys import Property
from data_plumber_http.types import Object, String
from data_plumber_http.settings import Responses


def test_object_additional_properties_free_form():
    """
    Test conflict with `additional_properties` and `free_form` in `Object`.
    """

    with pytest.raises(ValueError):
        Object(
            additional_properties=String(),
            free_form=True
        )


def test_object_accept_only_free_form():
    """
    Test conflict with `accept_only` and `free_form` in `Object`.
    """

    with pytest.raises(ValueError):
        Object(
            accept_only=["string"],
            free_form=True
        )


@pytest.mark.parametrize(
    "json",
    [
        {},
        {"string": "string1"},
        {"string": "string1", "boolean": True},
        {"string": "string1", "object": {"string": "string2"}},
    ]
)
def test_object_free_form_full(json):
    """Test free-form-`Object`."""

    output = Object(
        properties={
            Property("object"): Object(free_form=True)
        }
    ).assemble().run(json={"object": json})

    assert output.last_status == Responses.GOOD.status
    assert output.data.value["object"] == json


@pytest.mark.parametrize(
    ("json", "status"),
    [
        ({"string": "string1", "object": {}}, Responses.GOOD.status),
        ({"object": {}}, Responses.GOOD.status),
        ({"object": {"another-string": "string2"}}, Responses.GOOD.status),
        (
            {"object": {"another-string": "string2", "something-else": True}},
            Responses.GOOD.status
        ),
        ({"object": {"another-string": False}}, Responses.BAD_TYPE.status),
    ]
)
def test_object_free_form_partial(json, status):
    """Test free-form-`Object`."""

    output = Object(
        properties={
            Property("string"): String(),
            Property("object"): Object(
                properties={
                    Property("another-string"): String()
                },
                free_form=True
            )
        }
    ).assemble().run(json=json)

    assert output.last_status == status
    if status == Responses.GOOD.status:
        assert output.data.value == json
    else:
        print(output.last_message)


def test_object_free_form_with_model():
    """Test free-form-`Object` with model."""

    class SomeModel:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    json = {"string": "string1", "object": {"string": "string2"}}
    output = Object(
        properties={
            Property("object"): Object(model=SomeModel, free_form=True)
        }
    ).assemble().run(json={"object": json})

    assert output.last_status == Responses.GOOD.status
    assert output.data.value["object"].kwargs == json
