"""Hooks is the main public API exposed by pplog.

Each hook applies a check into a different type of input.
"""
from .boolean import log_check_boolean
from .databricks_job import log_check_databricks_job_metrics
from .dataframe import log_this
from .fastapi import (
    async_check_fast_api_http_request,
    check_fast_api_http_request,
    log_unhandled_exception,
)
from .float import log_check_float
