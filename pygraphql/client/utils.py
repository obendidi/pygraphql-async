import asyncio
import random
from typing import Optional

try:
    import trio

    BACKEND = "trio"
except ImportError:
    BACKEND = "asyncio"


async def sleep(seconds: float, backend=None) -> None:
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
