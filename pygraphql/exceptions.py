from traceback import format_exception
import typing


class RetryError(Exception):
    """Custom exception thrown when retry logic fails"""

    def __init__(
        self, retries_count: int, last_exception: typing.Optional[Exception]
    ) -> None:
        """update the Exception message to take into account the rety logic"""
        message = "Failed {} retries: {}".format(retries_count, last_exception)
        super().__init__(message)
        self.last_exception = last_exception


class InvalidQueryType(Exception):
    pass


class MissingParameter(Exception):
    pass


class IntenalServerError(Exception):
    pass
