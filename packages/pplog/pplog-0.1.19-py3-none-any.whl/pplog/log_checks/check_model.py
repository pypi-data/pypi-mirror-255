"""Standard Model that implements specification of Log Check. This is used to bridge
between different implementations of check logic/engines to different engines."""
from dataclasses import dataclass
from typing import Union

# pylint: disable=too-many-instance-attributes


@dataclass
class Metric:
    """A logged metric."""

    name: str
    value: Union[float, str]


@dataclass
class OperatorModel:
    """Transforming the Operator into a structured definition of strings."""

    name: str
    function: str

    @classmethod
    def from_string(cls, operator_name: str) -> "OperatorModel":
        """Converts string into object for serialization later on."""
        if operator_name == "LESSER_THAN":
            return OperatorModel(name="lesser_than", function="<")

        if operator_name == "GREATER_THAN":
            return OperatorModel(name="greater_than", function=">")

        if operator_name == "EQUAL":
            return OperatorModel(name="equal", function="==")

        raise TypeError(f"Unsupported operator: {operator_name}")

    @classmethod
    def from_great_expectations(cls, ge_type: str) -> "OperatorModel":
        """Converts great expectations type into operator model."""
        return OperatorModel(name="great-expectations", function=ge_type)


@dataclass
class LogCheckResult:
    """The result of a check."""

    payload_type: str
    create_incident: bool
    log_check_name: str
    metric: Metric
    target: Union[str, float]
    operator: OperatorModel
    check: bool
    early_stop: bool
