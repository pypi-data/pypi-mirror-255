"""A module to expose great expectations in memory engine through a simple interface."""
from dataclasses import dataclass
from typing import List, Tuple

# pylint: disable=import-error
import great_expectations as gx
from great_expectations.core.expectation_configuration import ExpectationConfiguration
from great_expectations.core.expectation_suite import ExpectationSuite
from great_expectations.data_context.types.base import (
    DataContextConfig,
    InMemoryStoreBackendDefaults,
)


@dataclass
class SimpleExpectationResult:
    """The results of a single expectation check"""

    is_success: bool
    details: dict


@dataclass
class SimpleValidationResult:
    """The results of a expectation suite validation result."""

    suite_name: str
    is_suite_success: bool
    expectation_results: List[Tuple[bool, dict]]


def get_validation_results(checkpoint_result) -> SimpleValidationResult:
    """Converts a great expectations checkpoint_result into a simple list of Dataclass type"""
    results = []
    for key, item in checkpoint_result["run_results"].items():
        suite_name = str(key).rsplit("/", maxsplit=1)[-1]
        validation_result = item["validation_result"]
        is_suite_success = validation_result["success"]
        expectation_results = []
        for result in validation_result["results"]:
            details = result["result"].get("details", {})
            expectation_results.append(
                SimpleExpectationResult(is_success=result["success"], details=details)
            )
        results.append(SimpleValidationResult(suite_name, is_suite_success, expectation_results))
    if not results:
        raise TypeError("Could not retrieve validation results")

    if len(results) > 1:
        raise ValueError(
            "pplog does not support multiple expectation suites defined in the same checkpoint"
        )

    return results[0]


def get_in_memory_gx_context():
    """Initializes and returns a context configured with in-memory backend."""
    data_context_config = DataContextConfig(
        store_backend_defaults=InMemoryStoreBackendDefaults(),
    )
    context = gx.get_context(project_config=data_context_config)
    return context


def create_expectation_suite(expectation_configuration: ExpectationConfiguration):
    """Creates an expectation suite with a single expectation configuration.

    We don't need the suite abstraction for pplog at the moment, so we treat it
    as if it was the same as a single check.
    """
    suite = ExpectationSuite(expectation_suite_name="test_suite")
    suite.add_expectation(expectation_configuration)
    return suite


def create_checkpoint(context, suite, dataframe):
    """Creates a great expectations checkpoint using the DataFrame as input,
    and the in-memory engine previously configured for the context."""
    context.add_expectation_suite(expectation_suite=suite)

    dataframe_asset = context.sources.add_spark("test").add_dataframe_asset(
        name="test_asset", dataframe=dataframe
    )

    batch_request = dataframe_asset.build_batch_request()
    checkpoint = context.add_or_update_checkpoint(
        name="my_checkpoint",
        validations=[
            {
                "batch_request": batch_request,
                "expectation_suite_name": "test_suite",
            },
        ],
    )
    return checkpoint
