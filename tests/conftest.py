"""Common pytest fixtures."""

from data_plumber_http.settings import Responses


def pytest_sessionstart(session):
    Responses().warn_on_change = False
    for index, x in enumerate(Responses().INTERNAL_RESPONSES):  # pylint: disable=no-member
        if getattr(Responses(), x).status >= 400:
            Responses().update(x, status=400+index)
    Responses().warn_on_change = True
