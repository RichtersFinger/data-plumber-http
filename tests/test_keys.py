"""
Part of the test suite for data-plumber-flask.

Run with
pytest -v -s --cov=data_plumber_flask.keys --cov=data_plumber_flask.types
"""

import pytest

from data_plumber_http.keys import Property, OneOf, AllOf
from data_plumber_http.types \
    import Boolean, String, Object
from data_plumber_http.settings import Responses


@pytest.mark.parametrize(
    ("json", "status"),
    [
        ({"str": "string"}, Responses.GOOD.status),
        ({"bool": True}, Responses.GOOD.status),
        ({"bool": 0.1}, Responses.MISSING_REQUIRED_ONEOF.status),
        ({"str": "string", "bool": True}, Responses.MULTIPLE_ONEOF.status),
    ]
)
def test_one_of_simple(json, status):
    """Basic test for key `OneOf`."""
    output = Object(
        properties={
            OneOf("str|bool", required=True): {
                Property("str"): String(),
                Property("bool"): Boolean()
            }
        }
    ).assemble().run(json=json)

    assert output.last_status == status
    if status == Responses.GOOD.status:
        assert output.data.value == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("exclusive", "status"),
    [
        (True, Responses.MULTIPLE_ONEOF.status),
        (False, Responses.GOOD.status),
    ],
    ids=["exclusive", "non-exclusive"]
)
def test_one_of_exclusive(exclusive, status):
    """Test argument `exclusive` for key `OneOf`."""
    json = {"str": "string", "bool": True}
    output = Object(
        properties={
            OneOf("str|bool", exclusive=exclusive): {
                Property("str"): String(),
                Property("bool"): Boolean()
            }
        }
    ).assemble().run(json=json)

    assert output.last_status == status
    if status == Responses.GOOD.status:
        assert len(output.data.value) == 1
        key = list(output.data.value.keys())[0]
        assert key in json
        assert output.data.value[key] == json[key]
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    "properties",
    [
        {Property("str", default="default"): String()},
        {OneOf("str", default="default"): {Property("str"): String()}},
    ],
    ids=["Property", "OneOf"]
)
@pytest.mark.parametrize(
    "json",
    [
        {"str": "string"},
        {"no-str": "string"},
    ],
    ids=["arg_present", "arg_missing"]
)
def test_key_default(properties, json):
    """Test argument `default` for keys `Property` and `OneOf`."""
    output = Object(
        properties=properties
    ).assemble().run(json=json)

    assert output.last_status == Responses.GOOD.status
    if "str" in json:
        assert output.data.value == json
    else:
        assert output.data.value["str"] == "default"


@pytest.mark.parametrize(
    "properties",
    [
        {
            Property(
                "str", default=lambda default_string, **kwargs: default_string
            ): String()
        },
        {
            OneOf(
                "str", default=lambda default_string, **kwargs: default_string
            ): {Property("str"): String()}
        },
    ],
    ids=["Property", "OneOf"]
)
@pytest.mark.parametrize(
    "json",
    [
        {"str": "string"},
        {"no-str": "string"},
    ],
    ids=["arg_present", "arg_missing"]
)
def test_key_default_callable(properties, json):
    """
    Test argument `default` with callable for keys `Property` and
    `OneOf`.
    """
    output = Object(
        properties=properties
    ).assemble().run(json=json, default_string="more-text")

    assert output.last_status == Responses.GOOD.status
    if "str" in json:
        assert output.data.value == json
    else:
        assert output.data.value["str"] == "more-text"


@pytest.mark.parametrize(
    "json",
    [
        {"str": "string"},
        {"no-str": "string"},
    ],
    ids=["arg_present", "arg_missing"]
)
def test_one_of_fill_with_none(json):
    """Test argument `fill_with_none` for key `OneOf`."""
    output = Object(
        properties={
            OneOf("str", fill_with_none=True): {
                Property("str"): String()
            }
        }
    ).assemble().run(json=json)

    assert output.last_status == Responses.GOOD.status
    if "str" in json:
        assert output.data.value == json
    else:
        assert output.data.value["str"] is None


@pytest.mark.parametrize(
    ("json", "status"),
    [
        ({"str": "string"}, Responses.GOOD.status),
        ({"bool": True}, Responses.GOOD.status),
        ({"bool": 0.1}, Responses.MISSING_REQUIRED_ONEOF.status),
        ({"str": "string", "bool": True}, Responses.MULTIPLE_ONEOF.status),
    ]
)
def test_one_of_validation_only(json, status):
    """Test argument `validation_only` for key `OneOf`."""
    output = Object(
        properties={
            OneOf("str|bool", required=True, validation_only=True): {
                Property("str"): String(),
                Property("bool"): Boolean()
            }
        }
    ).assemble().run(json=json)

    assert output.last_status == status
    if status == Responses.GOOD.status:
        assert output.data.value == {}
    else:
        print(output.last_message)
