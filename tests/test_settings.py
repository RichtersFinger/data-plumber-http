"""
Part of the test suite for data-plumber-http.

Run with
pytest -v -s
  --cov=data_plumber_http.keys
  --cov=data_plumber_http.types
  --cov=data_plumber_http.decorators
  --cov=data_plumber_http.settings
"""

from unittest import mock

import pytest

from data_plumber_http.settings import Responses


def test_singleton_property():
    """Test singleton-property of `Responses`."""
    assert id(Responses()) == id(Responses())


def test_responses_new():
    """Test method `new` of `Responses()`-singleton."""
    Responses().new("TEST", "Test message.", 5)
    assert Responses().get("TEST").msg == "Test message."
    assert Responses().get("TEST").status == 5
    delattr(Responses(), "TEST")


def test_responses_new_override():
    """Test method `new` of `Responses()`-singleton with `override`."""
    Responses().new("TEST", "Test message.", 5)
    Responses().new("TEST", "Test message 2.", 6, override=True)
    assert Responses().get("TEST").msg == "Test message 2."
    assert Responses().get("TEST").status == 6
    delattr(Responses(), "TEST")


@pytest.mark.parametrize(
    "kwargs",
    [
        {"status": 6},
        {"msg": "Test message 2."},
        {"status": 6, "msg": "Test message 2."},
    ],
    ids=["status", "msg", "status+msg"]
)
def test_responses_update(kwargs):
    """Test method `update` of `Responses()`-singleton."""
    Responses().new("TEST", "Test message.", 5)
    Responses().update("TEST", **kwargs)
    if "status" in kwargs:
        assert Responses().get("TEST").status == kwargs["status"]
    else:
        assert Responses().get("TEST").status == 5
    if "msg" in kwargs:
        assert Responses().get("TEST").msg == kwargs["msg"]
    else:
        assert Responses().get("TEST").msg == "Test message."
    delattr(Responses(), "TEST")


def test_responses_warn():
    """Test for generated warning if native responses are changed."""

    class TestError(Exception):
        "Used as a signal. "

    Responses().new("TEST", "Test message.", 5)
    with mock.patch("data_plumber_http.settings.warnings") as patch:
        def _warn(*args, **kwargs):
            raise TestError()
        patch.warn = _warn

        # no warning due to custom response
        Responses().update("TEST", status=6)
        # warning for internal response
        with pytest.raises(TestError):
            Responses().update("GOOD", status=Responses().GOOD.status)

        # disable warning mechanism
        Responses().warn_on_change = False
        Responses().update("GOOD", status=Responses().GOOD.status)
    Responses().warn_on_change = True
    delattr(Responses(), "TEST")
