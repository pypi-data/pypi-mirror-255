"""Hosts CachedWorkspaceClient"""
import functools
from typing import List

# pylint: disable=import-error
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.compute import ClusterDetails, ClusterEvent, NodeType


class SimpleWorkspaceClient:
    """Calls DatabricksSDK with lru cache.

    This makes sure no duplicate calls are done to the API.
    """

    def __init__(self, workspace_client):
        """Initializes the static caching wrapper with a workspace client."""
        self.workspace_client = workspace_client

    def get_current_list_of_node_types(self) -> List[NodeType]:
        """Retrieve up-to-date list of node types from Databricks.

        This is necessary for two reasons:
            - Retrieving additional info, such as memory/CPU of each worker type
            - Checking whether we have unmapped nodes in the hardcoded DBU table.
        """
        return self.workspace_client.clusters.list_node_types()

    def get_cluster_details(self, cluster_id: str) -> ClusterDetails:
        """Retrieves cluster details using Databricks SDK."""
        return self.workspace_client.clusters.get(cluster_id)

    def get_cluster_events(
        self, cluster_id: str, start_timestamp_in_milliseconds: int
    ) -> List[ClusterEvent]:
        """Get cluster events (specially useful for auto-scaling)."""
        return self.workspace_client.clusters.events(
            cluster_id,
            start_time=start_timestamp_in_milliseconds,
            event_types=["RUNNING", "RESIZING", "UPSIZE_COMPLETED"],
        )


@functools.lru_cache
def get_cached_workspace_client() -> SimpleWorkspaceClient:
    """Returns an initialized cached workspace client"""
    return SimpleWorkspaceClient(WorkspaceClient())
