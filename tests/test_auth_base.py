import os

from pygraphql.auth import BaseAuth

import pytest


class Request:
    def __init__(self):
        self.headers = {}


def test_BaseAuth_simple():
    auth = BaseAuth(token="blabla")
    request = Request()
    request = next(auth.auth_flow(request))
    assert request.headers["Authorization"] == "bearer blabla"


def test_BaseAuth_env():
    os.environ["GRAPHQL_AUTH_TOKEN"] = "blibli"
    auth = BaseAuth()
    request = Request()
    request = next(auth.auth_flow(request))
    assert request.headers["Authorization"] == "bearer blibli"


def test_BaseAuth_assertion_error():
    del os.environ["GRAPHQL_AUTH_TOKEN"]
    with pytest.raises(AssertionError):
        BaseAuth()
