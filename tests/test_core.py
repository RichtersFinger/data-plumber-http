"""Test core functionality."""

from unittest import TestCase
from data_plumber import Pipeline

from data_plumber_http.keys import Property
from data_plumber_http.types import Object, String
from data_plumber_http.settings import Responses


class TestProperty(TestCase):
    """Test class `Property`."""

    def test_empty_name(self):
        """Empty `name`."""
        # test name in constructor
        Property(origin="field1", name="field1")
        Property(origin="", name="field1")  # this is valid JSON
        with self.assertRaises(ValueError):
            Property(origin="field1", name="")
        with self.assertRaises(ValueError):
            Property(origin="", name="")
        with self.assertRaises(ValueError):
            Property(origin="")

        # test name-setter
        p = Property("field1")
        p.name = "field1_name"
        self.assertEqual(p.name, "field1_name")
        with self.assertRaises(ValueError):
            p.name = ""

    def test_validation_only(self):
        """Argument `validation_only`."""
        output = (
            Object(
                properties={
                    Property("string", validation_only=False): String()
                }
            )
            .assemble()
            .run(json={"string": "test-string"})
        )
        self.assertDictEqual(output.data.value, {"string": "test-string"})
        self.assertEqual(output.last_status, Responses().GOOD.status)

        output = (
            Object(
                properties={Property("string", validation_only=True): String()}
            )
            .assemble()
            .run(json={"string": "test-string"})
        )
        self.assertDictEqual(output.data.value, {})
        self.assertEqual(output.last_status, Responses().GOOD.status)

    def test_required(self):
        """Argument `required`."""
        pipeline = Object(
            properties={Property("some-string", required=True): String()}
        ).assemble()

        output = pipeline.run(json={"some-string": "test-string"})
        self.assertDictEqual(output.data.value, {"some-string": "test-string"})

        output = pipeline.run(json={"another-string": "test-string"})
        self.assertIsNone(output.data.value)
        self.assertEqual(
            output.last_status, Responses().MISSING_REQUIRED.status
        )
        self.assertIn("some-string", output.last_message)
        self.assertIn("missing", output.last_message)

    def test_default(self):
        """Argument `default`."""
        for default in ["default-text", None]:
            for json in [{"string": "test-string"}, {}]:
                with self.subTest(default=default, json=json):
                    output = (
                        Object(
                            properties={
                                Property("string", default=default): String()
                            }
                        )
                        .assemble()
                        .run(json=json)
                    )

                    self.assertEqual(
                        output.last_status, Responses().GOOD.status
                    )
                    self.assertEqual(
                        output.data.value.get("string"),
                        json.get("string") or default,
                    )

    def test_default_callable(self):
        """Callable argument `default`."""
        output = (
            Object(
                properties={
                    Property(
                        "string",
                        default=lambda default_string, **kwargs: default_string,
                    ): String()
                }
            )
            .assemble()
            .run(json={}, default_string="more-text")
        )

        self.assertEqual(output.last_status, Responses().GOOD.status)
        self.assertEqual(output.data.value.get("string"), "more-text")

    def test_required_default(self):
        """Arguments `required` and `default`."""
        for default in ["default-text", None]:
            with self.subTest(default=default):
                output = (
                    Object(
                        properties={
                            Property(
                                "string", default=default, required=True
                            ): String()
                        }
                    )
                    .assemble()
                    .run(json={})
                )

                if default is not None:
                    self.assertEqual(output.last_status, 0)
                    self.assertIn("string", output.data.value)
                    self.assertEqual(output.data.value["string"], default)
                else:
                    self.assertEqual(
                        output.last_status, Responses().MISSING_REQUIRED.status
                    )
                    self.assertIn("missing", output.last_message.lower())
                    self.assertIn("string", output.last_message)
                    self.assertEqual(output.data.value, None)

    def test_origin_name(self):
        """Arguments `origin` and `name`."""
        output = (
            Object(
                properties={
                    Property(origin="string", name="model_arg"): String()
                }
            )
            .assemble()
            .run(json={"string": "test-string"})
        )

        self.assertEqual(output.last_status, Responses().GOOD.status)
        self.assertDictEqual(output.data.value, {"model_arg": "test-string"})


