"""
Part of the test suite for data-plumber-flask.

Run with
pytest -v -s --cov=data_plumber_http.keys --cov=data_plumber_http.types
"""

import pytest

from data_plumber_http.keys import Property
from data_plumber_http.types \
    import Array, Boolean, Float, Integer, Number, Object, String
from data_plumber_http.types import Responses


@pytest.mark.parametrize(
    ("prop", "json", "status"),
    [
        (String(), "string1", Responses.GOOD.status),
        (String(), 0, Responses.BAD_TYPE.status),
        (Boolean(), True, Responses.GOOD.status),
        (Boolean(), 0, Responses.BAD_TYPE.status),
        (Integer(), 0, Responses.GOOD.status),
        (Integer(), 0.1, Responses.BAD_TYPE.status),
        (Float(), 0.1, Responses.GOOD.status),
        (Float(), True, Responses.BAD_TYPE.status),
        (Number(), 0, Responses.GOOD.status),
        (Number(), 0.1, Responses.GOOD.status),
        (Number(), True, Responses.GOOD.status),
        (Number(), "string1", Responses.BAD_TYPE.status),
        (Array(items=Integer()), [0, 1], Responses.GOOD.status),
        (Array(items=Number()), [0, 1.5], Responses.GOOD.status),
        (Array(items=String()), ["string1", "string2"], Responses.GOOD.status),
        (
            Array(items=Object(free_form=True)),
            [{"field1": 1, "field2": "string"}, {}],
            Responses.GOOD.status
        ),
        (Array(items=String()), 0, Responses.BAD_TYPE.status),
        (Array(items=String()), [0], Responses.BAD_TYPE.status),
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
    if status == Responses.GOOD.status:
        assert output.data.value["field"] == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        (
            {},
            Responses.BAD_TYPE.status
        ),
        (
            [
                {"field1": 0.1, "field2": [True, "string"]},
            ],
            Responses.BAD_TYPE.status
        ),
        (
            [
                {"field2": [0.1, True, "string"]},
            ],
            Responses.BAD_TYPE.status
        ),
        (
            [
                {"field1": False, "field2": [True, "string"]},
                {"field1": "False", "field2": ["True", "string"]},
            ],
            Responses.GOOD.status
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
    if status == Responses.GOOD.status:
        assert output.data.value["field"] == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        (
            [True, False, True],
            Responses.GOOD.status
        ),
        (
            ["string1", "string2"],
            Responses.GOOD.status
        ),
        (
            ["string1", True],
            Responses.BAD_TYPE.status
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
    if status == Responses.GOOD.status:
        assert output.data.value["field"] == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        ("string1", Responses.GOOD.status),
        ("string", Responses.BAD_VALUE.status),
        ("string11", Responses.BAD_VALUE.status),
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
    if status == Responses.GOOD.status:
        assert output.data.value["field"] == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        ("string1", Responses.GOOD.status),
        ("string2", Responses.GOOD.status),
        ("string", Responses.BAD_VALUE.status),
        ("string11", Responses.BAD_VALUE.status),
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
    if status == Responses.GOOD.status:
        assert output.data.value["field"] == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        (1, Responses.GOOD.status),
        (2, Responses.GOOD.status),
        (0, Responses.BAD_VALUE.status),
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
    if status == Responses.GOOD.status:
        assert output.data.value["field"] == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        (1, Responses.GOOD.status),
        (2, Responses.GOOD.status),
        (3, Responses.GOOD.status),
        (0, Responses.BAD_VALUE.status),
    ]
)
def test_integer_range(json, status):
    """Test property `range_` of `Integer`."""
    output = Object(
        properties={
            Property("field"): Integer(range_=[1, 3])
        }
    ).assemble().run(json={"field": json})

    assert output.last_status == status
    if status == Responses.GOOD.status:
        assert output.data.value["field"] == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        (1.0, Responses.GOOD.status),
        (3.5, Responses.GOOD.status),
        (0.9, Responses.BAD_VALUE.status),
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
    if status == Responses.GOOD.status:
        assert output.data.value["field"] == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        (1.0, Responses.GOOD.status),
        (2.0, Responses.GOOD.status),
        (3.0, Responses.GOOD.status),
        (0.0, Responses.BAD_VALUE.status),
    ]
)
def test_float_range(json, status):
    """Test property `range_` of `Float`."""
    output = Object(
        properties={
            Property("field"): Float(range_=[1, 3])
        }
    ).assemble().run(json={"field": json})

    assert output.last_status == status
    if status == Responses.GOOD.status:
        assert output.data.value["field"] == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        (1, Responses.GOOD.status),
        (2, Responses.GOOD.status),
        (3.5, Responses.GOOD.status),
        (0, Responses.BAD_VALUE.status),
        (0.9, Responses.BAD_VALUE.status),
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
    if status == Responses.GOOD.status:
        assert output.data.value["field"] == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        (1, Responses.GOOD.status),
        (1.0, Responses.GOOD.status),
        (2, Responses.GOOD.status),
        (2.0, Responses.GOOD.status),
        (3, Responses.GOOD.status),
        (3.0, Responses.GOOD.status),
        (0, Responses.BAD_VALUE.status),
        (0.0, Responses.BAD_VALUE.status),
    ]
)
def test_number_range(json, status):
    """Test property `range_` of `Number`."""
    output = Object(
        properties={
            Property("field"): Number(range_=[1, 3])
        }
    ).assemble().run(json={"field": json})

    assert output.last_status == status
    if status == Responses.GOOD.status:
        assert output.data.value["field"] == json
    else:
        print(output.last_message)
