import os

import pytest

from pygraphql.auth import HasuraAdminAuth


class Request:
    def __init__(self):
        self.headers = {}


def test_HasuraAdminAuth_simple():
    auth = HasuraAdminAuth(secret="blabla")
    request = Request()
    request = next(auth.auth_flow(request))
    assert request.headers["x-hasura-admin-Secret"] == "blabla"


def test_HasuraAdminAuth_env():
    os.environ["HASURA_GRAPHQL_ADMIN_SECRET"] = "blibli"
    auth = HasuraAdminAuth()
    request = Request()
    request = next(auth.auth_flow(request))
    assert request.headers["x-hasura-admin-Secret"] == "blibli"


def test_HasuraAdminAuth_assertion_error():
    del os.environ["HASURA_GRAPHQL_ADMIN_SECRET"]
    with pytest.raises(AssertionError):
        auth = HasuraAdminAuth()
