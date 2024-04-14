
from typing import Callable
from functools import wraps

from flask import request, Response
from data_plumber import Pipeline

from data_plumber_http.types import Responses


def flask_args():
    return request.args


def flask_form():
    return request.form


def flask_files():
    return request.files


def flask_values():
    return request.values


def flask_json():
    return request.json


def flask_handler(handler: Pipeline, json: Callable[[], dict]):
    """
    Returns decorator for flask view-functions to validate and process
    request-data.

    Use as decorator for a flask view-function like
     >>> @app.route("/", methods=["GET"])
     ... @flask_handler(
     ...     handler=Object(...).assemble(),
     ...     json=flask_args
     ... )
     ... def main(
     ...     <kwargs from Object>
     ... ):
     ...     ...

    Keyword arguments:
    handler -- `Pipeline` to be called
    json -- callable that returns the input data as dictionary
    """

    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            output = handler.run(
                json=json()
            )
            if output.last_status != Responses.GOOD.status:
                return Response(
                    response=output.last_message,
                    status=output.last_status,
                    mimetype="text/plain"
                )
            return view(*args, **(kwargs | output.data.value))
        return wrapped
    return decorator
