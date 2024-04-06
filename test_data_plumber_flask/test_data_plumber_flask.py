"""
Test suite for data-plumber.

Run with
pytest -v -s --cov=data_plumber_flask.keys --cov=data_plumber_flask.types
"""

# * missing tests: additional properties
# * __or__ for types
# * additional validation in model


import pytest
from data_plumber import Pipeline

from data_plumber_flask.keys import AllOf, OneOf, Property
from data_plumber_flask.types \
    import Array, Boolean, Float, Integer, Number, Object, String


def test_object_pipeline_type():
    """Test property `pipeline` of type `Object`."""

    assert isinstance(
        Object(properties={Property("string"): String()}).assemble(),
        Pipeline
    )


def test_object_pipeline_run_basic():
    """Test basic `Object`'s `Pipeline.run`."""

    pipeline = Object(properties={Property("string"): String()}).assemble()

    output = pipeline.run(json={"string": "test-string"})
    assert output.data == {"string": "test-string"}
    assert output.last_status == 0

    output = pipeline.run(json={"another-string": "test-string"})
    assert output.data == {}
    assert output.last_status == 0


def test_property_fill_with_none():
    """Test argument `fill_with_none` of `Property`."""

    output = Object(
        properties={Property("string", fill_with_none=False): String()}
    ).assemble().run(json={"another-string": "test-string"})
    assert output.data == {}
    assert output.last_status == 0

    output = Object(
        properties={Property("string", fill_with_none=True): String()}
    ).assemble().run(json={"another-string": "test-string"})
    assert output.data == {"string": None}
    assert output.last_status == 0


def test_property_required():
    """Test argument `required` of `Property`."""

    pipeline = Object(
        properties={Property("some-string", required=True): String()}
    ).assemble()

    output = pipeline.run(json={"some-string": "test-string"})
    assert output.data == {"some-string": "test-string"}

    output = pipeline.run(json={"another-string": "test-string"})
    assert output.data == {}
    assert output.last_status == 400
    assert "some-string" in output.last_message
    assert "missing" in output.last_message


@pytest.mark.parametrize(
    "default",
    [
        "default-text", None
    ],
    ids=["default", "no_default"]
)
@pytest.mark.parametrize(
    "json",
    [
        {"string": "test-string"}, {}
    ],
    ids=["arg_present", "arg_missing"]
)
def test_property_default(default, json):
    """Test argument `default` of `Property`."""

    output = Object(
        properties={
            Property("string", default=default):
            String()
        }
    ).assemble().run(json=json)

    assert output.last_status == 0
    assert output.data.get("string") == json.get("string") or default


def test_property_default_callable():
    """Test callable argument `default` of `Property`."""

    output = Object(
        properties={
            Property(
                "string",
                default=lambda default_string, **kwargs: default_string
            ): String()
        }
    ).assemble().run(json={}, default_string="more-text")

    assert output.last_status == 0
    assert output.data.get("string") == "more-text"


@pytest.mark.parametrize(
    "default",
    [
        "default-text", None
    ],
    ids=["default", "no_default"]
)
def test_property_required_default(default):
    """Test arguments `required` and `default` of `Property`."""

    output = Object(
        properties={
            Property("string", default=default, required=True):
            String()
        }
    ).assemble().run(json={})

    if default is not None:
        assert output.last_status == 0
        assert "string" in output.data
        assert output.data["string"] == default
    else:
        assert output.last_status == 400
        assert "missing" in output.last_message.lower()
        assert "string" in output.last_message
        assert output.data == {}


def test_property_origin_name():
    """Test arguments `origin` and `name` of `Property`."""

    output = Object(
        properties={
            Property(origin="string", name="model_arg"): String()
        }
    ).assemble().run(json={"string": "test-string"})

    assert output.last_status == 0
    assert output.data == {"model_arg": "test-string"}


def test_object_key_value_conflict_in_properties():
    """Test constructor of `Object` regarding duplicate property names."""

    # this is fine
    Object(
        properties={
            Property(origin="string", name="model_arg"): String(),
            Property(origin="string", name="model_arg2"): String()
        }
    )

    with pytest.raises(ValueError):
        Object(
            properties={
                Property(origin="string", name="model_arg"): String(),
                Property(origin="string", name="model_arg"): String()
            }
        )


def test_object_model():
    """Test argument `model` of `Object`."""
    class SomeModel:
        def __init__(self, model_arg):
            self.string = model_arg

    output = Object(
        model=SomeModel,
        properties={
            Property(origin="string", name="model_arg"): String()
        }
    ).assemble().run(json={"string": "test-string"})

    assert output.last_status == 0
    assert isinstance(output.data, SomeModel)
    assert output.data.string == "test-string"

    output = Object(
        model=SomeModel,
        properties={
            Property(origin="string", name="model_arg"): String()
        }
    ).assemble().run(json={"string": "test-string"})

    assert output.last_status == 0
    assert isinstance(output.data, dict)
    assert output.data == {"string": "test-string"}


@pytest.mark.parametrize(
    ("json", "status"),
    [
        (
            {
                "some-object": {
                    "string": "test-string",
                    "another-object": {"string": "more-text"}
                }
            }, 0
        ),
        (
            {
                "some-object": {
                    "string": "test-string",
                    "another-object": {}
                }
            }, 0
        ),
        (
            {
                "some-object": {
                    "another-object": {"string": "more-text"}
                }
            }, 0
        ),
        (
            {
                "some-object": {
                    "string": "test-string",
                }
            }, 400
        ),
        (
            {
                "some-object": {}
            }, 400
        ),
        (
            {}, 0
        ),
    ]
)
def test_object_nested(json, status):
    """Test nested `Object`s."""

    pipeline = Object(
        properties={
            Property("some-object"): Object(
                properties={
                    Property("string"): String(),
                    Property("another-object", required=True): Object(
                        properties={
                            Property("string"): String()
                        }
                    )
                }
            )
        }
    ).assemble()

    output = pipeline.run(json=json)
    assert output.last_record == status
    assert output.data == json


@pytest.mark.parametrize(
    "accept",
    [
        ["string"], None
    ],
    ids=["reject_unknown", "accept_unknown"]
)
@pytest.mark.parametrize(
    "json",
    [
        {}, {"another-string": "test-string"}
    ],
    ids=["json_no_unknown", "json_has_unknown"]
)
def test_object_unknown(accept, json):
    """Test property `accept_only` in `Object`."""

    output = Object(
        properties={Property("string"): String()},
        accept_only=accept
    ).assemble().run(json=json)
    if accept is not None and "another-string" in json:
        assert output.last_status == 400
        assert "another-string" in output.last_message
    else:
        assert output.last_status == 0
