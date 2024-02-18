"""Databricks Job Hook"""

import logging

from pplog import errors

# pylint: disable=unused-argument, logging-fstring-interpolation
from pplog.factory import get_class

logger = logging.getLogger(__name__)


def log_check_databricks_job_metrics(key, dbutils):
    """Simple Hook to check job metrics (duration, DBU usage)"""
    try:
        check_class, check_class_arguments = get_class(key)
        check_class_arguments["dbutils"] = dbutils
        try:
            check_class(key, check_class_arguments).run_check()
        except errors.ClusterEventsNotSupported:
            logger.warning(
                "This Databricks runtime does not support DBU tracking. Job metric check skipped."
            )
    except KeyError:
        logger.warning(f"Job {key} is NOT tracked by pplog. Please check if that is expected")
