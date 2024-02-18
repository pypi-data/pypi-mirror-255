"""Hooks for DataFrame - houses 'log_this'"""
from typing import Any, Callable

from pplog.factory import get_class


def log_this(key: str, output_check: bool = True) -> Callable:
    """Wrapper function

    Args:
        key (str): ppconf identifier key
        output_check (bool - Optional - defaults to True): whether to log the result
            of the LogCheck on func's output
    """

    def decorator(func) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            check_class, check_class_arguments = get_class(key)
            # Call the original function
            result = func(*args, **kwargs)
            if output_check:
                check_class(key, result, check_class_arguments).run_check()
            return result

        return wrapper

    return decorator
