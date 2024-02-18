"""

:author: Jonathan Decker
"""

import functools
import logging

from rich import print

logger = logging.getLogger("logger")


class IronikFatalError(Exception):
    """
    Exception for irrecoverable errors that should lead to program termination.
    """

    def __init__(self, message):
        self.message = "Ironik has stopped due to the following error: " + message
        super().__init__(self.message)
        logger.warning(self.message)


class IronikPassingError(Exception):
    """
    Exception for recoverable errors that should not lead to program termination.
    """

    def __init__(self, message):
        self.message = "The following error occurred has occurred, execution will continue: " + message
        super().__init__(self.message)
        logger.warning(self.message)


def passing_error_handler(func):
    """
    Decorator for functions that can throw an IronikPassingError such that the IronikPassingError is caught and printed.
    Args:
        func:

    Returns:

    """

    @functools.wraps(func)
    def inner_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IronikPassingError as exception:
            logger.debug(f"Passing error occurred in {func.__name__}")
            print(exception)
            return None

    return inner_function
