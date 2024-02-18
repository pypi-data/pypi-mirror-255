"""Databricks Job Hook"""
# pylint: disable=unused-argument
from pplog.factory import get_class


def log_check_databricks_job_metrics(key, dbutils):
    """Simple Hook to check job metrics (duration, DBU usage)"""
    check_class, check_class_arguments = get_class(key)
    check_class_arguments["dbutils"] = dbutils
    check_class(key, check_class_arguments).run_check()
