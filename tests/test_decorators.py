"""Test decorator integration."""

from unittest import TestCase
from typing import Optional

from flask import Flask, Response, request

from data_plumber_http.keys import Property
from data_plumber_http.types import Object, String, Integer
from data_plumber_http.settings import Responses
from data_plumber_http.decorators import flask_handler, flask_args, flask_json


class TestFlaskArgs(TestCase):
    """Tests for the `flask_args` decorator."""

    def test_minimal(self):
        """Minimal input handler."""
        for arg, status in [
            ("123", Responses().GOOD.status),
            ("abc", Responses().BAD_VALUE.status),
        ]:
            with self.subTest(arg=arg, status=status):
                # pylint: disable=cell-var-from-loop
                base_app = Flask(__name__)
                base_app.config.update({"TESTING": True})

                @base_app.route("/", methods=["GET"])
                @flask_handler(
                    handler=Object(
                        properties={Property("arg"): String(pattern=r"[0-9]+")}
                    ).assemble(),
                    json=flask_args,
                )
                def main(arg: Optional[str] = None):
                    return Response(
                        f"Got '{arg}'.", status=Responses().GOOD.status
                    )

                client = base_app.test_client()

                response = client.get(f"/?arg={arg}")

                self.assertEqual(response.status_code, status)
                self.assertIn(arg, response.data.decode())
                print(response.data.decode())


class TestFlaskJson(TestCase):
    """Tests for the `flask_json` decorator."""

    def test_minimal(self):
        """Minimal input handler."""
        for string, status in [
            ("123", Responses().GOOD.status),
            ("abc", Responses().BAD_VALUE.status),
        ]:
            with self.subTest(string=string, status=status):
                # pylint: disable=cell-var-from-loop
                base_app = Flask(__name__)
                base_app.config.update({"TESTING": True})

                @base_app.route("/", methods=["POST"])
                @flask_handler(
                    handler=Object(
                        properties={
                            Property("string"): String(pattern=r"[0-9]+")
                        }
                    ).assemble(),
                    json=flask_json,
                )
                def main(string: Optional[str] = None):
                    return Response(
                        f"Got '{string}'.", status=Responses().GOOD.status
                    )

                client = base_app.test_client()

                response = client.post("/", json={"string": string})

                self.assertEqual(response.status_code, status)
                self.assertIn(string, response.data.decode())
                print(response.data.decode())

    def test_bad_mimetype(self):
        """
        Input handler where no json is sent.

        This test demonstrates the fix for
        https://github.com/RichtersFinger/data-plumber-http/issues/6
        """
        for test_id, get_json, error in [
            ("unpatched", lambda: request.json, True),
            ("patch", flask_json, False),
        ]:
            with self.subTest(test_id=test_id):
                # pylint: disable=cell-var-from-loop
                base_app = Flask(__name__)
                base_app.config.update({"TESTING": True})

                @base_app.route("/", methods=["POST"])
                @flask_handler(handler=Object().assemble(), json=get_json)
                def main():
                    return Response("Got it.", status=200)

                client = base_app.test_client()

                response = client.post("/")
                if error:
                    self.assertEqual(response.status_code, 415)
                else:
                    self.assertEqual(response.status_code, 200)

    def test_multiple(self):
        """Minimal input handler with multiple properties."""
        base_app = Flask(__name__)
        base_app.config.update({"TESTING": True})

        @base_app.route("/", methods=["POST"])
        @flask_handler(
            handler=Object(
                properties={
                    Property("string"): String(),
                    Property("integer"): Integer(),
                }
            ).assemble(),
            json=flask_json,
        )
        def main(
            string: Optional[str] = None,
            integer: Optional[int] = None,
        ):
            print("json values: ", string, integer)
            return Response("OK", status=Responses().GOOD.status)

        client = base_app.test_client()

        response = client.post("/", json={"string": "string1", "integer": 0})

        self.assertEqual(response.status_code, Responses().GOOD.status)

    def test_missing_required(self):
        """Input handler with missing required input."""
        for test_id, required in [("required", True), ("not-required", False)]:
            with self.subTest(test_id=test_id, required=required):
                # pylint: disable=cell-var-from-loop
                base_app = Flask(__name__)
                base_app.config.update({"TESTING": True})

                @base_app.route("/", methods=["POST"])
                @flask_handler(
                    handler=Object(
                        properties={
                            Property("string", required=required): String(),
                        }
                    ).assemble(),
                    json=flask_json,
                )
                def main(string: Optional[str] = None):
                    print("json values: ", string)
                    return Response("OK", status=Responses().GOOD.status)

                client = base_app.test_client()

                response = client.post("/", json={})

                if not required:
                    self.assertEqual(
                        response.status_code, Responses().GOOD.status
                    )
                else:
                    self.assertEqual(
                        response.status_code,
                        Responses().MISSING_REQUIRED.status,
                    )
                    print(response.data.decode())
