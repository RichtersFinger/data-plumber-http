"""
Tests dedicated to the `Union` operator.
"""

from unittest import TestCase

from data_plumber_http.keys import Property
from data_plumber_http.types import Boolean, String, Object, DPType
from data_plumber_http.settings import Responses


class TestDPTypeUnion(TestCase):
    """Test typing for union operator with `DPType`."""

    def test_twofold(self):
        """Twofold."""
        self.assertIsInstance(Boolean() | String(), DPType)

    def test_threefold(self):
        """Threefold."""
        self.assertIsInstance(Boolean() | String() | Object(), DPType)


class TestDPTypeMake(TestCase):
    """Test method `make` of union-type."""

    def test_twofold(self):
        """Twofold."""
        for id_, json, error in [
            ("string", "string", False),
            ("boolean", True, False),
            ("object", {}, True),
        ]:
            with self.subTest(id=id_, json=json, error=error):
                if error:
                    with self.assertRaises(ValueError) as exc_info:
                        (Boolean() | String()).make(json, ".")
                    print(exc_info)
                else:
                    self.assertEqual(
                        (Boolean() | String()).make(json, "."),
                        (json, Responses().GOOD.msg, Responses().GOOD.status),
                    )

    def test_threefold(self):
        """Threefold."""
        for id_, json, error in [
            ("string", "string", False),
            ("boolean", True, False),
            ("object", {}, False),
            ("list", [], True),
        ]:
            with self.subTest(id=id_, json=json, error=error):
                if error:
                    with self.assertRaises(ValueError) as exc_info:
                        (Boolean() | String() | Object(free_form=True)).make(
                            json, "."
                        )
                    print(exc_info)
                else:
                    self.assertEqual(
                        (Boolean() | String() | Object(free_form=True)).make(
                            json, "."
                        ),
                        (json, Responses().GOOD.msg, Responses().GOOD.status),
                    )


class TestObjectValidation(TestCase):
    """Test defining union-property in `Object`-properties."""

    def test_twofold(self):
        """Twofold."""
        for id_, json, status in [
            ("string", {"str-or-bool": "string"}, Responses().GOOD.status),
            ("boolean", {"str-or-bool": True}, Responses().GOOD.status),
            ("object", {"str-or-bool": {}}, Responses().BAD_TYPE.status),
        ]:
            with self.subTest(id=id_, json=json, status=status):
                output = (
                    Object(
                        properties={
                            Property("str-or-bool"): String() | Boolean()
                        }
                    )
                    .assemble()
                    .run(json=json)
                )

                self.assertEqual(output.last_status, status)
                if status == Responses().GOOD.status:
                    self.assertEqual(output.data.value, json)
                else:
                    print(output.last_message)

    def test_threefold_associative(self):
        """Associativity."""
        for id_, json, status in [
            ("string", {"str-or-bool": "string"}, Responses().GOOD.status),
            ("boolean", {"str-or-bool": True}, Responses().GOOD.status),
            (
                "object",
                {"str-or-bool": {"field1": "value1"}},
                Responses().GOOD.status,
            ),
        ]:
            for type_ in [
                (String() | Boolean()) | Object(free_form=True),
                String() | (Boolean() | Object(free_form=True)),
                (String() | Object(free_form=True)) | Boolean(),
                Object(free_form=True) | (String() | Boolean()),
            ]:
                with self.subTest(
                    id=id_, json=json, status=status, type_=type_
                ):
                    output = (
                        Object(properties={Property("str-or-bool"): type_})
                        .assemble()
                        .run(json=json)
                    )

                    self.assertEqual(output.last_status, status)
                    if status == Responses().GOOD.status:
                        self.assertEqual(output.data.value, json)
                    else:
                        print(output.last_message)
