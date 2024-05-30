"""
Part of the test suite for data-plumber-http.

Run with
pytest -v -s
  --cov=data_plumber_http.keys
  --cov=data_plumber_http.types
  --cov=data_plumber_http.decorators
  --cov=data_plumber_http.settings
"""

from pathlib import Path

import pytest

from data_plumber_http.keys import Property
from data_plumber_http.types \
    import Any, Array, Boolean, Float, Integer, Null, Number, \
        Object, String, Uri, Url, FileSystemObject
from data_plumber_http.settings import Responses


@pytest.mark.parametrize(
    ("prop", "json", "status"),
    [
        (String(), "string1", Responses().GOOD.status),
        (String(), 0, Responses().BAD_TYPE.status),
        (Boolean(), True, Responses().GOOD.status),
        (Boolean(), 0, Responses().BAD_TYPE.status),
        (Integer(), 0, Responses().GOOD.status),
        (Integer(), 0.1, Responses().BAD_TYPE.status),
        (Float(), 0.1, Responses().GOOD.status),
        (Float(), True, Responses().BAD_TYPE.status),
        (Null(), None, Responses().GOOD.status),
        (Null(), True, Responses().BAD_TYPE.status),
        (Number(), 0, Responses().GOOD.status),
        (Number(), 0.1, Responses().GOOD.status),
        (Number(), True, Responses().GOOD.status),
        (Number(), "string1", Responses().BAD_TYPE.status),
        (Array(), [0, "string1", {}], Responses().GOOD.status),
        (Array(items=Integer()), [0, 1], Responses().GOOD.status),
        (Array(items=Number()), [0, 1.5], Responses().GOOD.status),
        (Array(items=String()), ["string1", "string2"], Responses().GOOD.status),
        (
            Array(items=Object(free_form=True)),
            [{"field1": 1, "field2": "string"}, {}],
            Responses().GOOD.status
        ),
        (Array(items=String()), 0, Responses().BAD_TYPE.status),
        (Array(items=String()), [0], Responses().BAD_TYPE.status),
    ]
)
def test_types(prop, json, status):
    """Test `_DPTypes` in `Object`."""
    output = Object(
        properties={
            Property("field"): prop,
        }
    ).assemble().run(json={"field": json})

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value["field"] == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        (
            {},
            Responses().BAD_TYPE.status
        ),
        (
            [
                {"field1": 0.1, "field2": [True, "string"]},
            ],
            Responses().BAD_TYPE.status
        ),
        (
            [
                {"field2": [0.1, True, "string"]},
            ],
            Responses().BAD_TYPE.status
        ),
        (
            [
                {"field1": False, "field2": [True, "string"]},
                {"field1": "False", "field2": ["True", "string"]},
            ],
            Responses().GOOD.status
        ),
    ]
)
def test_types_complex(json, status):
    """Test more complex relation of `_DPTypes` in `Object`."""
    output = Object(
        properties={
            Property("field"): Array(
                items=Object(
                    properties={
                        Property("field1"): Boolean() | String(),
                        Property("field2"): Array(items=Boolean() | String()),
                    }
                )
            )
        }
    ).assemble().run(json={"field": json})

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value["field"] == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        (
            [True, False, True],
            Responses().GOOD.status
        ),
        (
            ["string1", "string2"],
            Responses().GOOD.status
        ),
        (
            ["string1", True],
            Responses().BAD_TYPE.status
        ),
    ]
)
def test_types_complex_union(json, status):
    """Test more complex relation of `_DPTypes` in `Object`."""
    output = Object(
        properties={
            Property("field"):
                Array(items=Boolean()) | Array(items=String())
        }
    ).assemble().run(json={"field": json})

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value["field"] == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        ("string1", Responses().GOOD.status),
        ("string", Responses().BAD_VALUE.status),
        ("string11", Responses().BAD_VALUE.status),
    ]
)
def test_string_pattern(json, status):
    """Test property `pattern` of `String`."""
    output = Object(
        properties={
            Property("field"): String(pattern=r"string[0-9]")
        }
    ).assemble().run(json={"field": json})

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value["field"] == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        ("string1", Responses().GOOD.status),
        ("string2", Responses().GOOD.status),
        ("string", Responses().BAD_VALUE.status),
        ("string11", Responses().BAD_VALUE.status),
    ]
)
def test_string_enum(json, status):
    """Test property `enum` of `String`."""
    output = Object(
        properties={
            Property("field"): String(enum=["string1", "string2"])
        }
    ).assemble().run(json={"field": json})

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value["field"] == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        (1, Responses().GOOD.status),
        (2, Responses().GOOD.status),
        (0, Responses().BAD_VALUE.status),
    ]
)
def test_integer_values(json, status):
    """Test property `values` of `Integer`."""
    output = Object(
        properties={
            Property("field"): Integer(values=[1, 2])
        }
    ).assemble().run(json={"field": json})

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value["field"] == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("options", "json", "status"),
    [
        ({"min_value": 1}, 2, Responses().GOOD.status),
        ({"min_value": 1}, 1, Responses().BAD_VALUE.status),
        ({"min_value": 1}, 0, Responses().BAD_VALUE.status),
        ({"min_value_inclusive": 1}, 2, Responses().GOOD.status),
        ({"min_value_inclusive": 1}, 1, Responses().GOOD.status),
        ({"min_value_inclusive": 1}, 0, Responses().BAD_VALUE.status),
        ({"max_value": 1}, 0, Responses().GOOD.status),
        ({"max_value": 1}, 1, Responses().BAD_VALUE.status),
        ({"max_value": 1}, 2, Responses().BAD_VALUE.status),
        ({"max_value_inclusive": 1}, 0, Responses().GOOD.status),
        ({"max_value_inclusive": 1}, 1, Responses().GOOD.status),
        ({"max_value_inclusive": 1}, 2, Responses().BAD_VALUE.status),
    ]
)
def test_integer_min_max_value(options, json, status):
    """Test properties for value ranges of `Integer`."""
    output = Object(
        properties={
            Property("field"): Integer(**options)
        }
    ).assemble().run(json={"field": json})

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value["field"] == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        (1.0, Responses().GOOD.status),
        (3.5, Responses().GOOD.status),
        (0.9, Responses().BAD_VALUE.status),
    ]
)
def test_float_values(json, status):
    """Test property `values` of `Float`."""
    output = Object(
        properties={
            Property("field"): Float(values=[1.0, 3.5])
        }
    ).assemble().run(json={"field": json})

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value["field"] == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("options", "json", "status"),
    [
        ({"min_value": 1}, 2.0, Responses().GOOD.status),
        ({"min_value": 1}, 1.0, Responses().BAD_VALUE.status),
        ({"min_value": 1}, 0.0, Responses().BAD_VALUE.status),
        ({"min_value_inclusive": 1}, 2.0, Responses().GOOD.status),
        ({"min_value_inclusive": 1}, 1.0, Responses().GOOD.status),
        ({"min_value_inclusive": 1}, 0.0, Responses().BAD_VALUE.status),
        ({"max_value": 1}, 0.0, Responses().GOOD.status),
        ({"max_value": 1}, 1.0, Responses().BAD_VALUE.status),
        ({"max_value": 1}, 2.0, Responses().BAD_VALUE.status),
        ({"max_value_inclusive": 1}, 0.0, Responses().GOOD.status),
        ({"max_value_inclusive": 1}, 1.0, Responses().GOOD.status),
        ({"max_value_inclusive": 1}, 2.0, Responses().BAD_VALUE.status),
    ]
)
def test_float_min_max_value(options, json, status):
    """Test properties for value ranges of `Float`."""
    output = Object(
        properties={
            Property("field"): Float(**options)
        }
    ).assemble().run(json={"field": json})

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value["field"] == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        (1, Responses().GOOD.status),
        (2, Responses().GOOD.status),
        (3.5, Responses().GOOD.status),
        (0, Responses().BAD_VALUE.status),
        (0.9, Responses().BAD_VALUE.status),
    ]
)
def test_number_values(json, status):
    """Test property `values` of `Number`."""
    output = Object(
        properties={
            Property("field"): Number(values=[1, 2, 3.5])
        }
    ).assemble().run(json={"field": json})

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value["field"] == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("options", "json", "status"),
    [
        ({"min_value": 1}, 2.0, Responses().GOOD.status),
        ({"min_value": 1}, 1.0, Responses().BAD_VALUE.status),
        ({"min_value": 1}, 0.0, Responses().BAD_VALUE.status),
        ({"min_value": 1}, 2, Responses().GOOD.status),
        ({"min_value": 1}, 1, Responses().BAD_VALUE.status),
        ({"min_value": 1}, 0, Responses().BAD_VALUE.status),
        ({"min_value_inclusive": 1}, 2.0, Responses().GOOD.status),
        ({"min_value_inclusive": 1}, 1.0, Responses().GOOD.status),
        ({"min_value_inclusive": 1}, 0.0, Responses().BAD_VALUE.status),
        ({"min_value_inclusive": 1}, 2, Responses().GOOD.status),
        ({"min_value_inclusive": 1}, 1, Responses().GOOD.status),
        ({"min_value_inclusive": 1}, 0, Responses().BAD_VALUE.status),
        ({"max_value": 1}, 0.0, Responses().GOOD.status),
        ({"max_value": 1}, 1.0, Responses().BAD_VALUE.status),
        ({"max_value": 1}, 2.0, Responses().BAD_VALUE.status),
        ({"max_value": 1}, 0, Responses().GOOD.status),
        ({"max_value": 1}, 1, Responses().BAD_VALUE.status),
        ({"max_value": 1}, 2, Responses().BAD_VALUE.status),
        ({"max_value_inclusive": 1}, 0.0, Responses().GOOD.status),
        ({"max_value_inclusive": 1}, 1.0, Responses().GOOD.status),
        ({"max_value_inclusive": 1}, 2.0, Responses().BAD_VALUE.status),
        ({"max_value_inclusive": 1}, 0, Responses().GOOD.status),
        ({"max_value_inclusive": 1}, 1, Responses().GOOD.status),
        ({"max_value_inclusive": 1}, 2, Responses().BAD_VALUE.status),
    ]
)
def test_number_min_max_value(options, json, status):
    """Test properties for value ranges of `Number`."""
    output = Object(
        properties={
            Property("field"): Number(**options)
        }
    ).assemble().run(json={"field": json})

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value["field"] == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        ("http://pypi.org/path", Responses().GOOD.status),
        ("http://pypi.org", Responses().GOOD.status),
        ("pypi.org", Responses().GOOD.status),  # interpreted as path
        ("http", Responses().GOOD.status),
        ("http://", Responses().GOOD.status),
        ("http:/path", Responses().GOOD.status),
    ]
)
def test_url_basic(json, status):
    """Test type `Url`."""
    output = Object(
        properties={
            Property("field"): Url()
        }
    ).assemble().run(json={"field": json})

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value["field"] == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        ("http://pypi.org", Responses().GOOD.status),
        ("custom://pypi.org", Responses().GOOD.status),
        ("sftp://pypi.org", Responses().BAD_VALUE.status),
        ("pypi.org", Responses().BAD_VALUE.status),
    ]
)
def test_url_schemes(json, status):
    """Test type `Url`."""
    output = Object(
        properties={
            Property("field"): Url(schemes=["http", "custom"])
        }
    ).assemble().run(json={"field": json})

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value["field"] == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        ("http://pypi.org/path", Responses().GOOD.status),
        ("http://pypi.org", Responses().GOOD.status),
        ("pypi.org", Responses().BAD_VALUE.status),
        ("://pypi.org", Responses().BAD_VALUE.status),
        ("http://", Responses().BAD_VALUE.status),
        ("http:/path", Responses().BAD_VALUE.status),
        ("", Responses().BAD_VALUE.status),
    ]
)
def test_url_require_netloc(json, status):
    """Test type `Url`."""
    output = Object(
        properties={
            Property("field"): Url(require_netloc=True)
        }
    ).assemble().run(json={"field": json})

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value["field"] == json
    else:
        print(output.last_message)


