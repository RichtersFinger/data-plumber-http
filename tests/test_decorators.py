"""
Part of the test suite for data-plumber-flask.

Run with
pytest -v -s --cov=data_plumber_http.keys --cov=data_plumber_http.types --cov=data_plumber_http.decorators
"""

from typing import Optional

import pytest
from flask import Flask, Response, request as flask_request

from data_plumber_http.keys import Property
from data_plumber_http.types import Responses, Object, String, Integer
from data_plumber_http.decorators \
     import flask_handler, flask_args, flask_json


@pytest.fixture(name="base_app")
def _base_app():
    app = Flask(__name__)
    app.config.update({
        "TESTING": True,
    })
    return app


@pytest.mark.parametrize(
    ("arg", "status"),
    [
        ("123", Responses.GOOD.status),
        ("abc", Responses.BAD_VALUE.status)
    ]
)
def test_flask_args_minimal(base_app, arg, status):
    """Test minimal input handler for args."""

    @base_app.route("/", methods=["GET"])
    @flask_handler(
        handler=Object(
            properties={
                Property("arg"): String(pattern=r"[0-9]+")
            }
        ).assemble(),
        json=flask_args
    )
    def main(
        arg: Optional[str] = None
    ):
        return Response(f"Got '{arg}'.", status=Responses.GOOD.status)

    client = base_app.test_client()

    response = client.get(f"/?arg={arg}")

    assert response.status_code == status
    assert arg in response.data.decode()
    print(response.data.decode())


@pytest.mark.parametrize(
    ("string", "status"),
    [
        ("123", Responses.GOOD.status),
        ("abc", Responses.BAD_VALUE.status)
    ]
)
def test_flask_json_minimal(base_app, string, status):
    """Test minimal input handler for json."""

    @base_app.route("/", methods=["POST"])
    @flask_handler(
        handler=Object(
            properties={
                Property("string"): String(pattern=r"[0-9]+")
            }
        ).assemble(),
        json=flask_json
    )
    def main(
        string: Optional[str] = None
    ):
        return Response(f"Got '{string}'.", status=Responses.GOOD.status)

    client = base_app.test_client()

    response = client.post("/", json={"string": string})

    assert response.status_code == status
    assert string in response.data.decode()
    print(response.data.decode())


def test_flask_json_multiple(base_app):
    """Test minimal input handler for json with multiple properties."""

    @base_app.route("/", methods=["POST"])
    @flask_handler(
        handler=Object(
            properties={
                Property("string"): String(),
                Property("integer"): Integer(),
            }
        ).assemble(),
        json=flask_json
    )
    def main(
        string: Optional[str] = None,
        integer: Optional[int] = None,
    ):
        return Response("OK", status=Responses.GOOD.status)

    client = base_app.test_client()

    response = client.post(
        "/",
        json={"string": "string1", "integer": 0}
    )

    assert response.status_code == Responses.GOOD.status


@pytest.mark.parametrize(
    "required",
    [True, False],
    ids=["required", "not-required"]
)
def test_flask_json_missing_required(base_app, required):
    """Test input handler for json with missing required input."""

    @base_app.route("/", methods=["POST"])
    @flask_handler(
        handler=Object(
            properties={
                Property("string", required=required): String(),
            }
        ).assemble(),
        json=flask_json
    )
    def main(
        string: Optional[str] = None
    ):
        return Response("OK", status=Responses.GOOD.status)

    client = base_app.test_client()

    response = client.post(
        "/",
        json={}
    )

    if not required:
        assert response.status_code == Responses.GOOD.status
    else:
        assert response.status_code == Responses.MISSING_REQUIRED.status
        print(response.data.decode())
