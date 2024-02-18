"""Exceptions thrown by pplog."""


class FailedToGetClusterInfoException(Exception):
    """Could not get ClusterInfo for DBU Estimation."""


class FailedToEstimateDBU(Exception):
    """Failed to estimate DBU"""


class DatabricksEnvironmentNotAvailable(Exception):
    """Tried to access Databricks resources inside an environment
    that is not Databricks."""


class GreatExpectationsNotAvailable(Exception):
    """Tried to access GreatExpectations resources inside an environment
    that does not have the library installed."""


class ShouldAbortException(Exception):
    """A check returned 'Failed' and was configured to abort the pipeline."""
