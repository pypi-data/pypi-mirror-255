"""Unhandled exception. When all else fails."""
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class UnhandledException:
    """The result of a check."""

    message: str
    exception: str


def log_unhandled_exception(
    identifier: str, message: str, formatted_traceback: str, job_name: Optional[str] = None
):
    """Logs an unhandled exception."""
    if job_name:
        logger.info(
            {
                "payload_type": "log_check",
                "log_check_name": f"{job_name}Success",
                "metric_name": "JobSuccess",
                "metric_value": False,
                "target": True,
                "operator_name": "equal",
                "operator": "==",
                "check": "Failed",
            }
        )

    logger.error(
        {
            "payload_type": "unhandled_exception",
            "log_check_name": identifier,
            "message": message,
            "traceback": formatted_traceback,
            "check": "Failed",
        }
    )