def test_url_return_parsed():
    """Test type `Url`."""
    output = Object(
        properties={
            Property("field"): Url(return_parsed=True)
        }
    ).assemble().run(json={"field": "http://pypi.org/path"})

    assert output.last_status == Responses().GOOD.status
    assert hasattr(output.data.value["field"], "scheme")
    assert hasattr(output.data.value["field"], "netloc")
    assert hasattr(output.data.value["field"], "path")


@pytest.mark.parametrize(
    ("json", "status"),
    [
        ("http://pypi.org/path", Responses().GOOD.status),
        ("http://pypi.org", Responses().GOOD.status),
        ("pypi.org", Responses().GOOD.status),  # interpreted as path
        ("http", Responses().GOOD.status),
        ("http://", Responses().GOOD.status),
        ("http:/path", Responses().GOOD.status),
    ]
)
def test_uri_basic(json, status):
    """Test type `Uri`."""
    output = Object(
        properties={
            Property("field"): Uri()
        }
    ).assemble().run(json={"field": json})

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value["field"] == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        ("http://pypi.org", Responses().GOOD.status),
        ("custom://pypi.org", Responses().GOOD.status),
        ("sftp://pypi.org", Responses().BAD_VALUE.status),
        ("pypi.org", Responses().BAD_VALUE.status),
    ]
)
def test_uri_schemes(json, status):
    """Test type `Uri`."""
    output = Object(
        properties={
            Property("field"): Uri(schemes=["http", "custom"])
        }
    ).assemble().run(json={"field": json})

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value["field"] == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        ("http://pypi.org/path", Responses().GOOD.status),
        ("http://pypi.org", Responses().GOOD.status),
        ("pypi.org", Responses().BAD_VALUE.status),
        ("://pypi.org", Responses().BAD_VALUE.status),
        ("http://", Responses().BAD_VALUE.status),
        ("http:/path", Responses().BAD_VALUE.status),
        ("", Responses().BAD_VALUE.status),
    ]
)
def test_uri_require_netloc(json, status):
    """Test type `Uri`."""
    output = Object(
        properties={
            Property("field"): Uri(require_authority=True)
        }
    ).assemble().run(json={"field": json})

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value["field"] == json
    else:
        print(output.last_message)


