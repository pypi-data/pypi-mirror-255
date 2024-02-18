"""Defines a custom exception decorator."""
from typing import Callable


def exception_decorator(exception, message):
    """Helper decorator for try excep clauses"""

    def exception_wrapper(func: Callable):
        """Helper wrapper for try/except clauses"""

        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception:
                raise exception(message) from exception

        return wrapper

    return exception_wrapper
