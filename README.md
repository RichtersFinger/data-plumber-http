 ![Tests](https://github.com/RichtersFinger/data-plumber-http/actions/workflows/tests.yml/badge.svg?branch=main) ![PyPI - License](https://img.shields.io/pypi/l/data-plumber-http) ![GitHub top language](https://img.shields.io/github/languages/top/RichtersFinger/data-plumber-http) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/data-plumber-http) ![PyPI version](https://badge.fury.io/py/data-plumber-http.svg) ![PyPI - Wheel](https://img.shields.io/pypi/wheel/data-plumber-http)

# data-plumber-http
This extension to the [`data-plumber`](https://github.com/RichtersFinger/data-plumber)-framework provides a mechanism to validate and unmarshal data in http-requests using a highly declarative format.
If a problem occurs, a suitable status-code and message containing a brief description of the problem are generated automatically.
It is
* configurable: automatically generated messages and status codes can be customized
* extendable: custom data structures can be defined without much overhead

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
```python
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
```python
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
```python
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
1. [Keys](#keys)
   1. [Property](#property)
   1. [OneOf/AllOf](#oneof-and-allof)
1. [Types](#types)
   1. [Object, Array, String, ...](#object)
   1. [Union Types](#union-types)
   1. [Custom Types](#custom-types)
1. [Decorators](#decorators)
1. [Response Configuration](#response-configuration)

### Keys
A `DPKey` is used in conjuction with the `properties`-argument in the `Object` constructor.

#### Property
A `Property` is the simplest form for a `DPKey`.
It specifies the field-related properties:
* **origin** key name in the input JSON
* **name** given name of the key generated from this `Property` (can be used to map JSON-names to python-names)
* **default** either static value or callable taking `Pipeline` input kwargs (see [`data-plumber` documentation](https://github.com/RichtersFinger/data-plumber/blob/main/docs/pipeline.md#running-a-pipeline)); used as default if property is missing in request
* **required** whether this property is required
* **validation_only** skip exporting this property to the resulting data and only perform validation

#### OneOf and AllOf
These are conditional `DPKey`s which can be used to declare simple conditional structures within the `properties`-map of an `Object`.
More complex relations are better processed in custom models or `DPType`s.
These conditional keys have the properties
* **name** name identifier for this key (may be useful for debugging)
* **exclusive** (`OneOf` only) whether exactly one match has to be made or multiple matches are allowed
* **default** (see `Property`)
* **required** (see `Property`)
* **validation_only** (see `Property`)

A simple `Object`-handler that accepts either `{"str": <string>, "bool": <boolean>}` or `{"int": <boolean>}` may take the form of
```python
Object(
    properties={
        OneOf("str&bool|int", exclusive=True): {
            AllOf("str&bool"): {
                Property("str"): String(),
                Property("bool"): Boolean()
            },
            Property("int"): Integer()
        }
    }
)
```
Note that in conditionally nested structures like in the example above, most properties of the inner `DPKey`s are silently ignored, i.e. all but `origin` and `name`.
To have, for example, a `default`-value, it needs to be configured for the outermost `DPKey` (`OneOf("str&bool|int", ...)` in the example).

See also [Union Types](#union-types).

### Types
#### Object
An `Object` corresponds to the JSON-type 'object' and is the base for any input handler-model.
Calling `assemble` on an `Object`-instance returns a `data-plumber`-`Pipeline`.
A `Pipeline.run` expects the keyword argument `json`, a dictionary containing the input data.

Its regular properties are
* **model** data model (python class) for this `Object` or factory function (gets passed the entire output of a `Pipeline`-run)
* **properties** mapping for explicitly expected contents of this `Object`; this mapping is stored as the public property `properties`

Additionally, there are different options to configure how unknown properties in the input are treated.
These are mutually exclusive:
* **additional_properties** -- either boolean or field type
  * boolean: if `True`, ignore any additional fields; if `False`, rejects fields that are not listed in `properties`
  * type: required type specification for implicitly expected contents of this `Object`; if this type is set, all contents of the input which are not listed in `properties` have to satisfy the requirements imposed by that type; corresponding fields in `json` are added to the output
* **accept_only** -- list of accepted field names; if set, on execution a `json` is rejected if it contains a key that is not in `accept_only`
* **free_form** -- whether to accept and include any content that has not been defined explicitly via `properties`

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
* **min_value**, **min_value_invlusive**, **max_value**, **max_value_inclusive** configuration for accepted value ranges

#### Null
The `Null`-type represents a JSON-'null' and generates a `None` value in python.

#### Any
The `Any`-type can be used to indicate a field to be of free form.
Any regular JSON-type (`Array` (free-form), `Boolean`, `Float`, `Integer`, `Null`, `Object` (free-form), and `String`) is accepted here.

#### Uri/Url
The types `Uri` and `Url` can be used to declare fields that are required to have a uri- or url-format.
Their properties are
* **schemes** list of strings that are accepted as schemes (omit for accepting any)
* **require_authority** (`Uri` only) whether to require a non-empty authority-section
* **require_netloc** (`Url` only) whether to require a non-empty netloc-section
* **return_parsed** whether to return a string or named tuple (result from a call to `urllib.parse.urlparse`)

#### FileSystemObject
The `FileSystemObject`-type implements a rudimentary validation logic for references to objects within a file system.
Properties are
* **cwd** override the process's cwd; the input is appended to this `Path` prior to validation
* **relative_to** make call to `pathlib.Path.relative_to` prior to validation
* **exists**, **is_file**, **is_dir**, **is_fifo** collection of validation options; any omitted value is skipped during validation

#### Union Types
Types can be combined freely by using the `|`-operator.
A type specification of `Boolean() | String()`, for example, accepts either a boolean- or a string-value.

#### Custom Types
When using this extension, custom types can be defined easily by inheriting from an existing `DPType` or, at a lower level, from their common interface `data_plumber_http.DPType` itself and
* defining the `TYPE`-property (python class) as well as
* implementing the `make`-method.
As a simple example for this, consider the following type-definition for a string-type that is required to be prefixed with some string:
```python
from typing import Any

from data_plumber_http import DPType
from data_plumber_http.settings import Responses

class PrefixedString(DPType):
    TYPE = str
    def __init__(self, prefix: str):
        self._prefix = prefix
    def make(self, json, loc: str) -> tuple[Any, str, int]:
        if not json.startswith(self._prefix):
            return (
                None,
                Responses().BAD_VALUE.msg.format(
                    origin=json,
                    loc=loc,
                    expected="a prefix of " + self._prefix
                ),
                Responses().BAD_VALUE.status
            )
        return (
            self.TYPE(json),
            Responses().GOOD.msg,
            Responses().GOOD.status
        )
```
This type can then, for example, be used as
```python
Object(
    properties={Property("string"): PrefixedString(prefix="my-prefix:")}
)
```
Running the assembled `Pipeline` with a `json`-keyword argument (`Object(..).assemble().run(json={"string": ...})`) of `{"string": "my-prefix: hello"}` returns a good status but `{"string": "missing-prefix: hello"}` is rejected.

### Decorators
This package provides a factory for decorators which allow to seamlessly integrate the validation and unmarshalling of input data with flask view-functions.
See the example given in the section [Usage Example](#usage-example).
The `decorators`-subpackage defines (aside from the decorator-factory `flask_handler`) shortcuts for collecting request data as `json`-input:
* `flask_args`: `request.args`
* `flask_form`: `request.form`
* `flask_files`: `request.files`
* `flask_values`: `request.values`
* `flask_json`: `request.json`

### Response Configuration
The status-codes and messages used by `data-plumber-http` are defined in the class `data_plumber_http.settings.Responses`.
By modifying the respective (singleton) object, the status codes (or messages) can be easily altered to one's individual requirements.
```python
from data_plumber_http.settings import Responses

Responses().update("BAD_VALUE", status = 406)
```

You can also register new response types which can then be used in custom `DPTypes`
```python
Responses().new(
    "DELETED",
    msg="Resource '{json}' requested in '{loc}' has been permanently deleted.",
    status = 410
)
...
class MyResource(DPType):
    TYPE = str
    ...
    def make(self, json, loc):
        ...
        return (
            None,
            Responses().DELETED.msg.format(
                json=json,
                loc=loc
            ),
            Responses().DELETED.status
        )
```

Note that changing the status codes of pre-defined responses into a different range (e.g. 4XX- to 2XX-range) can break the extension's functionality.
Corresponding warnings can be disabled by changing the `warn_on_change` property of `Responses()`.
