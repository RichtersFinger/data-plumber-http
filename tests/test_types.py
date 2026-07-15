"""
Test classes in `types` and their interaction.
"""

from pathlib import Path
from unittest import TestCase

from data_plumber_http.keys import Property
from data_plumber_http.types import (
    Any,
    Array,
    Boolean,
    Float,
    Integer,
    Null,
    Number,
    Object,
    String,
    Uri,
    Url,
    FileSystemObject,
)
from data_plumber_http.settings import Responses


class TestObjectDPTypes(TestCase):
    """Tests for `_DPTypes` in `Object`."""

    def test_basic(self):
        """Test simple types."""
        cases = [
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
            (
                Array(items=String()),
                ["string1", "string2"],
                Responses().GOOD.status,
            ),
            (
                Array(items=Object(free_form=True)),
                [{"field1": 1, "field2": "string"}, {}],
                Responses().GOOD.status,
            ),
            (Array(items=String()), 0, Responses().BAD_TYPE.status),
            (Array(items=String()), [0], Responses().BAD_TYPE.status),
        ]
        for prop, json, status in cases:
            with self.subTest(
                prop=prop.__class__.__name__, json=json, status=status
            ):
                output = (
                    Object(
                        properties={
                            Property("field"): prop,
                        }
                    )
                    .assemble()
                    .run(json={"field": json})
                )

                self.assertEqual(output.last_status, status)
                if status == Responses().GOOD.status:
                    self.assertEqual(output.data.value["field"], json)
                else:
                    print(output.last_message)

    def test_complex(self):
        """Test complex relation of types."""
        cases = [
            ({}, Responses().BAD_TYPE.status),
            (
                [
                    {"field1": 0.1, "field2": [True, "string"]},
                ],
                Responses().BAD_TYPE.status,
            ),
            (
                [
                    {"field2": [0.1, True, "string"]},
                ],
                Responses().BAD_TYPE.status,
            ),
            (
                [
                    {"field1": False, "field2": [True, "string"]},
                    {"field1": "False", "field2": ["True", "string"]},
                ],
                Responses().GOOD.status,
            ),
        ]
        for json, status in cases:
            with self.subTest(json=json, status=status):
                output = (
                    Object(
                        properties={
                            Property("field"): Array(
                                items=Object(
                                    properties={
                                        Property("field1"): Boolean()
                                        | String(),
                                        Property("field2"): Array(
                                            items=Boolean() | String()
                                        ),
                                    }
                                )
                            )
                        }
                    )
                    .assemble()
                    .run(json={"field": json})
                )

                self.assertEqual(output.last_status, status)
                if status == Responses().GOOD.status:
                    self.assertEqual(output.data.value["field"], json)
                else:
                    print(output.last_message)

    def test_complex_union(self):
        """Test union of complex relations."""
        cases = [
            ([True, False, True], Responses().GOOD.status),
            (["string1", "string2"], Responses().GOOD.status),
            (["string1", True], Responses().BAD_TYPE.status),
        ]
        for json, status in cases:
            with self.subTest(json=json, status=status):
                output = (
                    Object(
                        properties={
                            Property("field"): Array(items=Boolean())
                            | Array(items=String())
                        }
                    )
                    .assemble()
                    .run(json={"field": json})
                )

                self.assertEqual(output.last_status, status)
                if status == Responses().GOOD.status:
                    self.assertEqual(output.data.value["field"], json)
                else:
                    print(output.last_message)


class TestString(TestCase):
    """Tests for type `String`."""

    def test_pattern(self):
        """Test property `pattern`."""
        cases = [
            ("string1", Responses().GOOD.status),
            ("string", Responses().BAD_VALUE.status),
            ("string11", Responses().BAD_VALUE.status),
        ]
        for json, status in cases:
            with self.subTest(json=json, status=status):
                output = (
                    Object(
                        properties={
                            Property("field"): String(pattern=r"string[0-9]")
                        }
                    )
                    .assemble()
                    .run(json={"field": json})
                )

                self.assertEqual(output.last_status, status)
                if status == Responses().GOOD.status:
                    self.assertEqual(output.data.value["field"], json)
                else:
                    print(output.last_message)

    def test_enum(self):
        """Test property `enum`."""
        cases = [
            ("string1", Responses().GOOD.status),
            ("string2", Responses().GOOD.status),
            ("string", Responses().BAD_VALUE.status),
            ("string11", Responses().BAD_VALUE.status),
        ]
        for json, status in cases:
            with self.subTest(json=json, status=status):
                output = (
                    Object(
                        properties={
                            Property("field"): String(
                                enum=["string1", "string2"]
                            )
                        }
                    )
                    .assemble()
                    .run(json={"field": json})
                )

                self.assertEqual(output.last_status, status)
                if status == Responses().GOOD.status:
                    self.assertEqual(output.data.value["field"], json)
                else:
                    print(output.last_message)


