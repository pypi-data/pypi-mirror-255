"""Models to Map Databricks SDK into information we actually track."""
from dataclasses import dataclass
from typing import List

# pylint: disable=import-error, too-many-instance-attributes
from databricks.sdk.service.compute import AutoScale, ClusterEvent, NodeType

from pplog.dbricks.dbu_table import dbu_table


@dataclass
class WorkerType:
    """Wraps the relevant parts of the WorkerType."""

    name: str
    dbu: float
    memory_in_mbs: int
    cpu_cores: int

    @classmethod
    def from_node_type(cls, node_type: NodeType) -> "WorkerType":
        """Keep only the useful info about a NodeType and adds DBU count."""
        return WorkerType(
            node_type.node_type_id,
            dbu=dbu_table.get(node_type.node_type_id),
            memory_in_mbs=node_type.memory_mb,
            cpu_cores=node_type.num_cores,
        )


@dataclass
class ClusterInfo:
    """Wraps the relevant parts of a ClusterInfo for DBU estimation."""

    num_workers: int
    auto_scale: AutoScale
    events: List[ClusterEvent]
    driver_type: WorkerType
    worker_type: WorkerType
    is_photon: bool
    total_cpu_cores: int
    total_memory_in_mbs: int
