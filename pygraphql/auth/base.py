import logging
import os

import httpx


class BaseAuth(httpx.Auth):
    def __init__(self, token=None):
        self._token = token or os.getenv("GRAPHQL_AUTH_TOKEN")
        assert isinstance(self._token, str)
        self._logger = logging.getLogger(__name__)
        self._logger.debug(f"Success {self.__class__.__name__} setup")

    def auth_flow(self, request):
        request.headers["Authorization"] = f"bearer {self._token}"
        yield request
