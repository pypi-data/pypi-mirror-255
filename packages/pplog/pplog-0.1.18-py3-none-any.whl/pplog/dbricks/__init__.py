"""Databricks SDK integration package.

Contains logic to retrieve current available node types, and check
whether our DBU table is up-to-date.
"""
import json
import logging
from typing import Dict, List, Tuple

# pylint: disable=import-error, too-many-instance-attributes
from databricks.sdk.service.compute import NodeType

from pplog import errors
from pplog.dbricks.cached_workspace_client import SimpleWorkspaceClient
from pplog.dbricks.dbu_table import dbu_table
from pplog.dbricks.model import ClusterInfo, WorkerType
from pplog.errors.decorator import exception_decorator
from pplog.time_tracking import (
    get_current_millisecond_timestamp,
    get_time_from_ms_timestamp,
)

logger = logging.getLogger(__name__)


def get_current_cluster_id(dbutils) -> str:
    """Retrieves current cluster ID using DBUtils."""
    ctx = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
    return ctx.tags().get("clusterId").value()


def get_job_trigger_time(dbutils) -> int:
    """Retrieves job Trigger Time using DBUtils."""
    ctx = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
    return ctx.tags().get("jobTriggerTime").value()


def check_missing_config(workspace_client: SimpleWorkspaceClient) -> int:
    """Checks whether our DBU table is up-to-date."""
    current_list = [node.node_type_id for node in workspace_client.get_current_list_of_node_types()]

    missing = []
    for node_type_id in current_list:
        if node_type_id not in dbu_table:
            missing.append(node_type_id)

    if len(missing) > 0:
        logger.warning(
            "Missing configuration for one or more node_types: '%s'", missing, extra={"pplog_init"}
        )
    return len(missing)


def filter_node_types_by_id(node_type_id: str, node_types: List[NodeType]) -> NodeType:
    """Filter node_types by a specific node_type_id."""
    filtered_node_types = [
        node_type for node_type in node_types if node_type.node_type_id == node_type_id
    ]
    if len(filtered_node_types) == 0:
        raise errors.FailedToGetClusterInfoException(f"Could not find node type id: {node_type_id}")

    if len(filtered_node_types) > 1:
        raise errors.FailedToGetClusterInfoException(
            f"Found multiple nodes with same id: {node_type_id}"
        )

    return filtered_node_types[0]


def get_cluster_info(cluster_id: str, workspace_client: SimpleWorkspaceClient) -> ClusterInfo:
    """Returns all the required information from a Cluster to estimate DBU usage."""
    cluster_details = workspace_client.get_cluster_details(cluster_id)
    node_types = workspace_client.get_current_list_of_node_types()

    driver_node_type = WorkerType.from_node_type(
        filter_node_types_by_id(cluster_details.driver_node_type_id, node_types)
    )

    worker_node_type = WorkerType.from_node_type(
        filter_node_types_by_id(cluster_details.node_type_id, node_types)
    )

    cluster_info_kwargs = {
        "num_workers": cluster_details.num_workers,
        "auto_scale": cluster_details.autoscale,
        "events": [],
        "total_cpu_cores": cluster_details.cluster_cores,
        "total_memory_in_mbs": cluster_details.cluster_memory_mb,
        "is_photon": cluster_details.runtime_engine.value == "PHOTON",
        "driver_type": driver_node_type,
        "worker_type": worker_node_type,
    }

    cluster_events = workspace_client.get_cluster_events(cluster_id)

    if len(cluster_events) == 0:
        raise errors.FailedToGetClusterInfoException(
            "Empty cluster events, cannot infer num workers."
        )

    cluster_info_kwargs["events"] = cluster_events
    return ClusterInfo(**cluster_info_kwargs)


@exception_decorator(KeyError, "Databricks may have changed their API")
def get_databricks_context(dbutils) -> Dict:
    """Returns dictionary with databricks context information

    Args:
        dbutils (DBUtils): Databricks Utilities class instance

    Returns:
        Dict: Databricks context dictionary
    """
    return json.loads(dbutils.notebook.entry_point.getDbutils().notebook().getContext().toJson())


@exception_decorator(KeyError, "Databricks may have changed their API")
def get_databricks_log_properties(dbutils) -> Dict:  # type: ignore
    """Get databricks log properties to setup logging with a unique job run identifier
    from databricks-notebook-context.
    If notebook submitted as databricks-job: `cluster-id.job-id.run-id`.
    If notebook submitted manually: `cluster-id.notebook-name.notebook-id`
    :param dbutils: Dbutils, databricks utilities class
    :return: dict, with databricks properties to uniquely identify job run
    """
    context = get_databricks_context(dbutils)
    cluster_id = context["tags"]["clusterId"]
    job_id = context["tags"].get("jobId") or context["extraContext"]["notebook_path"].split("/")[-1]
    run_id = context.get("currentRunId") or context["tags"]["notebookId"]
    job_start_time = int(context["tags"]["jobTriggerTime"])
    databricks_properties = {
        "job_id": f"{cluster_id}.{job_id}.{run_id}",
        "cluster_id": cluster_id,
        "job_start_time": job_start_time,
    }
    return databricks_properties


@exception_decorator(KeyError, "Databricks may have changed their API")
def get_current_databricks_job_duration(dbutils) -> Tuple[int, ...]:  # type: ignore
    """Returns the duration of the current databricks job in hours, minutes, seconds

    Args:
        dbutils (DBUtils): Databricks Utilities class instance

    Returns:
        Tuple[int]: hours, minutes, seconds
    """
    context = get_databricks_context(dbutils)
    job_start_time = int(context["tags"]["jobTriggerTime"])
    elapsed_time_ms = get_current_millisecond_timestamp() - job_start_time
    return get_time_from_ms_timestamp(elapsed_time_ms)


@exception_decorator(KeyError, "Databricks may have changed their API")
def log_current_databricks_job_duration(dbutils):
    """Logs the current duration of the current databricks job

    Args:
        dbutils (DBUtils): Databricks Utilities class instance

    Logs:
        Current Databricks job  duration

    Usage:
        Place it after the final step in your databricks dag to get the full job duration
    """
    hours, minutes, seconds = get_current_databricks_job_duration(dbutils)
    context = get_databricks_context(dbutils)
    job_name = context["tags"].get("jobName") or context["extraContext"]["notebook_id"]
    job_id = context["tags"].get("jobId") or context["extraContext"]["notebook_path"].split("/")[-1]
    logger.info(
        f"Job <{job_name}> with id <{job_id}> has taken {hours} hours,"
        + f" {minutes} minutes and {seconds} seconds to complete."
    )
