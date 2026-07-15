"""
Part of the test suite for data-plumber-http.

Run with
pytest -v -s
  --cov=data_plumber_http.keys
  --cov=data_plumber_http.types
  --cov=data_plumber_http.decorators
  --cov=data_plumber_http.settings
"""

from unittest import mock, TestCase

from data_plumber_http.settings import Responses


class TestResponsesSingleton(TestCase):
    """Tests for singleton-property."""

    def test_property(self):
        """Evaluate identity."""
        self.assertEqual(id(Responses()), id(Responses()))


class TestResponsesNew(TestCase):
    """Tests for `new` method."""

    def test_basic(self):
        """Standard behavior."""
        Responses().new("TEST", "Test message.", 5)
        self.assertEqual(Responses().get("TEST").msg, "Test message.")
        self.assertEqual(Responses().get("TEST").status, 5)
        delattr(Responses(), "TEST")

    def test_override(self):
        """With `override`."""
        Responses().new("TEST", "Test message.", 5)
        Responses().new("TEST", "Test message 2.", 6, override=True)
        self.assertEqual(Responses().get("TEST").msg, "Test message 2.")
        self.assertEqual(Responses().get("TEST").status, 6)
        delattr(Responses(), "TEST")


class TestResponsesUpdate(TestCase):
    """Tests for `update` method."""

    def test_kwargs(self):
        """Parameter combinations."""
        kwargs_list = [
            ("status", {"status": 6}),
            ("msg", {"msg": "Test message 2."}),
            ("status+msg", {"status": 6, "msg": "Test message 2."}),
        ]

        for test_id, kwargs in kwargs_list:
            with self.subTest(test_id=test_id):
                Responses().new("TEST", "Test message.", 5)
                Responses().update("TEST", **kwargs)
                if "status" in kwargs:
                    self.assertEqual(
                        Responses().get("TEST").status, kwargs["status"]
                    )
                else:
                    self.assertEqual(Responses().get("TEST").status, 5)
                if "msg" in kwargs:
                    self.assertEqual(
                        Responses().get("TEST").msg, kwargs["msg"]
                    )
                else:
                    self.assertEqual(
                        Responses().get("TEST").msg, "Test message."
                    )
                delattr(Responses(), "TEST")


class TestResponsesWarn(TestCase):
    """Tests for warnings."""

    def test_native_change(self):
        """Changing native responses."""

        class TestError(Exception):
            "Used as a signal."

        Responses().new("TEST", "Test message.", 5)
        with mock.patch("data_plumber_http.settings.warnings") as patch:

            def _warn(*args, **kwargs):
                raise TestError()

            patch.warn = _warn

            # no warning due to custom response
            Responses().update("TEST", status=6)
            # warning for internal response
            with self.assertRaises(TestError):
                Responses().update("GOOD", status=Responses().GOOD.status)

            # disable warning mechanism
            Responses().warn_on_change = False
            Responses().update("GOOD", status=Responses().GOOD.status)
        Responses().warn_on_change = True
        delattr(Responses(), "TEST")
