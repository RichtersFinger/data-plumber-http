"""
Part of the test suite for data-plumber-http.

Run with
pytest -v -s
  --cov=data_plumber_http.keys
  --cov=data_plumber_http.types
  --cov=data_plumber_http.decorators
  --cov=data_plumber_http.settings
"""

import pytest

from data_plumber_http.keys import Property, OneOf, AllOf
from data_plumber_http.types \
    import Boolean, String, Object
from data_plumber_http.settings import Responses


@pytest.mark.parametrize(
    ("json", "status"),
    [
        ({"str": "string"}, Responses().GOOD.status),
        ({"bool": True}, Responses().GOOD.status),
        ({"bool": 0.1}, Responses().BAD_TYPE.status),
        ({"str": "string", "bool": True}, Responses().MULTIPLE_ONEOF.status),
    ]
)
def test_one_of_simple(json, status):
    """Basic test for key `OneOf`."""
    output = Object(
        properties={
            OneOf("str|bool", required=True): {
                Property("str"): String(),
                Property("bool"): Boolean()
            }
        }
    ).assemble().run(json=json)

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("exclusive", "status"),
    [
        (True, Responses().MULTIPLE_ONEOF.status),
        (False, Responses().GOOD.status),
    ],
    ids=["exclusive", "non-exclusive"]
)
def test_one_of_exclusive(exclusive, status):
    """Test argument `exclusive` for key `OneOf`."""
    json = {"str": "string", "bool": True}
    output = Object(
        properties={
            OneOf("str|bool", exclusive=exclusive): {
                Property("str"): String(),
                Property("bool"): Boolean()
            }
        }
    ).assemble().run(json=json)

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert len(output.data.value) == 1
        key = list(output.data.value.keys())[0]
        assert key in json
        assert output.data.value[key] == json[key]
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("properties", "required"),
    [
        ({Property("str", required=True): String()}, True),
        ({OneOf("str", required=True): {Property("str"): String()}}, True),
        ({AllOf("str", required=True): {Property("str"): String()}}, True),
        ({Property("str", required=False): String()}, False),
        ({OneOf("str", required=False): {Property("str"): String()}}, False),
        ({AllOf("str", required=False): {Property("str"): String()}}, False),
    ],
    ids=[
        "Property_req", "OneOf_req", "AllOf_req", "Property_opt", "OneOf_opt",
        "AllOf_opt",
    ]
)
@pytest.mark.parametrize(
    "json",
    [
        {"str": "string"},
        {"no-str": "string"},
    ],
    ids=["arg_present", "arg_missing"]
)
def test_key_required(properties, required, json):
    """Test argument `required` for keys `Property`, `OneOf`, and `AllOf`."""
    output = Object(
        properties=properties
    ).assemble().run(json=json)

    if not required or "str" in json:
        assert output.last_status == Responses().GOOD.status
    else:
        assert output.last_status != Responses().GOOD.status
    if "str" in json:
        assert output.data.value == json


@pytest.mark.parametrize(
    "properties",
    [
        {Property("str", default="default"): String()},
        {OneOf("str", default="default"): {Property("str"): String()}},
        {AllOf("str", default="default"): {Property("str"): String()}},
    ],
    ids=["Property", "OneOf", "AllOf"]
)
@pytest.mark.parametrize(
    "json",
    [
        {"str": "string"},
        {"no-str": "string"},
    ],
    ids=["arg_present", "arg_missing"]
)
def test_key_default(properties, json):
    """Test argument `default` for keys `Property`, `OneOf`, and `AllOf`."""
    output = Object(
        properties=properties
    ).assemble().run(json=json)

    assert output.last_status == Responses().GOOD.status
    if "str" in json:
        assert output.data.value == json
    else:
        assert output.data.value["str"] == "default"


@pytest.mark.parametrize(
    "properties",
    [
        {
            Property(
                "str", default=lambda default_string, **kwargs: default_string
            ): String()
        },
        {
            OneOf(
                "str", default=lambda default_string, **kwargs: default_string
            ): {Property("str"): String()}
        },
        {
            AllOf(
                "str", default=lambda default_string, **kwargs: default_string
            ): {Property("str"): String()}
        },
    ],
    ids=["Property", "OneOf", "AllOf"]
)
@pytest.mark.parametrize(
    "json",
    [
        {"str": "string"},
        {"no-str": "string"},
    ],
    ids=["arg_present", "arg_missing"]
)
def test_key_default_callable(properties, json):
    """
    Test argument `default` with callable for keys `Property`, `OneOf`,
    and `AllOf`.
    """
    output = Object(
        properties=properties
    ).assemble().run(json=json, default_string="more-text")

    assert output.last_status == Responses().GOOD.status
    if "str" in json:
        assert output.data.value == json
    else:
        assert output.data.value["str"] == "more-text"


