"""Module for handling logic of estimating the DBU usage."""
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import pplog.errors
from pplog.dbricks import SimpleWorkspaceClient, get_cluster_info
from pplog.dbricks.model import ClusterEvent, ClusterInfo

logger = logging.getLogger(__name__)


@dataclass
class AutoscalingTimeSlice:
    """Converts Autoscaling Events from Databricks into Timeslices.
    This aims at simplifying the DBU calculation down the line
    when autoscaling is involved.
    """

    start_timestamp: int
    end_timestamp: Optional[int]
    num_workers: int
    elapsed_time_in_hours: Optional[float] = None

    @classmethod
    def from_autoscaling_events(
        cls,
        cluster_events: List[ClusterEvent],
        end_time: datetime,
    ) -> List["AutoscalingTimeSlice"]:
        """Converts a list of ClusterEvent into AutoscalingTimeSlice.

        This method takes care of reversing the cluster events, because
        it is assumed they were queried in DESCENDING order. Thus, it's important
        that the query is not changed to ASCENDING order without modifying this code.
        """
        i = 0
        time_slices = []
        reversed_events = list(reversed(cluster_events))
        for i, left in enumerate(reversed_events):
            left = reversed_events[i]

            time_slice_kwargs = {
                "start_timestamp": left.timestamp,
                "num_workers": left.details.current_num_workers,
            }

            try:
                time_slice_kwargs["end_timestamp"] = reversed_events[i + 1].timestamp
            except IndexError:
                time_slice_kwargs["end_timestamp"] = end_time

            elapsed_time_in_milliseconds = (
                time_slice_kwargs["end_timestamp"] - time_slice_kwargs["start_timestamp"]
            )

            elapsed_time_in_seconds = elapsed_time_in_milliseconds / 1000
            elapsed_time_in_minutes = elapsed_time_in_seconds / 60
            time_slice_kwargs["elapsed_time_in_hours"] = elapsed_time_in_minutes / 60

            time_slice = AutoscalingTimeSlice(**time_slice_kwargs)
            time_slices.append(time_slice)

        return time_slices

    @classmethod
    def compute_dbu(
        cls,
        time_slices: List["AutoscalingTimeSlice"],
        cluster_info: ClusterInfo,
    ):
        """Computes DBU using AutoscalingTimeSlices and ClusterInfo.

        The logic is quite simple. For each time slice, use the ClusterInfo
        to check how much each DBUs the driver + workers consume per hour.

        Then multiply by the slice's duration in hours.

        Finally, we should add all slices DBUs together into the final result.
        """
        total_dbus = 0.0
        for time_slice in time_slices:
            slice_dbu = 0.0
            slice_dbu += cluster_info.driver_type.dbu
            slice_dbu += time_slice.num_workers * cluster_info.worker_type.dbu
            slice_dbu *= time_slice.elapsed_time_in_hours
            total_dbus += slice_dbu

        return total_dbus


def estimate_dbu_usage(
    cluster_id: str,
    workspace_client: SimpleWorkspaceClient,
    job_start_timestamp: int,
    approx_job_end_timestamp: int,
) -> float:
    """Calculates DBU usage."""
    # This exception check should probably be moved one module to the top,
    # once we have the final hook
    if job_start_timestamp > approx_job_end_timestamp:
        raise pplog.errors.FailedToEstimateDBU(
            f"Start time '{job_start_timestamp}' "
            "is greater than end time '{approx_job_end_timestamp}'"
        )

    cluster_info = get_cluster_info(cluster_id, workspace_client)

    total_dbus = 0.0

    total_elapsed_time_in_milliseconds = approx_job_end_timestamp - job_start_timestamp

    if not cluster_info.auto_scale:
        # Events are retrieved in descending order, e.g., first element in array
        # is the most recent event.

        # This is done to avoid taking stale events by mistake, as there is pagination.
        # Typically should not happen, anyway, as a new cluster is created in each job.

        # In any case, accesing the last element returns the first event.
        first_event = cluster_info.events[-1]
        if first_event.type.value != "RUNNING":
            raise pplog.errors.FailedToEstimateDBU(
                "Received inconsistent cluster events. "
                f"First event is not of type RUNNING: {first_event}"
            )

        cluster_dbus = 0.0
        cluster_dbus += cluster_info.driver_type.dbu
        cluster_dbus += first_event.details.current_num_workers * cluster_info.worker_type.dbu
        elapsed_in_seconds = total_elapsed_time_in_milliseconds / 1000
        elapsed_in_minutes = elapsed_in_seconds / 60
        elapsed_hours = elapsed_in_minutes / 60

        total_dbus = cluster_dbus * elapsed_hours

    else:
        time_slices = AutoscalingTimeSlice.from_autoscaling_events(
            cluster_events=cluster_info.events, end_time=approx_job_end_timestamp
        )
        total_dbus = AutoscalingTimeSlice.compute_dbu(time_slices, cluster_info)

    return total_dbus