class TestInteger(TestCase):
    """Tests for type `Integer`."""

    def test_values(self):
        """Test property `values`."""
        cases = [
            (1, Responses().GOOD.status),
            (2, Responses().GOOD.status),
            (0, Responses().BAD_VALUE.status),
        ]
        for json, status in cases:
            with self.subTest(json=json, status=status):
                output = (
                    Object(
                        properties={Property("field"): Integer(values=[1, 2])}
                    )
                    .assemble()
                    .run(json={"field": json})
                )

                self.assertEqual(output.last_status, status)
                if status == Responses().GOOD.status:
                    self.assertEqual(output.data.value["field"], json)
                else:
                    print(output.last_message)

    def test_min_max_value(self):
        """Test properties for value ranges."""
        cases = [
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
        for options, json, status in cases:
            with self.subTest(options=options, json=json, status=status):
                output = (
                    Object(properties={Property("field"): Integer(**options)})
                    .assemble()
                    .run(json={"field": json})
                )

                self.assertEqual(output.last_status, status)
                if status == Responses().GOOD.status:
                    self.assertEqual(output.data.value["field"], json)
                else:
                    print(output.last_message)


class TestFloat(TestCase):
    """Tests for type `Float`."""

    def test_values(self):
        """Test property `values`."""
        cases = [
            (1.0, Responses().GOOD.status),
            (3.5, Responses().GOOD.status),
            (0.9, Responses().BAD_VALUE.status),
        ]
        for json, status in cases:
            with self.subTest(json=json, status=status):
                output = (
                    Object(
                        properties={
                            Property("field"): Float(values=[1.0, 3.5])
                        }
                    )
                    .assemble()
                    .run(json={"field": json})
                )

                self.assertEqual(output.last_status, status)
                if status == Responses().GOOD.status:
                    self.assertEqual(output.data.value["field"], json)
                else:
                    print(output.last_message)

    def test_min_max_value(self):
        """Test properties for value ranges."""
        cases = [
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
        for options, json, status in cases:
            with self.subTest(options=options, json=json, status=status):
                output = (
                    Object(properties={Property("field"): Float(**options)})
                    .assemble()
                    .run(json={"field": json})
                )

                self.assertEqual(output.last_status, status)
                if status == Responses().GOOD.status:
                    self.assertEqual(output.data.value["field"], json)
                else:
                    print(output.last_message)


class TestNumber(TestCase):
    """Tests for type `Number`."""

    def test_values(self):
        """Test property `values`."""
        cases = [
            (1, Responses().GOOD.status),
            (2, Responses().GOOD.status),
            (3.5, Responses().GOOD.status),
            (0, Responses().BAD_VALUE.status),
            (0.9, Responses().BAD_VALUE.status),
        ]
        for json, status in cases:
            with self.subTest(json=json, status=status):
                output = (
                    Object(
                        properties={
                            Property("field"): Number(values=[1, 2, 3.5])
                        }
                    )
                    .assemble()
                    .run(json={"field": json})
                )

                self.assertEqual(output.last_status, status)
                if status == Responses().GOOD.status:
                    self.assertEqual(output.data.value["field"], json)
                else:
                    print(output.last_message)

    def test_min_max_value(self):
        """Test properties for value ranges."""
        cases = [
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
        for options, json, status in cases:
            with self.subTest(options=options, json=json, status=status):
                output = (
                    Object(properties={Property("field"): Number(**options)})
                    .assemble()
                    .run(json={"field": json})
                )

                self.assertEqual(output.last_status, status)
                if status == Responses().GOOD.status:
                    self.assertEqual(output.data.value["field"], json)
                else:
                    print(output.last_message)


class TestUrl(TestCase):
    """Tests for type `Url`."""

    def test_basic(self):
        """Test basic validation."""
        cases = [
            ("http://pypi.org/path", Responses().GOOD.status),
            ("http://pypi.org", Responses().GOOD.status),
            ("pypi.org", Responses().GOOD.status),  # interpreted as path
            ("http", Responses().GOOD.status),
            ("http://", Responses().GOOD.status),
            ("http:/path", Responses().GOOD.status),
        ]
        for json, status in cases:
            with self.subTest(json=json, status=status):
                output = (
                    Object(properties={Property("field"): Url()})
                    .assemble()
                    .run(json={"field": json})
                )

                self.assertEqual(output.last_status, status)
                if status == Responses().GOOD.status:
                    self.assertEqual(output.data.value["field"], json)
                else:
                    print(output.last_message)

    def test_schemes(self):
        """Test property `schemes`."""
        cases = [
            ("http://pypi.org", Responses().GOOD.status),
            ("custom://pypi.org", Responses().GOOD.status),
            ("sftp://pypi.org", Responses().BAD_VALUE.status),
            ("pypi.org", Responses().BAD_VALUE.status),
        ]
        for json, status in cases:
            with self.subTest(json=json, status=status):
                output = (
                    Object(
                        properties={
                            Property("field"): Url(schemes=["http", "custom"])
                        }
                    )
                    .assemble()
                    .run(json={"field": json})
                )

                self.assertEqual(output.last_status, status)
                if status == Responses().GOOD.status:
                    self.assertEqual(output.data.value["field"], json)
                else:
                    print(output.last_message)

    def test_require_netloc(self):
        """Test property `require_netloc`."""
        cases = [
            ("http://pypi.org/path", Responses().GOOD.status),
            ("http://pypi.org", Responses().GOOD.status),
            ("pypi.org", Responses().BAD_VALUE.status),
            ("://pypi.org", Responses().BAD_VALUE.status),
            ("http://", Responses().BAD_VALUE.status),
            ("http:/path", Responses().BAD_VALUE.status),
            ("", Responses().BAD_VALUE.status),
        ]
        for json, status in cases:
            with self.subTest(json=json, status=status):
                output = (
                    Object(
                        properties={
                            Property("field"): Url(require_netloc=True)
                        }
                    )
                    .assemble()
                    .run(json={"field": json})
                )

                self.assertEqual(output.last_status, status)
                if status == Responses().GOOD.status:
                    self.assertEqual(output.data.value["field"], json)
                else:
                    print(output.last_message)

    def test_return_parsed(self):
        """Test property `return_parsed`."""
        output = (
            Object(properties={Property("field"): Url(return_parsed=True)})
            .assemble()
            .run(json={"field": "http://pypi.org/path"})
        )

        self.assertEqual(output.last_status, Responses().GOOD.status)
        self.assertTrue(hasattr(output.data.value["field"], "scheme"))
        self.assertTrue(hasattr(output.data.value["field"], "netloc"))
        self.assertTrue(hasattr(output.data.value["field"], "path"))


class TestUri(TestCase):
    """Tests for type `Uri`."""

    def test_basic(self):
        """Test basic validation."""
        cases = [
            ("http://pypi.org/path", Responses().GOOD.status),
            ("http://pypi.org", Responses().GOOD.status),
            ("pypi.org", Responses().GOOD.status),  # interpreted as path
            ("http", Responses().GOOD.status),
            ("http://", Responses().GOOD.status),
            ("http:/path", Responses().GOOD.status),
        ]
        for json, status in cases:
            with self.subTest(json=json, status=status):
                output = (
                    Object(properties={Property("field"): Uri()})
                    .assemble()
                    .run(json={"field": json})
                )

                self.assertEqual(output.last_status, status)
                if status == Responses().GOOD.status:
                    self.assertEqual(output.data.value["field"], json)
                else:
                    print(output.last_message)

    def test_schemes(self):
        """Test property `schemes`."""
        cases = [
            ("http://pypi.org", Responses().GOOD.status),
            ("custom://pypi.org", Responses().GOOD.status),
            ("sftp://pypi.org", Responses().BAD_VALUE.status),
            ("pypi.org", Responses().BAD_VALUE.status),
        ]
        for json, status in cases:
            with self.subTest(json=json, status=status):
                output = (
                    Object(
                        properties={
                            Property("field"): Uri(schemes=["http", "custom"])
                        }
                    )
                    .assemble()
                    .run(json={"field": json})
                )

                self.assertEqual(output.last_status, status)
                if status == Responses().GOOD.status:
                    self.assertEqual(output.data.value["field"], json)
                else:
                    print(output.last_message)

    def test_require_authority(self):
        """Test property `require_authority`."""
        cases = [
            ("http://pypi.org/path", Responses().GOOD.status),
            ("http://pypi.org", Responses().GOOD.status),
            ("pypi.org", Responses().BAD_VALUE.status),
            ("://pypi.org", Responses().BAD_VALUE.status),
            ("http://", Responses().BAD_VALUE.status),
            ("http:/path", Responses().BAD_VALUE.status),
            ("", Responses().BAD_VALUE.status),
        ]
        for json, status in cases:
            with self.subTest(json=json, status=status):
                output = (
                    Object(
                        properties={
                            Property("field"): Uri(require_authority=True)
                        }
                    )
                    .assemble()
                    .run(json={"field": json})
                )

                self.assertEqual(output.last_status, status)
                if status == Responses().GOOD.status:
                    self.assertEqual(output.data.value["field"], json)
                else:
                    print(output.last_message)

    def test_return_parsed(self):
        """Test property `return_parsed`."""
        output = (
            Object(properties={Property("field"): Uri(return_parsed=True)})
            .assemble()
            .run(json={"field": "http://pypi.org/path"})
        )

        self.assertEqual(output.last_status, Responses().GOOD.status)
        self.assertTrue(hasattr(output.data.value["field"], "scheme"))
        self.assertTrue(hasattr(output.data.value["field"], "netloc"))
        self.assertTrue(hasattr(output.data.value["field"], "path"))


class TestFileSystemObject(TestCase):
    """Tests for type `FileSystemObject`."""

    def test_options(self):
        """Test various instantiation options."""
        cases = [
            ("basic", {}, __file__, Responses().GOOD.status),
            (
                "exists-good",
                {"exists": True},
                __file__,
                Responses().GOOD.status,
            ),
            (
                "is_file-good",
                {"is_file": True},
                __file__,
                Responses().GOOD.status,
            ),
            (
                "is_dir-good",
                {"is_dir": False},
                __file__,
                Responses().GOOD.status,
            ),
            (
                "is_file-conflict",
                {"is_file": False},
                __file__,
                Responses().CONFLICT.status,
            ),
            (
                "is_dir-but file",
                {"is_file": True},
                str(Path(__file__).parent),
                Responses().BAD_RESOURCE.status,
            ),
            (
                "is_fifo-but file",
                {"is_dir": True},
                __file__,
                Responses().BAD_RESOURCE.status,
            ),
            (
                "is_file-but dir",
                {"is_fifo": True},
                __file__,
                Responses().BAD_RESOURCE.status,
            ),
            (
                "is_file-not found",
                {"is_file": True},
                __file__ + ".x",
                Responses().RESOURCE_NOT_FOUND.status,
            ),
            (
                "relative_to-relative-good",
                {"relative_to": Path("tests")},
                str(Path(__file__).relative_to(Path(__file__).parents[1])),
                Responses().GOOD.status,
            ),
            (
                "relative_to-absolute-bad",
                {"relative_to": Path(__file__).parent},
                str(Path(__file__).parents[1] / "another_path"),
                Responses().BAD_VALUE.status,
            ),
            (
                "relative_to-mixed-bad",
                {"relative_to": Path(".")},
                __file__,
                Responses().BAD_VALUE.status,
            ),
            (
                "cwd",
                {"cwd": Path("tests"), "is_file": True},
                Path(__file__).name,
                Responses().GOOD.status,
            ),
        ]
        for case_id, kwargs, json, status in cases:
            with self.subTest(
                case_id=case_id, kwargs=kwargs, json=json, status=status
            ):
                output = (
                    Object(
                        properties={
                            Property("field"): FileSystemObject(**kwargs)
                        }
                    )
                    .assemble()
                    .run(json={"field": json})
                )

                self.assertEqual(output.last_status, status)
                if status == Responses().GOOD.status:
                    if "relative_to" in kwargs:
                        self.assertEqual(
                            Path(json).relative_to(kwargs["relative_to"]),
                            output.data.value["field"],
                        )
                    elif "cwd" in kwargs:
                        self.assertEqual(
                            output.data.value["field"], kwargs["cwd"] / json
                        )
                    else:
                        self.assertEqual(str(output.data.value["field"]), json)
                else:
                    print(output.last_message)


class TestAny(TestCase):
    """Tests for type `Any`."""

    def test_basic(self):
        """Test basic validation."""
        cases = [
            ([1, "string1"], Responses().GOOD.status),
            (True, Responses().GOOD.status),
            (0.1, Responses().GOOD.status),
            (1, Responses().GOOD.status),
            (None, Responses().GOOD.status),
            ({"inner-field": "value"}, Responses().GOOD.status),
            ("string1", Responses().GOOD.status),
        ]
        for json, status in cases:
            with self.subTest(json=json, status=status):
                output = (
                    Object(properties={Property("field"): Any()})
                    .assemble()
                    .run(json={"field": json})
                )

                self.assertEqual(output.last_status, status)
                if status == Responses().GOOD.status:
                    self.assertEqual(output.data.value["field"], json)