@pytest.mark.parametrize(
    ("json", "status"),
    [
        ({"str": "string"}, Responses().GOOD.status),
        ({"bool": True}, Responses().GOOD.status),
        ({"bool": 0.1}, Responses().BAD_TYPE.status),
        ({"str": "string", "bool": True}, Responses().MULTIPLE_ONEOF.status),
    ]
)
def test_one_of_validation_only(json, status):
    """Test argument `validation_only` for key `OneOf`."""
    output = Object(
        properties={
            OneOf("str|bool", required=True, validation_only=True): {
                Property("str"): String(),
                Property("bool"): Boolean()
            }
        }
    ).assemble().run(json=json)

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value == {}
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        ({"str": "string"}, Responses().MISSING_REQUIRED_ALLOF.status),
        ({"bool": True}, Responses().MISSING_REQUIRED_ALLOF.status),
        ({"str": "string", "bool": 0.1}, Responses().BAD_TYPE.status),
        ({"str": "string", "bool": True}, Responses().GOOD.status),
    ]
)
def test_all_of_simple(json, status):
    """Basic test for key `AllOf`."""
    output = Object(
        properties={
            AllOf("str&bool", required=True): {
                Property("str"): String(),
                Property("bool"): Boolean()
            }
        }
    ).assemble().run(json=json)

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        ({"str": "string"}, Responses().MISSING_REQUIRED_ALLOF.status),
        ({"bool": True}, Responses().MISSING_REQUIRED_ALLOF.status),
        ({"str": "string", "bool": True}, Responses().GOOD.status),
        ({"str": "string", "bool": 0.1}, Responses().BAD_TYPE.status),
    ]
)
def test_all_of_validation_only(json, status):
    """Test argument `validation_only` for key `AllOf`."""
    output = Object(
        properties={
            AllOf("str&bool", required=True, validation_only=True): {
                Property("str"): String(),
                Property("bool"): Boolean()
            }
        }
    ).assemble().run(json=json)

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value == {}
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        ({"str": "string"}, Responses().MISSING_REQUIRED_ONEOF.status),
        ({"bool2": True}, Responses().GOOD.status),
        ({"str": "string", "bool": True}, Responses().GOOD.status),
        ({"str": "string", "bool": True, "bool2": True}, Responses().MULTIPLE_ONEOF.status),
    ]
)
def test_one_of_all_of_simple(json, status):
    """Basic test for interaction of keys `OneOf` and `AllOf`."""
    output = Object(
        properties={
            OneOf("str&bool|bool2", required=True): {
                AllOf("str&bool"): {
                    Property("str"): String(),
                    Property("bool"): Boolean()
                },
                Property("bool2"): Boolean()
            }
        }
    ).assemble().run(json=json)

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        ({"str": "string"}, Responses().MISSING_REQUIRED_ALLOF.status),
        ({"bool": True}, Responses().MISSING_REQUIRED_ALLOF.status),
        ({"bool2": True}, Responses().MISSING_REQUIRED_ALLOF.status),
        ({"str": "string", "bool": True}, Responses().MISSING_REQUIRED_ALLOF.status),
        ({"str": "string", "bool2": True}, Responses().GOOD.status),
        ({"bool": True, "bool2": True}, Responses().GOOD.status),
        ({"str": "string", "bool": True, "bool2": True}, Responses().MISSING_REQUIRED_ALLOF.status),
    ]
)
def test_all_of_one_of_simple(json, status):
    """Basic test for interaction of keys `OneOf` and `AllOf`."""
    output = Object(
        properties={
            AllOf("(str|bool)&bool2", required=True): {
                OneOf("str|bool", exclusive=True): {
                    Property("str"): String(),
                    Property("bool"): Boolean()
                },
                Property("bool2"): Boolean()
            }
        }
    ).assemble().run(json=json)

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        ({"str2": "string2", "str3": "string3", "bool": True}, Responses().GOOD.status),
        ({"str": "string", "bool": True}, Responses().GOOD.status),
        ({"str": "string", "str2": "string2", "str3": "string3", "bool": True}, Responses().MISSING_REQUIRED_ALLOF.status),
        ({"str2": "string2", "str3": "string3", "str4": "string4", "bool": True}, Responses().MISSING_REQUIRED_ALLOF.status),
        ({"str2": "string2", "str4": "string4"}, Responses().MISSING_REQUIRED_ALLOF.status),
        ({"str2": "string2", "str4": False, "bool": True}, Responses().MISSING_REQUIRED_ALLOF.status),
    ]
)
def test_all_of_one_of_complex(json, status):
    """Complex test for interaction of keys `OneOf` and `AllOf`."""
    output = Object(
        properties={
            AllOf("outer", required=True): {
                OneOf("str|inner", exclusive=True): {
                    Property("str"): String(),
                    AllOf("inner"): {
                        Property("str2"): String(),
                        OneOf("inner2"): {
                            Property("str3"): String(),
                            Property("str4"): String()
                        }
                    }
                },
                Property("bool"): Boolean()
            }
        }
    ).assemble().run(json=json)

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        ({"str": "string", "bool": True}, Responses().GOOD.status),
        ({"obj": {}, "bool": True}, Responses().MISSING_REQUIRED_ALLOF.status),
        ({"obj": {"str2": "string2"}, "bool": True}, Responses().MISSING_REQUIRED_ALLOF.status),
        ({"obj": {"str2": "string2", "str3": "string3", "str4": "string4"}, "bool": True}, Responses().MISSING_REQUIRED_ALLOF.status),
        ({"obj": {"str2": "string2", "str3": "string3"}, "bool": True}, Responses().GOOD.status),
        ({"obj": {"str2": "string2", "str4": "string4"}, "bool": True}, Responses().GOOD.status),
    ]
)
def test_all_of_one_of_complex_objects(json, status):
    """
    Complex test for interaction of keys `OneOf` and `AllOf` and
    `Object`.
    """
    output = Object(
        properties={
            AllOf("outer", required=True): {
                OneOf("str|obj", exclusive=True): {
                    Property("str"): String(),
                    Property("obj"): Object(
                        properties={
                            Property("str2", required=True): String(),
                            OneOf("inner2", required=True): {
                                Property("str3"): String(),
                                Property("str4"): String()
                            }
                        }
                    )
                },
                Property("bool"): Boolean()
            }
        }
    ).assemble().run(json=json)

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        ({"str": True}, Responses().BAD_TYPE.status),
        ({"str2": True}, Responses().BAD_TYPE.status),
        ({"str3": True}, Responses().BAD_TYPE.status),
        ({"str4": True}, Responses().BAD_TYPE.status),
        ({"str5": "string"}, Responses().GOOD.status),
    ]
)
def test_key_types_in_free_form_object(json, status):
    """Test occurrence of different key-types in free-form `Object`."""
    output = Object(
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
        free_form=True
    ).assemble().run(json=json)

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value == json
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        ({"str": True}, Responses().BAD_TYPE.status),
        ({"str2": True}, Responses().BAD_TYPE.status),
        ({"str3": True}, Responses().BAD_TYPE.status),
        ({"str4": True}, Responses().BAD_TYPE.status),
        ({"str5": "string"}, Responses().GOOD.status),
    ]
)
def test_key_types_object_w_additional_properties(json, status):
    """
    Test occurrence of different key-types in `Object` with
    `additional_properties`.
    """
    output = Object(
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
        additional_properties=True
    ).assemble().run(json=json)

    assert output.last_status == status
    if status == Responses().GOOD.status:
        print(output.data.value)
    else:
        print(output.last_message)


@pytest.mark.parametrize(
    ("json", "status"),
    [
        ({"str": True}, Responses().BAD_TYPE.status),
        ({"str2": True}, Responses().BAD_TYPE.status),
        ({"str3": True}, Responses().BAD_TYPE.status),
        ({"str4": True}, Responses().BAD_TYPE.status),
        ({"str5": "string"}, Responses().BAD_TYPE.status),
        ({"bool": True}, Responses().GOOD.status),
    ]
)
def test_key_types_object_w_additional_properties_dptype(json, status):
    """
    Test occurrence of different key-types in `Object` with
    `additional_properties`.
    """
    output = Object(
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
        additional_properties=Boolean()
    ).assemble().run(json=json)

    assert output.last_status == status
    if status == Responses().GOOD.status:
        assert output.data.value == json
    else:
        print(output.last_message)
