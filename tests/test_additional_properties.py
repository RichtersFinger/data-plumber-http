"""
Tests dedicated to the `Object` argument `additional_properties`.
"""

from unittest import TestCase

from data_plumber_http.keys import Property
from data_plumber_http.types import Boolean, Object, String
from data_plumber_http.settings import Responses


class TestObjectAdditionalProperties(TestCase):
    """Test interactions with `additional_properties` for `Object`."""

    def test_accept_only(self):
        """Conflict with `accept_only`."""

        with self.assertRaises(ValueError):
            Object(additional_properties=String(), accept_only=["string"])

    def test_standard(self):
        """Standard behavior."""

        json = {"string": "string1", "another-string": "string2"}
        output = (
            Object(
                additional_properties=String(),
            )
            .assemble()
            .run(json=json)
        )
        self.assertEqual(output.last_status, Responses().GOOD.status)
        self.assertDictEqual(output.data.value, json)

    def test_properties(self):
        """With `properties`."""

        json = {"string": "string1", "object": {"string": "string2"}}
        output = (
            Object(
                properties={
                    Property("object"): Object(
                        properties={Property("string"): String()}
                    )
                },
                additional_properties=String(),
            )
            .assemble()
            .run(json=json)
        )
        self.assertEqual(output.last_status, Responses().GOOD.status)
        self.assertDictEqual(output.data.value, json)

    def test_none_given(self):
        """None given."""

        json = {}
        output = (
            Object(
                additional_properties=String(),
            )
            .assemble()
            .run(json=json)
        )
        self.assertEqual(output.last_status, Responses().GOOD.status)
        self.assertDictEqual(output.data.value, json)

    def test_property_none_given(self):
        """With `properties` and none given."""

        json = {"string": "string1"}
        output = (
            Object(
                properties={Property("string"): String()},
                additional_properties=String(),
            )
            .assemble()
            .run(json=json)
        )
        self.assertEqual(output.last_status, Responses().GOOD.status)
        self.assertDictEqual(output.data.value, json)

    def test_bad_types(self):
        """Bad types."""

        json = {"string": "string1"}
        output = (
            Object(
                additional_properties=Boolean(),
            )
            .assemble()
            .run(json=json)
        )
        print(output.last_message)
        self.assertEqual(output.last_status, Responses().BAD_TYPE.status)

    def test_boolean_minimal(self):
        """Boolean value (minimal)."""

        cases = [
            ("default", Object().assemble(), Responses().GOOD.status),
            (
                "True",
                Object(additional_properties=True).assemble(),
                Responses().GOOD.status,
            ),
            (
                "False",
                Object(additional_properties=False).assemble(),
                Responses().UNKNOWN_PROPERTY.status,
            ),
        ]

        for case_id, pipeline, status in cases:
            with self.subTest(id=case_id):
                output = pipeline.run(json={"string": "string1"})
                if output.last_status != Responses().GOOD.status:
                    print(output.last_message)
                self.assertEqual(output.last_status, status)

    def test_boolean_non_empty(self):
        """Boolean value (non-trivial)."""

        jsons = {
            "string_in_json": {"string": "string1"},
            "another_string_in_json": {"another-string": "string1"},
        }
        additional_properties_cases = [True, False]

        for json_id, json_val in jsons.items():
            for additional_properties in additional_properties_cases:
                with self.subTest(
                    json=json_id, additional_properties=additional_properties
                ):
                    output = (
                        Object(
                            properties={Property("string"): String()},
                            additional_properties=additional_properties,
                        )
                        .assemble()
                        .run(json=json_val)
                    )

                    if output.last_status != Responses().GOOD.status:
                        print(output.last_message)
                    if "string" in json_val or additional_properties:
                        self.assertEqual(
                            output.last_status, Responses().GOOD.status
                        )
                    else:
                        self.assertEqual(
                            output.last_status,
                            Responses().UNKNOWN_PROPERTY.status,
                        )
