"""
Part of the test suite for data-plumber-flask.

Run with
pytest -v -s --cov=data_plumber_flask.keys --cov=data_plumber_flask.types
"""

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
