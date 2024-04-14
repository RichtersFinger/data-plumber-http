 ![Tests](https://github.com/RichtersFinger/data-plumber-http/actions/workflows/tests.yml/badge.svg?branch=main) ![PyPI - License](https://img.shields.io/pypi/l/data-plumber-http) ![GitHub top language](https://img.shields.io/github/languages/top/RichtersFinger/data-plumber-http) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/data-plumber-http) ![PyPI version](https://badge.fury.io/py/data-plumber-http.svg) ![PyPI - Wheel](https://img.shields.io/pypi/wheel/data-plumber-http)

# data-plumber-http
This extension to the [`data-plumber`](https://github.com/RichtersFinger/data-plumber)-framework provides a mechanism to validate and unmarshal data in http-requests using a highly declarative format.
If a problem occurrs, a suitable status-code and message containing a brief description of the problem are generated automatically.
The extension also defines a decorator for a seamless integration with `flask`-web apps.

## Contents
1. [Install](#install)
1. [Usage Example](#usage-example)
1. [Documentation](#documentation)
1. [Changelog](CHANGELOG.md)

## Install
Install using `pip` with
```
pip install data-plumber[http]
```
Consider installing in a virtual environment.

## Usage example
Consider a minimal `flask`-app implementing the `/pet`-POST endpoint of the [`Swagger Petstore - OpenAPI 3.0`](https://petstore3.swagger.io/#/pet/addPet).
A suitable unmarshalling-model may look like
```
from data_plumber_http import Property, Object, Array, String, Integer

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
```
Here, the arguments `model=Category` and `model=Tag` refer to separately defined python classes `Category` and `Tag`, i.e.
```
from typing import Optional
from dataclasses import dataclass

@dataclass
class Tag:
    id_: Optional[int] = None
    name: Optional[str] = None

@dataclass
class Category:
    id_: Optional[int] = None
    name: Optional[str] = None
```
In a `flask` app, this model can then be used as
```
from flask import Flask, Response
from data_plumber_http.decorators import flask_handler, flask_json

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
```
Based on the example-request body given in the Pet Store API (`{"id": 10, "name": "doggie", "category": {"id": 1, "name": "Dogs"}, "photoUrls": ["string"], "tags": [{"id": 0, "name": "string"}], "status": available"}`), this app returns with
```
"OK: doggie, ['string'], 10, test_pet_post.<locals>.Category(id_=1, name='Dogs'), [test_pet_post.<locals>.Tag(id_=0, name='string')], available"
```

## Documentation

### Property
### Types
### Decorators
