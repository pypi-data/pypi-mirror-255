"""This module define some formatters for different sinkers.
Fow now, it's only available for Splunk.

Note that this is not
to be confused with the logging handlers. The handler handles
where the log message is sent to.

Here, in the formatters package, we define how the message is
structured.

This is also not to be confused with the Python's standard lib
LoggingFormatter. This executes before the logging formatter
from the is executed.
"""
# pylint: disable=too-few-public-methods, no-self-use
from abc import ABC, abstractmethod

from pplog.log_checks.check_model import LogCheckResult


class IAdapter(ABC):
    """Abstract base interface."""

    @abstractmethod
    def format(self, log_check_result) -> dict:
        """Abstract format method."""
        raise NotImplementedError


class SplunkFormatter:
    """Formats log message into the format we expect to use
    with Splunk.

    It's important to note that this format is further changed
    by the handler, since it puts the result from this 'format'
    inside a dictionary using the 'data' key.
    """

    def format(self, log_check_result: LogCheckResult) -> dict:
        """Transforms a LogCheckResult into a dictionary."""
        return {
            "payload_type": log_check_result.payload_type,
            "create_incident": log_check_result.create_incident,
            "log_check_name": log_check_result.log_check_name,
            "metric_name": log_check_result.metric.name,
            "metric_value": log_check_result.metric.value,
            "target": log_check_result.target,
            "operator_name": log_check_result.operator.name,
            "operator": log_check_result.operator.function,
            "check": "OK" if log_check_result.check else "Failed",
        }
