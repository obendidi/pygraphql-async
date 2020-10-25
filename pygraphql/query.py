from typing import Any, Dict

from pygraphql.client.base import BaseClientAsync
from pygraphql.client.utils import ExecutionResult


class Query:
    """Class object of instanciating a query to be used in multiple instances"""

    def __init__(self, query: str, **kwargs: Any):
        """initialise the Query object, takes a query string as input
            and either a client object or kwargs to create a BaseClientAsync

            examples:
                >>> get_data = Query("...query_str...", client=client)
                or:
                >>> get_data = Query("...query_str...", endpoint=endpoint)
                or:
                >>> get_data = Query("...query_str...", endpoint=endpoint, auth=auth)

            in both last examples, Query will use provided kwargs to create client that
            will execute the query each time it is called

            takes exactly the same kwargs as pygraphql.BaseClientAsync

        Args:
            query: the query string
        """
        self._client = kwargs.get("client")
        self._query = query
        self._kwargs = kwargs

    async def __call__(
        self,
        variables: Dict[str, Any],
        max_tries: int = 5,
        random_exponential_sleep_multiplier: float = 1,
        random_exponential_sleep_max_sleep: float = 300,
        random_exponential_sleep_exp_base: float = 2,
        random_exponential_sleep_min_sleep: float = 0,
        exc_info: bool = False,
    ) -> ExecutionResult:
        """call function of the Query object

        Args:
            variables: variales used for the query or empty dict
            max_tries (optional): max number of retries in case of errors.
                        Defaults to 5.
            random_exponential_sleep_multiplier (optional): Defaults to 1
            random_exponential_sleep_max_sleep (optional):Defaults to 300
            random_exponential_sleep_exp_base (optional): Defaults to 2.
            random_exponential_sleep_min_sleep (optional): Defaults to 0.
            exc_info (optional): wether to log exec info in case of exception.
                    Defaults to False.

        Returns:
            ExecutionResult: result of the query
        """
        exec_kwargs: Dict[str, Any] = {
            "max_tries": max_tries,
            "random_exponential_sleep_multiplier": random_exponential_sleep_multiplier,
            "random_exponential_sleep_max_sleep": random_exponential_sleep_max_sleep,
            "random_exponential_sleep_exp_base": random_exponential_sleep_exp_base,
            "random_exponential_sleep_min_sleep": random_exponential_sleep_min_sleep,
            "exc_info": exc_info,
        }
        if isinstance(self._client, BaseClientAsync):
            return await self._client.execute(
                self._query,
                variables,
                **exec_kwargs,
            )

        async with BaseClientAsync(**self._kwargs) as client:
            return await client.execute(self._query, variables, **exec_kwargs)


# class BigQuery:
#     """run a qurey in parrallel to get huge amount of data using trio.nursery?"""

#     def __init__(self, query: str, aggregation_path: str, **kwargs: Any):
#         _assert_import_trio(name=self.__class__.__name__)


# def _assert_import_trio(name: str = None) -> None:
#     try:
#         import trio  # pylint: disable=unused-import,import-outside-toplevel

#     except ImportError as import_error:
#         raise Exception(
#             f"""trio not found, to use '{name}' please install pygraphql with 'trio':
#                 $ pip install pygraphql[trio]
#                 or from source
#                 $ poery install -E trio
#             """
#         ) from import_error
