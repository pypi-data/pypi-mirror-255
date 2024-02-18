""" LogEvent classes (Checks) """


import logging
from typing import List

from pyspark.sql import DataFrame as SparkDF

from pplog.config import Operator
from pplog.errors import DatabricksEnvironmentNotAvailable
from pplog.integrations import great_expectations as ge
from pplog.integrations import http
from pplog.log_checks._base import IMultiCheck, SingleCheck
from pplog.log_checks.check_model import LogCheckResult, Metric, OperatorModel
from pplog.time_tracking import get_current_millisecond_timestamp

try:
    from pplog.dbricks import get_databricks_log_properties
    from pplog.dbricks.cached_workspace_client import get_cached_workspace_client
    from pplog.dbu_estimation import estimate_dbu_usage

    IS_DATABRICKS_AVAILABLE = True
except ImportError:
    IS_DATABRICKS_AVAILABLE = False


#  pylint:disable=fixme,too-few-public-methods,too-many-function-args,too-many-instance-attributes,too-many-arguments

logger = logging.getLogger(__name__)


class CheckFloatValue(SingleCheck):
    """Spark DataFrame Count Checker"""

    def __init__(self, identifier: str, float_value: float, params: dict) -> None:
        super().__init__()
        self._identifier = identifier
        self._float_value = float_value
        self._params = params
        self._comparison_function_string = params["comparison_function"]
        self._comparison_function = getattr(Operator, self._comparison_function_string.upper())
        self._comparison_value = params["comparison_value"]
        self._create_incident = params.get("create_incident", True)
        self._early_stop = params.get("early_stop", True)

    def check(self) -> LogCheckResult:
        """Perform check and log result"""
        success = self._comparison_function(self._float_value, self._comparison_value)
        result = LogCheckResult(
            payload_type="log_check",
            create_incident=self._create_incident,
            log_check_name=self._identifier,
            metric=Metric(
                name="float_check",
                value=self._float_value,
            ),
            target=self._comparison_value,
            operator=OperatorModel.from_string(self._comparison_function_string.upper()),
            check=success,
            early_stop=self._early_stop,
        )
        return result


class CheckDataFrameCount(SingleCheck):
    """Spark DataFrame Count Checker"""

    def __init__(self, identifier: str, sdf: SparkDF, params: dict) -> None:
        super().__init__()
        self._identifier = identifier
        self._sdf = sdf
        self._params = params
        self._comparison_function_string = params["comparison_function"]
        self._comparison_function = getattr(Operator, self._comparison_function_string.upper())
        self._comparison_value = params["comparison_value"]
        self._create_incident = params.get("create_incident", True)
        self._early_stop = params.get("early_stop", True)
        self._sdf_count = sdf.count()

    def check(self) -> LogCheckResult:
        """Perform check and log result"""
        success = self._comparison_function(self._sdf_count, self._comparison_value)
        result = LogCheckResult(
            payload_type="log_check",
            create_incident=self._create_incident,
            log_check_name=self._identifier,
            metric=Metric(
                name="row_count",
                value=self._sdf_count,
            ),
            target=self._comparison_value,
            operator=OperatorModel.from_string(self._comparison_function_string.upper()),
            check=success,
            early_stop=self._early_stop,
        )
        return result


class GreatExpectationsSparkDFCheck(SingleCheck):
    """Checks a SparkDataFrame with great expectations library."""

    def __init__(self, identifier: str, sdf: SparkDF, params: dict) -> None:
        super().__init__()
        self._identifier = identifier
        self._sdf = sdf
        self._params = params
        self._expectation_type = params["expectation_type"]
        self._ge_kwargs = params["kwargs"]
        self._create_incident = params.get("create_incident", True)
        self._early_stop = params.get("early_stop", True)

        expectation_config = ge.ExpectationConfiguration(
            expectation_type=self._expectation_type,
            kwargs=self._ge_kwargs,
        )

        suite = ge.create_expectation_suite(expectation_config)
        self.checkpoint = ge.create_checkpoint(
            context=ge.get_in_memory_gx_context(), suite=suite, dataframe=sdf
        )

    def check(self) -> LogCheckResult:
        """Perform check and log result"""
        results = self.checkpoint.run()
        simple_results: ge.SimpleValidationResult = ge.get_validation_results(results)
        result = LogCheckResult(
            payload_type="log_check",
            create_incident=self._create_incident,
            log_check_name=self._identifier,
            metric=Metric(
                name=self._expectation_type,
                value="great-expectations-check",  # not sure what to put in here for GE
            ),
            target="great-expectation-check",
            operator=OperatorModel.from_great_expectations(self._expectation_type),
            check=simple_results.is_suite_success,
            early_stop=self._early_stop,
        )
        return result


