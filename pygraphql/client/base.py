import logging
import os
from typing import Any

import httpx

from pygraphql.auth.base import BaseAuth
from pygraphql.client.utils import (
    ExecutionResult,
    RandomExponentialSleep,
    RetryError,
    sleep,
)


class BaseClientAsync(httpx.AsyncClient):
    """Base async client to connect to a graphql endpoint
    based on httpx.AsyncClient, this class takes all the kwargs
    of AsyncClient in addition to `endpoint` where we define the endpoint.

    example:
        >>> token = "xxx"
        >>> query_str = "..."
        >>> endpoint = https://api.github.com/graphql
        >>> auth = BaseAuth(token=token)
        >>> async with BaseClientAsync(endpoint=endpoint, auth=auth) as client:
            result = await client.execute(
                query_str,
                {"var": "variables"},
            )
    """

    def __init__(self, **kwargs: Any):
        """initialise the client, uses exactly same kwargs as httpx.AsyncClient"""
        self._endpoint = kwargs.pop("endpoint", os.getenv("GRAPHQL_ENDPOINT"))
        self._backend = kwargs.pop("backend", None)  # just for test purposes
        assert isinstance(self._endpoint, str)

        # handle timeout
        self.default_timeout = (
            5.0  # https://www.python-httpx.org/advanced/#timeout-configuration
        )

        if "auth" not in kwargs:
            kwargs["auth"] = BaseAuth()

        super().__init__(**kwargs)
        self._logger = logging.getLogger(__name__)

    async def execute(
        self,
        query: str,
        variables: dict,
        max_tries: int = 5,
        random_exponential_sleep_multiplier: float = 1,
        random_exponential_sleep_max_sleep: float = 300,
        random_exponential_sleep_exp_base: float = 2,
        random_exponential_sleep_min_sleep: float = 0,
        exc_info: bool = False,
    ) -> ExecutionResult:
        """Function to execute  graphql query asynchronously

        Args:
            query: a query in str format or as a DocumentNode
            variables: variables dict containing variables of the query,
                or empty if no variables
            max_tries (optional): max number of retries in case of errors.
                        Defaults to 5.
            random_exponential_sleep_multiplier (optional): Defaults to 1
            random_exponential_sleep_max_sleep (optional):Defaults to 300
            random_exponential_sleep_exp_base (optional): Defaults to 2.
            random_exponential_sleep_min_sleep (optional): Defaults to 0.
            exc_info (optional): wether to log exec info in case of exception.
                    Defaults to False.

        Raises:
            RetryError: if there is still an error after retrying

        Returns:
            ExecutionResult: result of the query
        """

        retries_count = 0

        assert isinstance(query, str)

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
                payload = {"query": query, "variables": variables}
                kwargs: Any = {}
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
                last_exception = error  # type: ignore
                old_timeout = timeout if timeout else self.default_timeout
                timeout = old_timeout * 1.5
                self._logger.warning(
                    "Execution failed with a 'ReadTimeoutError', Retrying for the {} \
                     time with a new timeout of {:0.2f}s (last_old={:0.2f}s)".format(
                        retries_count, timeout, old_timeout
                    )
                )
            except httpx.WriteTimeout as error:
                retries_count += 1
                last_exception = error  # type: ignore
                old_timeout = timeout if timeout else self.default_timeout
                timeout = old_timeout * 1.5
                self._logger.warning(
                    "Execution failed with a 'WriteTimeoutError', Retrying for the {} time \
                    with a new timeout of {:0.2f}s (last_old={:0.2f}s)".format(
                        retries_count, timeout, old_timeout
                    )
                )
            except Exception as error:  # pylint: disable=broad-except
                retries_count += 1
                sleep_time = sleeper(retries_count)
                last_exception = error  # type: ignore

                self._logger.warning(
                    "Execution failed with exception '{}'. Retrying for the {} time \
                    after {:0.2f} seconds...".format(
                        error, retries_count, sleep_time
                    ),
                    exc_info=exc_info,
                )
                await sleep(sleep_time, backend=self._backend)

        raise RetryError(retries_count, last_exception)
