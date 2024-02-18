"""Time tracking module."""
import logging
import timeit
from datetime import datetime
from typing import Any, Callable, Tuple

logger = logging.getLogger(__name__)


def timeit_wrapper(func: Callable):
    """
    Wrapper function to measure the execution time of another function.

    Args:
    - func: The function to be measured.
    - *args: Positional arguments to be passed to the function.
    - **kwargs: Keyword arguments to be passed to the function.

    Returns:
    - The result of the wrapped function.

    Logs:
    - The execution time in seconds.

    Example usage:
        1.
        class K:
            @timeit_wrapper
            def func(self): ...

        if __name__ == '__main__':
            k = K()
            k.func()

        2.
        class K:
            def func(self): ...

        if __name__ == '__main__':
            k = K()
            k.func = timeit_wrapper(k.func)
            k.func()
    """

    def wrapper(*args: Any, **kwargs: Any):
        start_time = timeit.default_timer()
        result = func(*args, **kwargs)
        end_time = timeit.default_timer()
        execution_time = end_time - start_time
        #  pylint:disable-next=logging-fstring-interpolation
        logger.info(f"Execution time: {execution_time:.6f} seconds")
        return result

    return wrapper


def get_current_millisecond_timestamp():
    """Returns the current time in a milliseconds level timestamp"""
    return datetime.now().timestamp() * 1000


def get_time_from_ms_timestamp(timestamp: int) -> Tuple[int, ...]:
    """Returns hours, minutes, seconds from millisecond timestamp

    Args:
        timestamp (int): milliseconds level timestamp

    Returns:
        Tuple[int]: hours, minutes, seconds
    """
    timestamp_seconds = timestamp / 1000
    hours, remainder = divmod(timestamp_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return tuple(int(el) for el in [hours, minutes, seconds])
