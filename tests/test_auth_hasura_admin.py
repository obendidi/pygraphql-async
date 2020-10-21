import os

from pygraphql.auth import HasuraAdminAuth

import pytest


class Request:
    def __init__(self):
        self.headers = {}


def test_HasuraAdminAuth_simple():
    auth = HasuraAdminAuth(token="blabla")
    request = Request()
    request = next(auth.auth_flow(request))
    assert request.headers["x-hasura-admin-Secret"] == "blabla"


def test_HasuraAdminAuth_env():
    os.environ["GRAPHQL_AUTH_TOKEN"] = "blibli"
    auth = HasuraAdminAuth()
    request = Request()
    request = next(auth.auth_flow(request))
    assert request.headers["x-hasura-admin-Secret"] == "blibli"


def test_HasuraAdminAuth_assertion_error():
    del os.environ["GRAPHQL_AUTH_TOKEN"]
    with pytest.raises(AssertionError):
        HasuraAdminAuth()
