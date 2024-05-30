"""
Part of the test suite for data-plumber-http.

Run with
pytest -v -s
  --cov=data_plumber_http.keys
  --cov=data_plumber_http.types
  --cov=data_plumber_http.decorators
  --cov=data_plumber_http.settings
"""

from typing import Optional
from dataclasses import dataclass

from flask import Flask, Response

from data_plumber_http import Property, Object, Array, String, Integer
from data_plumber_http.decorators import flask_handler, flask_json


def test_pet_post():
    """Test documentation example."""
    # define data-models
    @dataclass
    class Tag:
        id_: Optional[int] = None
        name: Optional[str] = None

    @dataclass
    class Category:
        id_: Optional[int] = None
        name: Optional[str] = None

    # define data-plumber-http-model
    pet_post = Object(
        properties={
            Property("name", required=True): String(),
            Property("photoUrls", name="photo_urls", required=True):
                Array(items=String()),
            Property("id", name="id_"): Integer(),
            Property("category"): Object(
                model=Category,
                properties={
                    Property("id", name="id_", required=True): Integer(),
                    Property("name", required=True): String(),
                }
            ),
            Property("tags"): Array(
                items=Object(
                    model=Tag,
                    properties={
                        Property("id", name="id_", required=True): Integer(),
                        Property("name", required=True): String(),
                    }
                )
            ),
            Property("status"): String(enum=["available", "pending", "sold"]),
        }
    )

    # setup minimal flask-app with handler for pet_model
    app = Flask(__name__)
    @app.route("/pet", methods=["POST"])
    @flask_handler(
        handler=pet_post.assemble(),
        json=flask_json
    )
    def pet(
        name: str,
        photo_urls: list[str],
        id_: Optional[int] = None,
        category: Optional[Category] = None,
        tags: Optional[list[Tag]] = None,
        status: Optional[str] = None
    ):
        return Response(
            f"OK: {name}, {photo_urls}, {id_}, {category}, {tags}, {status}",
            200
        )

    # make api-call
    response = app.test_client().post(
        "/pet",
        json={
            "id": 10,
            "name": "doggie",
            "category": {
                "id": 1,
                "name": "Dogs"
            },
            "photoUrls": [
                "string"
            ],
            "tags": [
                {
                    "id": 0,
                    "name": "string"
                }
            ],
            "status": "available"
        }
    )

    # eval
    print(response.data.decode())
    assert response.status_code == 200
