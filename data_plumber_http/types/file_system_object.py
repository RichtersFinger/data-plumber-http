from typing import Any, Optional, Callable
from pathlib import Path

from . import _DPType, Responses


class FileSystemObject(_DPType):
    """
    A `FileSystemObject` corresponds to a `pathlib.Path` that is given
    either absolute or relative to the cwd. The output is a
    `pathlib.Path`-object.

    Keyword arguments:
    relative_to -- make call to `pathlib.Path.relative_to` before
                   validation; if input is not given relative to this
                   path, `make` returns a `BAD_VALUE`-status
                   (default `None`)
    cwd -- override the process's cwd; the input is appended to this
           `Path` before validation
           (default `None`)
    Validation steps (leave as `None` to skip test):
    exists -- if `True`, check for `pathlib.Path.exists` during
              validation
              (default `None`)
    is_file -- if `True`, check for `pathlib.Path.is_file` during
               validation
               (default `None`)
    is_dir -- if `True`, check for `pathlib.Path.is_dir` during
              validation
              (default `None`)
    is_fifo -- if `True`, check for `pathlib.Path.is_fifo` during
               validation
               (default `None`)
    """
    TYPE = str

    def __init__(
        self,
        cwd: Optional[Path] = None,
        relative_to: Optional[Path] = None,
        exists: Optional[bool] = None,
        is_file: Optional[bool] = None,
        is_dir: Optional[bool] = None,
        is_fifo: Optional[bool] = None,
    ):
        self._relative_to = relative_to
        self._cwd = cwd
        self._validation_map = {
            "exists": exists,
            "is_file": is_file,
            "is_dir": is_dir,
            "is_fifo": is_fifo
        }

    def make(self, json, loc: str) -> tuple[Any, str, int]:
        path = Path(json)
        if self._relative_to is not None:
            try:
                path = path.relative_to(self._relative_to)
            except ValueError as exc_info:
                return (
                    None,
                    Responses.BAD_VALUE.msg.format(
                        json,
                        loc,
                        f"path relative to '{self._relative_to}' ({exc_info})"
                    ),
                    Responses.BAD_VALUE.status
                )
        if self._cwd is not None:
            path = self._cwd / path
        for step, req in self._validation_map.items():
            if req is None:
                continue
            if getattr(path, step)() != req:
                if req:
                    return (
                        None,
                        Responses.RESOURCE_NOT_FOUND.msg.format(json, loc),
                        Responses.RESOURCE_NOT_FOUND.status
                    )
                return (
                    None,
                    Responses.CONFLICT.msg.format(json, loc),
                    Responses.CONFLICT.status
                )
        return (
            path,
            Responses.GOOD.msg,
            Responses.GOOD.status
        )
