from typing import Union
import os
import logging

import httpx
from graphql.execution import ExecutionResult
from graphql.language.ast import DocumentNode
from graphql.language.printer import print_ast

from .utils import RandomExponentialSleep, sleep, RetryError


class BaseClientAsync(httpx.AsyncClient):
    def __init__(self, **kwargs):
        self._endpoint = kwargs.pop("endpoint", os.getenv("GRAPHQL_ENDPOINT"))
        self._backend = kwargs.pop("backend", None)  # just for test purposes
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
        exc_info: bool = False,
    ) -> ExecutionResult:
        pass

        retries_count = 0

        # if gql query convert to str
        if isinstance(query, DocumentNode):
            query_str = print_ast(query)
        else:
            query_str = query

        assert isinstance(query_str, str)

        sleeper = RandomExponentialSleep(
            multiplier=random_exponential_sleep_multiplier,
            max_sleep=random_exponential_sleep_max_sleep,
            exp_base=random_exponential_sleep_exp_base,
            min_sleep=random_exponential_sleep_min_sleep,
        )
        timeout = None
        last_exception = None
        while retries_count < max_tries:
            try:
                payload = {"query": query_str, "variables": variables}
                kwargs = {}
                if timeout:
                    kwargs["timeout"] = timeout
                self._logger.debug("Start Exuction")
                request = await self.post(self._endpoint, json=payload, **kwargs)
                request.raise_for_status()
                result = request.json()
                assert (
                    "errors" in result or "data" in result
                ), 'Received non-compatible response "{}"'.format(result)
                self._logger.debug("Success Exuction")
                return ExecutionResult(
                    errors=result.get("errors"), data=result.get("data")
                )
            except httpx.ReadTimeout as error:
                retries_count += 1
                last_exception = error
                old_timeout = timeout if timeout else self.read_timeout
                timeout = old_timeout * 1.5
                self._logger.warning(
                    "Execution failed with a 'ReadTimeoutError', Retrying for the {} time \
                     with a new timeout of {:0.2f}s (last_old={:0.2f}s)".format(
                        retries_count, timeout, old_timeout
                    )
                )
            except httpx.WriteTimeout as error:
                retries_count += 1
                last_exception = error
                old_timeout = timeout if timeout else self.write_timeout
                timeout = old_timeout * 1.5
                self._logger.warning(
                    "Execution failed with a 'WriteTimeoutError', Retrying for the {} time \
                    with a new timeout of {:0.2f}s (last_old={:0.2f}s)".format(
                        retries_count, timeout, old_timeout
                    )
                )
            except Exception as error:
                retries_count += 1
                sleep_time = sleeper(retries_count)
                last_exception = error

                self._logger.warning(
                    "Execution failed with exception '{}'. Retrying for the {} time \
                    after {:0.2f} seconds...".format(
                        error, retries_count, sleep_time
                    ),
                    exc_info=exc_info,
                )
                await sleep(sleep_time, backend=self._backend)

        raise RetryError(retries_count, last_exception)
