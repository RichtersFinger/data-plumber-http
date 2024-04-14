import sys

__all__ = []

if "flask" in sys.modules:
    from .flask_input import flask_handler, flask_args, flask_form, \
        flask_files, flask_values, flask_json

    __all__.extend(
        [
            "flask_handler", "flask_args", "flask_form", "flask_files",
            "flask_values", "flask_json"
        ]
    )
