"""
Tests dedicated to the `Object` argument `free_form`.
"""

from unittest import TestCase

from data_plumber_http.keys import Property
from data_plumber_http.types import Object, String
from data_plumber_http.settings import Responses


class TestObjectFreeForm(TestCase):
    """Tests for `free_form` in `Object`."""

    def test_conflict_additional_properties(self):
        """Conflict with `additional_properties`."""
        with self.assertRaises(ValueError):
            Object(additional_properties=String(), free_form=True)

    def test_conflict_accept_only(self):
        """Conflict with `accept_only`."""
        with self.assertRaises(ValueError):
            Object(accept_only=["string"], free_form=True)

    def test_full(self):
        """Full evaluation."""
        for json in [
            {},
            {"string": "string1"},
            {"string": "string1", "boolean": True},
            {"string": "string1", "object": {"string": "string2"}},
        ]:
            with self.subTest(json=json):
                output = (
                    Object(
                        properties={Property("object"): Object(free_form=True)}
                    )
                    .assemble()
                    .run(json={"object": json})
                )

                self.assertEqual(output.last_status, Responses().GOOD.status)
                self.assertDictEqual(output.data.value["object"], json)

    def test_partial(self):
        """Partial evaluation."""
        for json, status in [
            ({"string": "string1", "object": {}}, Responses().GOOD.status),
            ({"object": {}}, Responses().GOOD.status),
            (
                {"object": {"another-string": "string2"}},
                Responses().GOOD.status,
            ),
            (
                {
                    "object": {
                        "another-string": "string2",
                        "something-else": True,
                    }
                },
                Responses().GOOD.status,
            ),
            (
                {"object": {"another-string": False}},
                Responses().BAD_TYPE.status,
            ),
        ]:
            with self.subTest(json=json, status=status):
                output = (
                    Object(
                        properties={
                            Property("string"): String(),
                            Property("object"): Object(
                                properties={
                                    Property("another-string"): String()
                                },
                                free_form=True,
                            ),
                        }
                    )
                    .assemble()
                    .run(json=json)
                )

                self.assertEqual(output.last_status, status)
                if status == Responses().GOOD.status:
                    self.assertDictEqual(output.data.value, json)
                else:
                    print(output.last_message)

    def test_with_model(self):
        """Evaluation with model."""

        class SomeModel:
            """Test model."""

            def __init__(self, **kwargs):
                self.kwargs = kwargs

        json = {"string": "string1", "object": {"string": "string2"}}
        output = (
            Object(
                properties={
                    Property("object"): Object(model=SomeModel, free_form=True)
                }
            )
            .assemble()
            .run(json={"object": json})
        )

        self.assertEqual(output.last_status, Responses().GOOD.status)
        self.assertDictEqual(output.data.value["object"].kwargs, json)
