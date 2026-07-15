"""
Test classes in `keys` and their interaction.
"""

from unittest import TestCase

from data_plumber_http.keys import Property, OneOf, AllOf
from data_plumber_http.types import Boolean, String, Object
from data_plumber_http.settings import Responses


def setUpModule():  # pylint: disable=invalid-name
    """
    Make default response status codes unique to increase test
    sensitivity.
    """
    Responses().warn_on_change = False
    # pylint: disable=no-member
    for index, x in enumerate(Responses().INTERNAL_RESPONSES):
        if getattr(Responses(), x).status >= 400:
            Responses().update(x, status=400 + index)
    Responses().warn_on_change = True


class TestOneOf(TestCase):
    """Tests for key `OneOf`."""

    def test_simple(self):
        """Basic test."""
        cases = [
            ({"str": "string"}, Responses().GOOD.status),
            ({"bool": True}, Responses().GOOD.status),
            ({"bool": 0.1}, Responses().BAD_TYPE.status),
            (
                {"str": "string", "bool": True},
                Responses().MULTIPLE_ONEOF.status,
            ),
        ]
        for json, status in cases:
            with self.subTest(json=json, status=status):
                output = (
                    Object(
                        properties={
                            OneOf("str|bool", required=True): {
                                Property("str"): String(),
                                Property("bool"): Boolean(),
                            }
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

    def test_exclusive(self):
        """Test argument `exclusive`."""
        cases = [
            (True, Responses().MULTIPLE_ONEOF.status),
            (False, Responses().GOOD.status),
        ]
        for exclusive, status in cases:
            with self.subTest(exclusive=exclusive, status=status):
                json = {"str": "string", "bool": True}
                output = (
                    Object(
                        properties={
                            OneOf("str|bool", exclusive=exclusive): {
                                Property("str"): String(),
                                Property("bool"): Boolean(),
                            }
                        }
                    )
                    .assemble()
                    .run(json=json)
                )

                self.assertEqual(output.last_status, status)
                if status == Responses().GOOD.status:
                    self.assertEqual(len(output.data.value), 1)
                    key = list(output.data.value.keys())[0]
                    self.assertIn(key, json)
                    self.assertEqual(output.data.value[key], json[key])
                else:
                    print(output.last_message)

    def test_validation_only(self):
        """Test argument `validation_only`."""
        cases = [
            ({"str": "string"}, Responses().GOOD.status),
            ({"bool": True}, Responses().GOOD.status),
            ({"bool": 0.1}, Responses().BAD_TYPE.status),
            (
                {"str": "string", "bool": True},
                Responses().MULTIPLE_ONEOF.status,
            ),
        ]
        for json, status in cases:
            with self.subTest(json=json, status=status):
                output = (
                    Object(
                        properties={
                            OneOf(
                                "str|bool", required=True, validation_only=True
                            ): {
                                Property("str"): String(),
                                Property("bool"): Boolean(),
                            }
                        }
                    )
                    .assemble()
                    .run(json=json)
                )

                self.assertEqual(output.last_status, status)
                if status == Responses().GOOD.status:
                    self.assertDictEqual(output.data.value, {})
                else:
                    print(output.last_message)


class TestKeyArguments(TestCase):
    """Tests for arguments common to `Property`, `OneOf`, and `AllOf`."""

    def test_required(self):
        """Test argument `required`."""
        properties_cases = [
            ({Property("str", required=True): String()}, True),
            ({OneOf("str", required=True): {Property("str"): String()}}, True),
            ({AllOf("str", required=True): {Property("str"): String()}}, True),
            ({Property("str", required=False): String()}, False),
            (
                {OneOf("str", required=False): {Property("str"): String()}},
                False,
            ),
            (
                {AllOf("str", required=False): {Property("str"): String()}},
                False,
            ),
        ]
        json_cases = [
            {"str": "string"},
            {"no-str": "string"},
        ]
        for properties, required in properties_cases:
            for json in json_cases:
                with self.subTest(
                    properties=properties, required=required, json=json
                ):
                    output = (
                        Object(properties=properties).assemble().run(json=json)
                    )

                    if not required or "str" in json:
                        self.assertEqual(
                            output.last_status, Responses().GOOD.status
                        )
                    else:
                        self.assertNotEqual(
                            output.last_status, Responses().GOOD.status
                        )
                    if "str" in json:
                        self.assertDictEqual(output.data.value, json)

    def test_default(self):
        """Test argument `default`."""
        properties_cases = [
            {Property("str", default="default"): String()},
            {OneOf("str", default="default"): {Property("str"): String()}},
            {AllOf("str", default="default"): {Property("str"): String()}},
        ]
        json_cases = [
            {"str": "string"},
            {"no-str": "string"},
        ]
        for properties in properties_cases:
            for json in json_cases:
                with self.subTest(properties=properties, json=json):
                    output = (
                        Object(properties=properties).assemble().run(json=json)
                    )

                    self.assertEqual(
                        output.last_status, Responses().GOOD.status
                    )
                    if "str" in json:
                        self.assertDictEqual(output.data.value, json)
                    else:
                        self.assertEqual(output.data.value["str"], "default")

    def test_default_callable(self):
        """Test argument `default` with callable."""
        properties_cases = [
            {
                Property(
                    "str",
                    default=lambda default_string, **kwargs: default_string,
                ): String()
            },
            {
                OneOf(
                    "str",
                    default=lambda default_string, **kwargs: default_string,
                ): {Property("str"): String()}
            },
            {
                AllOf(
                    "str",
                    default=lambda default_string, **kwargs: default_string,
                ): {Property("str"): String()}
            },
        ]
        json_cases = [
            {"str": "string"},
            {"no-str": "string"},
        ]
        for properties in properties_cases:
            for json in json_cases:
                with self.subTest(properties=properties, json=json):
                    output = (
                        Object(properties=properties)
                        .assemble()
                        .run(json=json, default_string="more-text")
                    )

                    self.assertEqual(
                        output.last_status, Responses().GOOD.status
                    )
                    if "str" in json:
                        self.assertDictEqual(output.data.value, json)
                    else:
                        self.assertEqual(output.data.value["str"], "more-text")


class TestAllOf(TestCase):
    """Tests for key `AllOf`."""

    def test_simple(self):
        """Basic test."""
        cases = [
            ({"str": "string"}, Responses().MISSING_REQUIRED_ALLOF.status),
            ({"bool": True}, Responses().MISSING_REQUIRED_ALLOF.status),
            ({"str": "string", "bool": 0.1}, Responses().BAD_TYPE.status),
            ({"str": "string", "bool": True}, Responses().GOOD.status),
        ]
        for json, status in cases:
            with self.subTest(json=json, status=status):
                output = (
                    Object(
                        properties={
                            AllOf("str&bool", required=True): {
                                Property("str"): String(),
                                Property("bool"): Boolean(),
                            }
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

    def test_validation_only(self):
        """Test argument `validation_only`."""
        cases = [
            ({"str": "string"}, Responses().MISSING_REQUIRED_ALLOF.status),
            ({"bool": True}, Responses().MISSING_REQUIRED_ALLOF.status),
            ({"str": "string", "bool": True}, Responses().GOOD.status),
            ({"str": "string", "bool": 0.1}, Responses().BAD_TYPE.status),
        ]
        for json, status in cases:
            with self.subTest(json=json, status=status):
                output = (
                    Object(
                        properties={
                            AllOf(
                                "str&bool", required=True, validation_only=True
                            ): {
                                Property("str"): String(),
                                Property("bool"): Boolean(),
                            }
                        }
                    )
                    .assemble()
                    .run(json=json)
                )

                self.assertEqual(output.last_status, status)
                if status == Responses().GOOD.status:
                    self.assertDictEqual(output.data.value, {})
                else:
                    print(output.last_message)


class TestKeyInteractions(TestCase):
    """Tests for interactions between `OneOf` and `AllOf`."""

    def test_one_of_all_of(self):
        """Basic interaction with nested `AllOf`."""
        cases = [
            ({"str": "string"}, Responses().MISSING_REQUIRED_ONEOF.status),
            ({"bool2": True}, Responses().GOOD.status),
            ({"str": "string", "bool": True}, Responses().GOOD.status),
            (
                {"str": "string", "bool": True, "bool2": True},
                Responses().MULTIPLE_ONEOF.status,
            ),
        ]
        for json, status in cases:
            with self.subTest(json=json, status=status):
                output = (
                    Object(
                        properties={
                            OneOf("str&bool|bool2", required=True): {
                                AllOf("str&bool"): {
                                    Property("str"): String(),
                                    Property("bool"): Boolean(),
                                },
                                Property("bool2"): Boolean(),
                            }
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

    def test_all_of_one_of(self):
        """Basic interaction with nested `OneOf`."""
        cases = [
            ({"str": "string"}, Responses().MISSING_REQUIRED_ALLOF.status),
            ({"bool": True}, Responses().MISSING_REQUIRED_ALLOF.status),
            ({"bool2": True}, Responses().MISSING_REQUIRED_ALLOF.status),
            (
                {"str": "string", "bool": True},
                Responses().MISSING_REQUIRED_ALLOF.status,
            ),
            ({"str": "string", "bool2": True}, Responses().GOOD.status),
            ({"bool": True, "bool2": True}, Responses().GOOD.status),
            (
                {"str": "string", "bool": True, "bool2": True},
                Responses().MISSING_REQUIRED_ALLOF.status,
            ),
        ]
        for json, status in cases:
            with self.subTest(json=json, status=status):
                output = (
                    Object(
                        properties={
                            AllOf("(str|bool)&bool2", required=True): {
                                OneOf("str|bool", exclusive=True): {
                                    Property("str"): String(),
                                    Property("bool"): Boolean(),
                                },
                                Property("bool2"): Boolean(),
                            }
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

    def test_complex(self):
        """Complex test for interaction."""
        cases = [
            (
                {"str2": "string2", "str3": "string3", "bool": True},
                Responses().GOOD.status,
            ),
            ({"str": "string", "bool": True}, Responses().GOOD.status),
            (
                {
                    "str": "string",
                    "str2": "string2",
                    "str3": "string3",
                    "bool": True,
                },
                Responses().MISSING_REQUIRED_ALLOF.status,
            ),
            (
                {
                    "str2": "string2",
                    "str3": "string3",
                    "str4": "string4",
                    "bool": True,
                },
                Responses().MISSING_REQUIRED_ALLOF.status,
            ),
            (
                {"str2": "string2", "str4": "string4"},
                Responses().MISSING_REQUIRED_ALLOF.status,
            ),
            (
                {"str2": "string2", "str4": False, "bool": True},
                Responses().MISSING_REQUIRED_ALLOF.status,
            ),
        ]
        for json, status in cases:
            with self.subTest(json=json, status=status):
                output = (
                    Object(
                        properties={
                            AllOf("outer", required=True): {
                                OneOf("str|inner", exclusive=True): {
                                    Property("str"): String(),
                                    AllOf("inner"): {
                                        Property("str2"): String(),
                                        OneOf("inner2"): {
                                            Property("str3"): String(),
                                            Property("str4"): String(),
                                        },
                                    },
                                },
                                Property("bool"): Boolean(),
                            }
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

    def test_complex_objects(self):
        """Complex test with `Object`."""
        cases = [
            ({"str": "string", "bool": True}, Responses().GOOD.status),
            (
                {"obj": {}, "bool": True},
                Responses().MISSING_REQUIRED_ALLOF.status,
            ),
            (
                {"obj": {"str2": "string2"}, "bool": True},
                Responses().MISSING_REQUIRED_ALLOF.status,
            ),
            (
                {
                    "obj": {
                        "str2": "string2",
                        "str3": "string3",
                        "str4": "string4",
                    },
                    "bool": True,
                },
                Responses().MISSING_REQUIRED_ALLOF.status,
            ),
            (
                {"obj": {"str2": "string2", "str3": "string3"}, "bool": True},
                Responses().GOOD.status,
            ),
            (
                {"obj": {"str2": "string2", "str4": "string4"}, "bool": True},
                Responses().GOOD.status,
            ),
        ]
        for json, status in cases:
            with self.subTest(json=json, status=status):
                output = (
                    Object(
                        properties={
                            AllOf("outer", required=True): {
                                OneOf("str|obj", exclusive=True): {
                                    Property("str"): String(),
                                    Property("obj"): Object(
                                        properties={
                                            Property(
                                                "str2", required=True
                                            ): String(),
                                            OneOf("inner2", required=True): {
                                                Property("str3"): String(),
                                                Property("str4"): String(),
                                            },
                                        }
                                    ),
                                },
                                Property("bool"): Boolean(),
                            }
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


class TestObject(TestCase):
    """Tests for `Object` with different key-types and properties."""

    def test_free_form(self):
        """Test occurrence of different key-types in free-form `Object`."""
        cases = [
            ({"str": True}, Responses().BAD_TYPE.status),
            ({"str2": True}, Responses().BAD_TYPE.status),
            ({"str3": True}, Responses().BAD_TYPE.status),
            ({"str4": True}, Responses().BAD_TYPE.status),
            ({"str5": "string"}, Responses().GOOD.status),
        ]
        for json, status in cases:
            with self.subTest(json=json, status=status):
                output = (
                    Object(
                        properties={
                            OneOf("str"): {
                                Property("str"): String(),
                            },
                            AllOf("str2"): {
                                Property("str2"): String(),
                            },
                            OneOf("str3|str4"): {
                                AllOf("str3"): {
                                    Property("str3"): String(),
                                },
                                AllOf("str4"): {
                                    Property("str4"): String(),
                                },
                            },
                        },
                        free_form=True,
                    )
                    .assemble()
                    .run(json=json)
                )

                self.assertEqual(output.last_status, status)
                if status == Responses().GOOD.status:
                    self.assertDictEqual(output.data.value, json)
                else:
                    print(output.last_message)

    def test_additional_properties_true(self):
        """Test `additional_properties=True`."""
        cases = [
            ({"str": True}, Responses().BAD_TYPE.status),
            ({"str2": True}, Responses().BAD_TYPE.status),
            ({"str3": True}, Responses().BAD_TYPE.status),
            ({"str4": True}, Responses().BAD_TYPE.status),
            ({"str5": "string"}, Responses().GOOD.status),
        ]
        for json, status in cases:
            with self.subTest(json=json, status=status):
                output = (
                    Object(
                        properties={
                            OneOf("str"): {
                                Property("str"): String(),
                            },
                            AllOf("str2"): {
                                Property("str2"): String(),
                            },
                            OneOf("str3|str4"): {
                                AllOf("str3"): {
                                    Property("str3"): String(),
                                },
                                AllOf("str4"): {
                                    Property("str4"): String(),
                                },
                            },
                        },
                        additional_properties=True,
                    )
                    .assemble()
                    .run(json=json)
                )

                self.assertEqual(output.last_status, status)
                if status == Responses().GOOD.status:
                    print(output.data.value)
                else:
                    print(output.last_message)

    def test_additional_properties_false(self):
        """Test `additional_properties=False`."""
        cases = [
            ({"str": "string"}, Responses().GOOD.status),
            ({"str2": "string"}, Responses().GOOD.status),
            ({"str3": "string"}, Responses().GOOD.status),
            ({"str4": "string"}, Responses().GOOD.status),
            ({"str5": "string"}, Responses().UNKNOWN_PROPERTY.status),
        ]
        for json, status in cases:
            with self.subTest(json=json, status=status):
                output = (
                    Object(
                        properties={
                            OneOf("str"): {
                                Property("str"): String(),
                            },
                            AllOf("str2"): {
                                Property("str2"): String(),
                            },
                            OneOf("str3|str4"): {
                                AllOf("str3"): {
                                    Property("str3"): String(),
                                },
                                AllOf("str4"): {
                                    Property("str4"): String(),
                                },
                            },
                        },
                        additional_properties=False,
                    )
                    .assemble()
                    .run(json=json)
                )

                self.assertEqual(output.last_status, status)
                if status == Responses().GOOD.status:
                    print(output.data.value)
                else:
                    print(output.last_message)

    def test_additional_properties_dptype(self):
        """Test `additional_properties` parameterized by type."""
        cases = [
            ({"str": True}, Responses().BAD_TYPE.status),
            ({"str2": True}, Responses().BAD_TYPE.status),
            ({"str3": True}, Responses().BAD_TYPE.status),
            ({"str4": True}, Responses().BAD_TYPE.status),
            ({"str5": "string"}, Responses().BAD_TYPE.status),
            ({"bool": True}, Responses().GOOD.status),
        ]
        for json, status in cases:
            with self.subTest(json=json, status=status):
                output = (
                    Object(
                        properties={
                            OneOf("str"): {
                                Property("str"): String(),
                            },
                            AllOf("str2"): {
                                Property("str2"): String(),
                            },
                            OneOf("str3|str4"): {
                                AllOf("str3"): {
                                    Property("str3"): String(),
                                },
                                AllOf("str4"): {
                                    Property("str4"): String(),
                                },
                            },
                        },
                        additional_properties=Boolean(),
                    )
                    .assemble()
                    .run(json=json)
                )

                self.assertEqual(output.last_status, status)
                if status == Responses().GOOD.status:
                    self.assertDictEqual(output.data.value, json)
                else:
                    print(output.last_message)
