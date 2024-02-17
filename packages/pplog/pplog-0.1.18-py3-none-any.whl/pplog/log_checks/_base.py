"""Abstract Check Interfaces."""
import logging
from abc import ABC, abstractmethod
from typing import List

from pplog.log_checks.check_model import LogCheckResult

logger = logging.getLogger(__name__)


class ICheck(ABC):
    """Abtract log checking class for single metric."""

    @abstractmethod
    def check(self) -> LogCheckResult:
        """Basic interface to be implemented."""
        raise NotImplementedError

    def log(self, result=None) -> None:
        """Logs payload from the check() function result"""
        if result is None:
            log_check_result = self.check()
        else:
            log_check_result = result

        payload = {
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
        logger.info(payload)


class IMultiCheck(ABC):
    """Abtract log checking class for multiple metrics."""

    @abstractmethod
    def check(self) -> List[LogCheckResult]:
        """Basic interface to be implemented."""
        raise NotImplementedError

    def log(self) -> None:
        """Logs payload from the check() function result"""
        for log_check_result in self.check():
            payload = {
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
            logger.info(payload)
