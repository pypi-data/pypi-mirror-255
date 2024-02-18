""" Hooks fastapi module - houses FastAPI hooks."""
import time
import traceback
from typing import Optional

from pplog.factory import get_class
from pplog.integrations import http
from pplog.log_checks.check_model import LogCheckResult
from pplog.unhandled_exception import log_unhandled_exception


async def async_check_fast_api_http_request(
    key: str, request: http.Request, call_next
) -> http.Response:
    """Async hook for fast api http request middleware."""
    start_time = time.time()
    # Process request and handle exceptions
    try:
        response = await call_next(request)
    except Exception as excp:
        message = str(excp)
        formatted_excp = traceback.format_exception(excp)
        log_unhandled_exception(key, message, " ".join(formatted_excp))
        raise excp

    # If we got here, we managed to finish process it without a 500
    # Log HTTP response as usual
    elapsed_time_in_ms = time.time() - start_time * 1000
    check_fast_api_http_request(
        key=key, request=request, response=response, elapsed_time_in_ms=elapsed_time_in_ms
    )
    return response


def check_fast_api_http_request(
    key: str, request: http.Request, response: http.Response, elapsed_time_in_ms: float
) -> Optional[LogCheckResult]:
    """Main logic for fast api request middleware.

    The core logic is implemented in sync function
    to make testing easier and not require additional hacking
    of the asyncio event loop.
    """
    check_class, check_class_arguments = get_class(key)
    if check_class_arguments.get("method", "").lower() != str(request.method).lower():
        return None

    if check_class_arguments.get("url_pattern", "") not in str(request.url):
        return None

    checker = check_class(key, request, response, elapsed_time_in_ms, check_class_arguments)
    log_result: LogCheckResult = checker.run_check()

    return log_result
