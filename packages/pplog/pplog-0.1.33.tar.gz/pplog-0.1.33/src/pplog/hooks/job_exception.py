"""Unhandled exception. When all else fails."""

import logging
import traceback

from pplog.unhandled_exception import log_unhandled_exception

logger = logging.getLogger(__name__)


def log_job_exception(excp, job_name: str):
    """Handles exception for a job execution."""
    message = str(excp)
    # Python 3.10 call
    try:
        formatted_excp = traceback.format_exception(excp)
    # Python 3.8 / Python3.9 call, old API
    except TypeError:
        formatted_excp = traceback.format_exception(type(excp), excp, None)[0]
    log_unhandled_exception(f"{job_name}Exception", message, " ".join(formatted_excp), job_name)