class CheckHttpResponseCheck(SingleCheck):
    """Http Response Checker"""

    def __init__(
        self,
        identifier: str,
        request: http.Request,
        response: http.Response,
        elapsed_time_in_ms: float,
        params: dict,
    ) -> None:
        super().__init__()
        self._identifier = identifier
        self._request = request
        self._response = response
        self._params = params
        self._comparison_function_string = params["comparison_function"]
        self._comparison_attribute = params["comparison_attribute"]
        self._comparison_function = getattr(Operator, self._comparison_function_string.upper())
        self._comparison_value = params["comparison_value"]
        self._url_pattern = params["url_pattern"]
        self._create_incident = params.get("create_incident", True)
        self._early_stop = False

        # Special value to measure latency of request
        if self._comparison_attribute == "elapsed_time_in_ms":
            self._value = elapsed_time_in_ms
        else:
            self._value = getattr(self._response, self._comparison_attribute)

    def check(self) -> LogCheckResult:
        """Perform check and log result"""
        success = self._comparison_function(self._value, self._comparison_value)
        result = LogCheckResult(
            payload_type="log_check",
            create_incident=self._create_incident,
            log_check_name=self._identifier,
            metric=Metric(
                name="http_request_check",
                value=self._value,
            ),
            target=self._comparison_value,
            operator=OperatorModel.from_string(self._comparison_function_string.upper()),
            check=success,
            early_stop=self._early_stop,
        )
        return result


class JobDatabricksMetricsCheck(IMultiCheck):
    """Job Metrics Checks"""

    def __init__(self, identifier: str, params: dict) -> None:
        if not IS_DATABRICKS_AVAILABLE:
            raise DatabricksEnvironmentNotAvailable(f"Cannot use '{__class__.__name__}'")
        super().__init__()
        self._identifier = identifier
        self.dbutils = params["dbutils"]
        self.max_dbu = params.get("max_accumulated_dbu_usage", -1)
        self.max_duration = params.get("max_duration_time_in_minutes", -1)
        self._create_incident = params.get("create_incident", False)
        self._early_stop = False

    def check(self) -> List[LogCheckResult]:
        """Perform check and log result"""
        results = []

        dbu_usage = 0
        duration_time_in_minutes = 0

        approx_end_time_timestamp = int(get_current_millisecond_timestamp())
        context = get_databricks_log_properties(self.dbutils)
        cluster_id = context["cluster_id"]

        simple_workspace_client = get_cached_workspace_client()
        dbu_usage = estimate_dbu_usage(
            cluster_id,
            simple_workspace_client,
            context["job_start_time"],
            approx_end_time_timestamp,
        )
        duration_time_in_seconds = (approx_end_time_timestamp - context["job_start_time"]) / 1000
        duration_time_in_minutes = duration_time_in_seconds / 60

        duration_comparison_function = "GREATER_THAN" if self.max_duration == -1 else "LESSER_THAN"
        dbu_comparison_function = "GREATER_THAN" if self.max_dbu == -1 else "LESSER_THAN"

        duration_operator = getattr(Operator, duration_comparison_function)
        dbu_operator = getattr(Operator, dbu_comparison_function)

        dbu_success = dbu_operator(dbu_usage, self.max_dbu)
        duration_success = duration_operator(duration_time_in_minutes, self.max_duration)

        results.append(
            LogCheckResult(
                payload_type="log_check",
                create_incident=self._create_incident,
                log_check_name=f"{self._identifier}DurationTime",
                metric=Metric(
                    name="duration_time_in_minutes",
                    value=duration_time_in_minutes,
                ),
                target=self.max_duration,
                operator=OperatorModel.from_string(duration_comparison_function),
                check=duration_success,
                early_stop=self._early_stop,
            )
        )
        results.append(
            LogCheckResult(
                payload_type="log_check",
                create_incident=self._create_incident,
                log_check_name=f"{self._identifier}DBU",
                metric=Metric(
                    name="DBU",
                    value=dbu_usage,
                ),
                target=self.max_dbu,
                operator=OperatorModel.from_string(dbu_comparison_function),
                check=dbu_success,
                early_stop=self._early_stop,
            )
        )
        results.append(
            LogCheckResult(
                payload_type="log_check",
                create_incident=self._create_incident,
                log_check_name=f"{self._identifier}Success",
                metric=Metric(name="JobSuccess", value=True),
                target=True,
                operator=OperatorModel.from_string("EQUAL"),
                check=True,
                early_stop=self._early_stop,
            )
        )
        return results


class CheckBooleanValue(SingleCheck):
    """Boolean Checker"""

    def __init__(self, identifier: str, boolean_value: bool, params: dict) -> None:
        super().__init__()
        self._identifier = identifier
        self._boolean_value = boolean_value
        self._params = params
        self._comparison_function = getattr(Operator, "EQUAL")
        self._comparison_value = params["comparison_value"]
        self._create_incident = params.get("create_incident", True)
        self._early_stop = params.get("early_stop", True)

    def check(self) -> LogCheckResult:
        """Perform check and log result"""
        success = self._comparison_function(self._boolean_value, self._comparison_value)
        result = LogCheckResult(
            payload_type="log_check",
            create_incident=self._create_incident,
            log_check_name=self._identifier,
            metric=Metric(name="boolean_check", value=self._boolean_value),
            target=self._comparison_value,
            operator=OperatorModel.from_string("EQUAL"),
            check=success,
            early_stop=self._early_stop,
        )
        return result
