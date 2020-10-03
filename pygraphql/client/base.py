from typing import Union
import os
import logging

import httpx
from graphql.execution import ExecutionResult
from graphql.language.ast import DocumentNode
from graphql.language.printer import print_ast

from .utils import RandomExponentialSleep, sleep


class BaseClientAsync(httpx.AsyncClient):
    def __init__(self, **kwargs):
        self._endpoint = kwargs.pop("endpoint", os.getenv("GRAPHQL_ENDPOINT"))
        assert isinstance(self._endpoint, str)
        super().__init__(**kwargs)
        self._logger = logging.getLogger(__name__)

    async def execute(
        self,
        query: Union[str, DocumentNode],
        variables: dict,
        max_tries: int = 5,
        random_exponential_sleep_multiplier: float = 1,
        random_exponential_sleep_max_sleep: float = 300,
        random_exponential_sleep_exp_base: float = 2,
        random_exponential_sleep_min_sleep: float = 0,
        exec_info: bool = False,
    ) -> ExecutionResult:
        pass

        retries_count = 0

        # if gql query convert to str
        if isinstance(query, DocumentNode):
            query_str = print_ast(query)
        else:
            query_str = query

        assert isinstance(query_str, str)
        while retries_count < max_tries:
            try:
                payload = {"query": query_str, "variables": variables}
                kwargs = {}
                request = await self.post(self._endpoint, json=payload, **kwargs)
                request.raise_for_status()
                result = request.json()
                assert (
                    "errors" in result or "data" in result
                ), 'Received non-compatible response "{}"'.format(result)
                return ExecutionResult(
                    errors=result.get("errors"), data=result.get("data")
                )
            except httpx.exceptions.ReadTimeout:
                pass
            except httpx.exceptions.WriteTimeout:
                pass
            except Exception as error:
                pass
