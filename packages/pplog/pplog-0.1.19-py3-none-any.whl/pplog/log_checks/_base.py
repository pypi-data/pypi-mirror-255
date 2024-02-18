"""Abstract Check Interfaces."""
import logging
from abc import abstractmethod
from typing import List

from pplog.errors import ShouldAbortException
from pplog.formatters import SplunkFormatter
from pplog.log_checks.check_model import LogCheckResult

logger = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods, no-self-use


class BaseCheck:
    """BaseCheck uses SplunkAdapter for formatting by default.

    This is for now the only supported format. If we would extend
    to have multiple formatters, we would need to figure out configure
    the project to switch between the different formatters.
    """

    def __init__(self) -> None:
        super().__init__()
        self.adapter = SplunkFormatter()

    def abort(self):
        """Raises ShouldAbortException when check failed."""
        raise ShouldAbortException


class SingleCheck(BaseCheck):
    """Abtract log checking class for single metric."""

    @abstractmethod
    def check(self) -> LogCheckResult:
        """Basic interface to be implemented."""
        raise NotImplementedError

    def run_check(self) -> LogCheckResult:
        """Public reused method. All inherited checks reuse this."""
        log_check_result = self.check()
        payload = self.adapter.format(log_check_result)
        logger.info(payload)
        if not log_check_result.check and log_check_result.early_stop:
            self.abort()
        return log_check_result


class IMultiCheck(BaseCheck):
    """Abtract log checking class for multiple metrics."""

    @abstractmethod
    def check(self) -> List[LogCheckResult]:
        """Basic interface to be implemented."""
        raise NotImplementedError

    def run_check(self) -> LogCheckResult:
        """Public reused method. All inherited checks reuse this."""
        log_check_results = self.check()

        # Log everything
        for log_check_result in log_check_results:
            payload = self.adapter.format(log_check_result)
            logger.info(payload)

        # If something fails, stop
        for log_check_result in log_check_results:
            if not log_check_result.check and log_check_result.early_stop:
                self.abort()

        return log_check_results
