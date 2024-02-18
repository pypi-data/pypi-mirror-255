"""Module for getting a splunk handler inside Databricks environment."""
# pylint: disable=no-name-in-module, import-error
from azure.eventgrid import EventGridPublisherClient
from pyspark.dbutils import DBUtils  # type: ignore

from pplog.azure import get_event_grid_published_client
from pplog.config import get_ppconfig
from pplog.handlers.splunk_handler import SplunkHandler
from pplog.logging import get_databricks_log_properties


def get_splunk_handler_databricks(dbutils: DBUtils, event_type) -> SplunkHandler:
    """Returns a SplunkHandler instance

    Args:
        dbutils (DBUtils): Databricks Utilities instance

    Returns:
        SplunkHandler: Splunk Handler Instance
    """
    prj_config = get_ppconfig()
    custom_properties: dict = get_databricks_log_properties(dbutils)
    event_grid_published_client: EventGridPublisherClient = get_event_grid_published_client(
        prj_config, dbutils
    )

    splunk_handler = SplunkHandler(event_grid_published_client, event_type, custom_properties)
    splunk_handler.set_name(name="uapc-splunk")
    return splunk_handler
