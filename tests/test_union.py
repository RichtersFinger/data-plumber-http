"""
Part of the test suite for data-plumber-http.

Run with
pytest -v -s
  --cov=data_plumber_http.keys
  --cov=data_plumber_http.types
  --cov=data_plumber_http.decorators
  --cov=data_plumber_http.settings
"""

import pytest

from data_plumber_http.keys import Property
from data_plumber_http.types \
    import Boolean, String, Object, _DPType
from data_plumber_http.settings import Responses


def test_union_type():
    """Test typing for union operator with `_DPType`."""
    assert isinstance(Boolean() | String(), _DPType)


def test_union_type_threefold():
    """Test typing for union operator with `_DPType`."""
    assert isinstance(Boolean() | String() | Object(), _DPType)


@pytest.mark.parametrize(
    ("json", "error"),
    [
        ("string", False),
        (True, False),
        ({}, True),
    ],
    ids=["string", "boolean", "object"]
)
def test_union_type_make(json, error):
    """Test method `make` of union-type."""
    if error:
        with pytest.raises(ValueError) as exc_info:
            (Boolean() | String()).make(json, ".")
        print(exc_info)
    else:
        assert (Boolean() | String()).make(json, ".") \
            == (json, Responses().GOOD.msg, Responses().GOOD.status)


@pytest.mark.parametrize(
    ("json", "error"),
    [
        ("string", False),
        (True, False),
        ({}, False),
        ([], True),
    ],
    ids=["string", "boolean", "object", "list"]
)
def test_union_type_make_threefold(json, error):
    """Test method `make` of union-type."""
    if error:
        with pytest.raises(ValueError) as exc_info:
            (Boolean() | String() | Object(free_form=True)).make(json, ".")
        print(exc_info)
    else:
        assert (Boolean() | String() | Object(free_form=True)).make(json, ".") \
            == (json, Responses().GOOD.msg, Responses().GOOD.status)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        ({"str-or-bool": "string"}, Responses().GOOD.status),
        ({"str-or-bool": True}, Responses().GOOD.status),
        ({"str-or-bool": {}}, Responses().BAD_TYPE.status),
    ],
    ids=["string", "boolean", "object"]
)
def test_union_in_object_validation(json, status):
    """Test defining union-property in `Object`-properties."""

    output = Object(
        properties={Property("str-or-bool"): String() | Boolean()}
    ).assemble().run(json=json)

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        ({"str-or-bool": "string"}, Responses().GOOD.status),
        ({"str-or-bool": True}, Responses().GOOD.status),
        ({"str-or-bool": {"field1": "value1"}}, Responses().GOOD.status),
    ],
    ids=["string", "boolean", "object"]
)
@pytest.mark.parametrize(
    ("type_"),
    [
        (String() | Boolean()) | Object(free_form=True),
        String() | (Boolean() | Object(free_form=True)),
        (String() | Object(free_form=True)) | Boolean(),
        Object(free_form=True) | (String() | Boolean()),
    ]
)
def test_union_in_object_validation_threefold_associative(json, status, type_):
    """Test defining union-property in `Object`-properties."""

    output = Object(
        properties={
            Property("str-or-bool"): type_
        }
    ).assemble().run(json=json)

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value == json
    else:
        print(output.last_message)