def test_uri_return_parsed():
    """Test type `Uri`."""
    output = Object(
        properties={
            Property("field"): Uri(return_parsed=True)
        }
    ).assemble().run(json={"field": "http://pypi.org/path"})

    assert output.last_status == Responses().GOOD.status
    assert hasattr(output.data.value["field"], "scheme")
    assert hasattr(output.data.value["field"], "netloc")
    assert hasattr(output.data.value["field"], "path")


@pytest.mark.parametrize(
    ("kwargs", "json", "status"),
    [
        ({}, __file__, Responses().GOOD.status),
        ({"exists": True}, __file__, Responses().GOOD.status),
        ({"is_file": True}, __file__, Responses().GOOD.status),
        ({"is_dir": False}, __file__, Responses().GOOD.status),
        ({"is_file": False}, __file__, Responses().CONFLICT.status),
        (
            {"is_file": True},
            str(Path(__file__).parent),
            Responses().BAD_RESOURCE.status
        ),
        ({"is_dir": True}, __file__, Responses().BAD_RESOURCE.status),
        ({"is_fifo": True}, __file__, Responses().BAD_RESOURCE.status),
        (
            {"is_file": True},
            __file__ + ".x",
            Responses().RESOURCE_NOT_FOUND.status
        ),
        (
            {"relative_to": Path("tests")},
            str(Path(__file__).relative_to(Path(__file__).parents[1])),
            Responses().GOOD.status
        ),
        (
            {"relative_to": Path(__file__).parent},
            str(Path(__file__).parents[1] / "another_path"),
            Responses().BAD_VALUE.status
        ),
        ({"relative_to": Path(".")}, __file__, Responses().BAD_VALUE.status),
        (
            {"cwd": Path("tests"), "is_file": True},
            Path(__file__).name,
            Responses().GOOD.status
        ),
    ],
    ids=[
        "basic", "exists-good", "is_file-good", "is_dir-good",
        "is_file-conflict", "is_dir-but file", "is_fifo-but file",
        "is_file-but dir", "is_file-not found", "relative_to-relative-good",
        "relative_to-absolute-bad", "relative_to-mixed-bad", "cwd",
    ]
)
def test_file_system_object(kwargs, json, status):
    """Test type `FileSystemObject`."""
    output = Object(
        properties={
            Property("field"): FileSystemObject(**kwargs)
        }
    ).assemble().run(json={"field": json})

    assert output.last_status == status
    if status == Responses().GOOD.status:
        if "relative_to" in kwargs:
            assert Path(json).relative_to(kwargs["relative_to"]) \
                == output.data.value["field"]
        elif "cwd" in kwargs:
            assert output.data.value["field"] == kwargs["cwd"] / json
        else:
            assert str(output.data.value["field"]) == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        ([1, "string1"], Responses().GOOD.status),
        (True, Responses().GOOD.status),
        (0.1, Responses().GOOD.status),
        (1, Responses().GOOD.status),
        (None, Responses().GOOD.status),
        ({"inner-field": "value"}, Responses().GOOD.status),
        ("string1", Responses().GOOD.status),
    ]
)
def test_any(json, status):
    """Test type `Any`."""
    output = Object(
        properties={
            Property("field"): Any()
        }
    ).assemble().run(json={"field": json})

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value["field"] == json
