import os

import httpx


class HasuraAdminAuth(httpx.Auth):
    def __init__(self, secret=None):
        self._secret = secret or os.getenv("HASURA_GRAPHQL_ADMIN_SECRET")
        assert isinstance(self._secret, str)

    def auth_flow(self, request):
        # Send the request, with a custom `x-hasura-admin-Secret` header.
        request.headers["x-hasura-admin-Secret"] = self._secret
        yield request
