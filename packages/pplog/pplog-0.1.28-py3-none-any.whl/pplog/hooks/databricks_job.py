"""Databricks Job Hook"""

import logging

# pylint: disable=unused-argument, logging-fstring-interpolation
from pplog.factory import get_class

logger = logging.getLogger(__name__)


def log_check_databricks_job_metrics(key, dbutils):
    """Simple Hook to check job metrics (duration, DBU usage)"""
    try:
        check_class, check_class_arguments = get_class(key)
        check_class_arguments["dbutils"] = dbutils
        check_class(key, check_class_arguments).run_check()
    except KeyError:
        logger.warning(f"Job {key} is NOT tracked by pplog. Please check if that is expected")
