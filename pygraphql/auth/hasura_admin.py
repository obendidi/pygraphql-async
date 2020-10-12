from .base import BaseAuth


class HasuraAdminAuth(BaseAuth):
    def auth_flow(self, request):
        # Send the request, with a custom `x-hasura-admin-Secret` header.
        request.headers["x-hasura-admin-Secret"] = self._token
        yield request