class TestDPType(TestCase):
    """Test class `DPType` interaction."""

    def test_custom(self):
        """Defining custom."""

        class NoA(String):
            """Custom `String` extension."""

            def make(self, json, loc):
                if "a" in json.lower():
                    return (
                        None,
                        (
                            f"Character 'a' in field '{loc}' not allowed "
                            + f"(got '{json}')."
                        ),
                        422,
                    )
                return (
                    self.TYPE(json),
                    Responses().GOOD.msg,
                    Responses().GOOD.status,
                )

        p = Object(properties={Property("string"): NoA()}).assemble()

        output = p.run(json={"string": "test-string"})
        self.assertEqual(output.last_status, Responses().GOOD.status)
        self.assertDictEqual(output.data.value, {"string": "test-string"})

        output = p.run(json={"string": "test-string with 'a'"})
        print(output.last_message)
        self.assertIn("Character 'a' in field", output.last_message)
        self.assertEqual(output.last_status, 422)


class TestObjectPipeline(TestCase):
    """Test `Object.assemble`."""

    def test_type(self):
        """Is `Pipeline`."""
        self.assertIsInstance(
            Object(properties={Property("string"): String()}).assemble(),
            Pipeline,
        )


class TestObjectPipelineRun(TestCase):
    """Test `Object`-`Pipeline.run`."""

    def test_basic(self):
        """Basic execution."""
        pipeline = Object(properties={Property("string"): String()}).assemble()

        output = pipeline.run(json={"string": "test-string"})
        self.assertDictEqual(output.data.value, {"string": "test-string"})
        self.assertEqual(output.last_status, Responses().GOOD.status)

        output = pipeline.run(json={"another-string": "test-string"})
        self.assertDictEqual(output.data.value, {})
        self.assertEqual(output.last_status, Responses().GOOD.status)

    def test_bad_type(self):
        """Handling of bad type."""
        pipeline = Object(properties={Property("string"): String()}).assemble()

        output = pipeline.run(json={"string": 0})
        self.assertIsNone(output.data.value)
        self.assertEqual(output.last_status, Responses().BAD_TYPE.status)
        print(output.last_message)


class TestObjectProperties(TestCase):
    """Test argument `properties` for `Object`."""

    def test_key_value_conflict(self):
        """Duplicate property names."""
        # this is fine
        Object(
            properties={
                Property(origin="string", name="model_arg"): String(),
                Property(origin="string", name="model_arg2"): String(),
            }
        )

        with self.assertRaises(ValueError):
            Object(
                properties={
                    Property(origin="string", name="model_arg"): String(),
                    Property(origin="string", name="model_arg"): String(),
                }
            )

    def test_constructed_from_other_object(self):
        """Property `properties`."""
        obj1 = Object(properties={Property("string"): String()})
        obj2 = Object(properties={Property("another-string"): String()})

        json = {"string": "string2", "another-string": "string2"}
        output = (
            Object(properties=obj1.properties | obj2.properties)
            .assemble()
            .run(json=json)
        )
        self.assertEqual(output.last_status, Responses().GOOD.status)
        self.assertDictEqual(output.data.value, json)


class TestObjectModel(TestCase):
    """Test argument `model` for `Object`."""

    def test_basic(self):
        """Argument `model`."""
        # without explicit model (default to dict)
        output = (
            Object(
                properties={
                    Property(origin="string", name="model_arg"): String()
                }
            )
            .assemble()
            .run(json={"string": "test-string"})
        )

        self.assertEqual(output.last_status, Responses().GOOD.status)
        self.assertIsInstance(output.data.value, dict)
        self.assertDictEqual(output.data.value, {"model_arg": "test-string"})

        # with explicit model
        class SomeModel:
            """Test model."""

            def __init__(self, model_arg):
                self.string = model_arg

        output = (
            Object(
                model=SomeModel,
                properties={
                    Property(origin="string", name="model_arg"): String()
                },
            )
            .assemble()
            .run(json={"string": "test-string"})
        )

        self.assertEqual(output.last_status, Responses().GOOD.status)
        self.assertIsInstance(output.data.value, SomeModel)
        self.assertEqual(output.data.value.string, "test-string")
        self.assertDictEqual(output.data.kwargs, {"model_arg": "test-string"})

    def test_as_factory(self):
        """Factory in argument `model`."""

        class SomeModel:
            """Test model."""

            def __init__(self, model_arg1: str, model_arg2: int):
                self.string = model_arg1
                self.number = model_arg2

        output = (
            Object(
                model=lambda model_arg1: SomeModel(
                    model_arg1=model_arg1, model_arg2=5
                ),
                properties={
                    Property(origin="string", name="model_arg1"): String()
                },
            )
            .assemble()
            .run(json={"string": "test-string"})
        )

        self.assertEqual(output.last_status, Responses().GOOD.status)
        self.assertIsInstance(output.data.value, SomeModel)
        self.assertEqual(output.data.value.string, "test-string")
        self.assertEqual(output.data.value.number, 5)

    def test_missing_arg(self):
        """Model-object cannot be constructed."""

        # with explicit model
        class SomeModel:
            """Test model."""

            def __init__(self, model_arg):
                self.string = model_arg

        output = (
            Object(
                model=SomeModel,
                properties={Property("model_arg", required=True): String()},
            )
            .assemble()
            .run(json={})
        )

        self.assertEqual(
            output.last_status, Responses().MISSING_REQUIRED.status
        )


