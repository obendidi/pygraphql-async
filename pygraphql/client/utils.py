import asyncio
import random
from typing import Any, Dict, Iterable, List, Optional

try:
    import trio

    BACKEND = "trio"
except ImportError:
    BACKEND = "asyncio"


async def sleep(seconds: float, backend=None) -> None:
    """a sleep function that takes into account wether trio is installed or not

    Args:
        seconds: num seconds to sleep
        backend (optional): force backend to use asyncio even if trio is installed.
            Defaults to None.
    """
    if backend == "asyncio" or BACKEND == "asyncio":
        await asyncio.sleep(seconds)
    else:
        await trio.sleep(seconds)


class RetryError(Exception):
    """Custom exception thrown when retry logic fails"""

    def __init__(self, retries_count: int, last_exception: Optional[Exception]) -> None:
        """update the Exception message to take into account the rety logic"""
        message = "Failed {} retries: {}".format(retries_count, last_exception)
        super().__init__(message)
        self.last_exception = last_exception


class RandomExponentialSleep:
    """Random wait with exponentially widening window.
    An exponential backoff strategy used to mediate contention between multiple
    uncoordinated processes for a shared resource in distributed systems. This
    is the sense in which "exponential backoff" is meant in e.g. Ethernet
    networking, and corresponds to the "Full Jitter" algorithm described in
    this blog post:
    https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
    Each retry occurs at a random time in a geometrically expanding interval.
    It allows for a custom multiplier and an ability to restrict the upper
    limit of the random interval to some maximum value.
    Example::
        RandomExponentialSleep(multiplier=0.5,  # initial window 0.5s
                                max_sleep=60)          # max 60s timeout
    """

    def __init__(
        self,
        multiplier: float = 1,
        max_sleep: float = 300,
        exp_base: float = 2,
        min_sleep: float = 0,
    ):
        self.multiplier = multiplier
        self.min_sleep = min_sleep
        self.max_sleep = max_sleep
        self.exp_base = exp_base

    def __call__(self, retry_number: int):
        high = self._get_high(retry_number)
        return random.uniform(0, high)

    def _get_high(self, retry_number: int):
        try:
            exp = self.exp_base ** retry_number
            result = self.multiplier * exp
        except OverflowError:
            return self.max_sleep
        return max(max(0, self.min_sleep), min(result, self.max_sleep))


class ExecutionResult:
    """The result of GraphQL execution.
    - ``data`` is the result of a successful execution of the query.
    - ``errors`` is included when any errors occurred as a non-empty list.
    """

    __slots__ = "data", "errors"

    data: Optional[Dict[str, Any]]
    errors: Optional[List[Any]]

    def __init__(
        self,
        data: Optional[Dict[str, Any]] = None,
        errors: Optional[List[Any]] = None,
    ):
        self.data = data
        self.errors = errors

    def __repr__(self) -> str:
        name = self.__class__.__name__
        return f"{name}(data={self.data!r}, errors={self.errors!r})"

    def __iter__(self) -> Iterable[Any]:
        return iter((self.data, self.errors))

    @property
    def formatted(self) -> Dict[str, Any]:
        """Get execution result formatted according to the specification."""
        return dict(data=self.data, errors=self.errors)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, dict):
            return other == dict(data=self.data, errors=self.errors)

        if isinstance(other, tuple):
            return other == (self.data, self.errors)
        return (
            isinstance(other, self.__class__)
            and other.data == self.data
            and other.errors == self.errors
        )

    def __ne__(self, other: Any) -> bool:
        return not self == other
