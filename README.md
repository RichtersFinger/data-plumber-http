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
pip install data-plumber-http
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
This section gives a brief overview of the features included in this package.

### Contents
1. [Property](#property)
1. [Types](#types)
   1. [Object](#object)
   1. [Array](#array)
   1. [String](#string)
   1. [Boolean](#boolean)
   1. [Integer/Float/Number](#integerfloatnumber)
   1. [Union Types](#union-types)
   1. [Custom Types](#custom-types)
1. [Decorators](#decorators)

### Property
A `Property` is used in conjuction with the `properties`-argument in the `Object` constructor.
It specifies the field-related properties:
* **origin** key name in the input JSON
* **name** given name of the key generated from this `Property` (can be used to map JSON-names to python-names)
* **default** either static value or callable taking input kwargs; used as default if property is missing in request
* **required** whether this property is required
* **fill_with_none** whether fields of missing arguments without a `default`-value/callable are filled with `None` instead
* **validation_only** skip exporting this property to the resulting data and only perform validation

### Types
#### Object
An `Object` corresponds to the JSON-type 'object' and is the base for any input handler-model.
Calling `assemble` on an `Object`-instance returns a `data-plumber`-`Pipeline`.
A `Pipeline.run` expects the keyword argument `json`, a dictionary containing the input data.

Its properties are
* **model** data model (python class) for this `Object` (gets passed the entire output of a `Pipeline`-run)
* **properties** mapping for explicitly expected contents of this `Object`
* **additional_properties** -- type for implicitly expected contents of this `Object` (mutually exclusive with `accept_only`); if this type is set, all contents of the input which are not listed in `properties` have to satisfy the requirements imposed by that type
* **accept_only** -- list of accepted field names; if set, on execution a `json` is rejected with 400 status if it contains a key that is not in `accept_only` (mutually exclusive with `additional_properties`)
* **free_form** -- whether to accept and use any content that has not been defined explicitly via `properties`

#### Array
An `Array` corresponds to the JSON-type 'array'.
Its properties are
* **items** type specification for items of this `Array`; if `None`, instead of performing a validation, all JSON-contents are added to the output ("free-form array")

#### String
A `String` corresponds to the JSON-type 'string'.
Its properties are
* **pattern** regex-pattern that the value of this field has to match
* **enum** list of allowed values for this field

#### Boolean
A `Boolean` corresponds to the JSON-type 'boolean'.

#### Integer/Float/Number
The types `Integer`, `Float`, and `Number` (the latter corresponding to the JSON-type 'number') represent numbers (integers, floating point numbers, and either of those, respectively).
Their properties are
* **values** list of values allowed in this field
* **range_** tuple of lower and upper bound for values in this field

#### Union Types
Types can be combined freely by using the `|`-operator.
A type specification of `Boolean() | String()`, for example, accepts either a boolean- or a string-value.

#### List of Additional Type Definitions
This package also defines some more higher-level types: `Url`, `FileSystemObject`, ...

#### Custom Types
When using this extension, custom types can be defined easily by inheriting from an existing type or, at a lower level, from `data_plumber_http._DPType` and
* defining the `TYPE`-property (python class) as well as
* implementing the `make`-method.
As a simple example for this, consider the following type-definition for a string-type that is required to be prefixed with some string:
```
from data_plumber_http.types import _DPType, Responses

class PrefixedString(_DPType):
    TYPE = str
    def __init__(self, prefix: str):
        self._prefix = prefix
    def make(self, json, loc: str) -> tuple[Any, str, int]:
        if not json.startswith(self._prefix):
            return (
                None,
                Responses.BAD_VALUE.msg.format(
                    json,
                    loc,
                    "a prefix of " + self._prefix
                ),
                Responses.BAD_VALUE.status
            )
        return (
            self.TYPE(json),
            Responses.GOOD.msg,
            Responses.GOOD.status
        )
```
This type can then, for example, be used as
```
Object(
    properties={Property("string"): PrefixedString(prefix="my-prefix:")}
)
```
Running the assembled `Pipeline` with a JSON of `{"string": "my-prefix: hello"}` is returns a good status but `{"string": "missing-prefix: hello"}` is rejected.


### Decorators
This package provides a factory for decorators which allow to seamlessly integrate the validation and unmarshalling of input data with flask view-functions.
See the example given in the section [Usage Example](#usage-example).
The `decorators`-subpackage defines (aside from the decorator-factory `flask_handler`) shortcuts for collecting request data as `json`-input:
* `flask_args`: `request.args`
* `flask_form`: `request.form`
* `flask_files`: `request.files`
* `flask_values`: `request.values`
* `flask_json`: `request.json`

### Status Codes
The status-codes used by `data-plumber-http` are defined in the class `data_plumber_http.Responses`.
By monkey-patching this class, the status codes can be easily altered to one's individual requirements.
```
from data_plumber_http import Responses

Responses.BAD_VALUE.status = 405
```