class TestObjectNested(TestCase):
    """Test nesting `Object`s."""

    def test_basic(self):
        """Basic nesting."""
        params = [
            (
                {
                    "some-object": {
                        "string": "test-string",
                        "another-object": {"string": "more-text"},
                    }
                },
                Responses().GOOD.status,
            ),
            (
                {
                    "some-object": {
                        "string": "test-string",
                        "another-object": {},
                    }
                },
                Responses().GOOD.status,
            ),
            (
                {"some-object": {"another-object": {"string": "more-text"}}},
                Responses().GOOD.status,
            ),
            (
                {
                    "some-object": {
                        "string": "test-string",
                    }
                },
                Responses().MISSING_REQUIRED.status,
            ),
            ({"some-object": {}}, Responses().MISSING_REQUIRED.status),
            ({}, Responses().GOOD.status),
        ]

        for json, status in params:
            with self.subTest(json=json, status=status):
                pipeline = Object(
                    properties={
                        Property("some-object"): Object(
                            properties={
                                Property("string"): String(),
                                Property(
                                    "another-object", required=True
                                ): Object(
                                    properties={Property("string"): String()}
                                ),
                            }
                        )
                    }
                ).assemble()

                output = pipeline.run(json=json)
                self.assertEqual(output.last_status, status)
                if output.last_status == Responses().GOOD.status:
                    self.assertDictEqual(output.data.value, json)
                else:
                    print(output.last_message)
                    self.assertIn(".some-object", output.last_message)
                    self.assertIn("another-object", output.last_message)

    def test_deeply(self):
        """Nested deeply."""
        for required in [True, False]:
            with self.subTest(required=required):
                pipeline = Object(
                    properties={
                        Property("some-object"): Object(
                            properties={
                                Property("string1"): String(),
                                Property("another-object"): Object(
                                    properties={
                                        Property("string2"): String(),
                                        Property("yet-more-objects"): Object(
                                            properties={
                                                Property(
                                                    "string3",
                                                    required=required,
                                                ): String()
                                            }
                                        ),
                                    }
                                ),
                            }
                        )
                    }
                ).assemble()

                json = {
                    "some-object": {
                        "string1": "a",
                        "another-object": {
                            "string2": "b",
                            "yet-more-objects": {},
                        },
                    }
                }
                output = pipeline.run(json=json)
                if required:
                    print(output.last_message)
                    self.assertEqual(
                        output.last_status, Responses().MISSING_REQUIRED.status
                    )
                    self.assertIn(
                        "some-object.another-object.yet-more-objects",
                        output.last_message,
                    )
                    self.assertIn("string3", output.last_message)
                else:
                    self.assertEqual(
                        output.last_status, Responses().GOOD.status
                    )
                    self.assertDictEqual(output.data.value, json)

    def test_with_default(self):
        """With default."""
        pipeline = Object(
            properties={
                Property("some-object"): Object(
                    properties={
                        Property(
                            "another-object", default=lambda **kwargs: None
                        ): Object(properties={Property("string2"): String()})
                    }
                )
            }
        ).assemble()

        json = {"some-object": {"string1": "a"}}
        output = pipeline.run(json=json)
        self.assertEqual(output.last_status, Responses().GOOD.status)
        self.assertDictEqual(
            output.data.value, {"some-object": {"another-object": None}}
        )


class TestObjectAcceptOnly(TestCase):
    """Test argument `accept_only` for `Object`."""

    def test_unknown(self):
        """Property `accept_only`."""
        for accept in [["string"], None]:
            for json in [{}, {"another-string": "test-string"}]:
                with self.subTest(accept=accept, json=json):
                    output = (
                        Object(
                            properties={Property("string"): String()},
                            accept_only=accept,
                        )
                        .assemble()
                        .run(json=json)
                    )
                    if accept is not None and "another-string" in json:
                        self.assertEqual(
                            output.last_status,
                            Responses().UNKNOWN_PROPERTY.status,
                        )
                        self.assertIn("another-string", output.last_message)
                    else:
                        self.assertEqual(
                            output.last_status, Responses().GOOD.status
                        )
