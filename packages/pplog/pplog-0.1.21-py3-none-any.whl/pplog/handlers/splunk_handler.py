"""Module to provide Azure Event Grid handlers for internal logging facility."""

import json
import logging
from typing import Any, Dict, Optional

from azure.eventgrid import EventGridEvent, EventGridPublisherClient
from logstash_formatter import LogstashFormatterV1

#  pylint: disable-next=E0611, E0401


class SplunkHandler(logging.Handler):
    """Class to instantiate the Azure Event Grid logging facility."""

    def __init__(
        self,
        event_grid_publisher_client: EventGridPublisherClient,
        event_type: str,
        custom_properties: Optional[Dict[str, Any]] = None,
    ):
        """Initialize an instance of the splunk handler.

        Args:
            event_grid_publisher_client: The EventGridPublisherClient instance.
                See `create_event_grid_publisher_client`
            custom_properties: A dictionary of key value pairs that will be part of every log
        """
        super().__init__()
        self.event_type = event_type
        #  same formatter is used in uap_core/logging, used here
        #  to have same logging format for splunk
        if custom_properties is not None:
            self.formatter = LogstashFormatterV1(
                json_cls=json.JSONEncoder,
                fmt=json.dumps({"extra": custom_properties}),
            )
        else:
            self.formatter = LogstashFormatterV1(json_cls=json.JSONEncoder)

        self.client = event_grid_publisher_client

    def emit(self, record: logging.LogRecord) -> None:
        """Emit the provided record to the event grid publisher client.

        Args:
            record: A logging.LogRecord.

        Returns:
            None
        """
        # drop azure event grid publisher client logs to avoid infinite recursion
        # only required if the handler is also configured on the root logger
        if "azure." in record.name:
            return

        # pylint: disable=broad-except
        try:
            record_json = self.formatter.format(record)  # type: ignore
            event = EventGridEvent(
                data_version="1.0",
                subject="Log-Message",
                event_type=self.event_type,
                #  formatter returns a str but we want the whole event
                #  to be json so that splunk can index it correctly
                data=json.loads(record_json),
            )
            self.client.send(event)
        except Exception:  # NOSONAR
            self.handleError(record)

    def close(self) -> None:
        """Close the event grid publisher client and clean up.

        Returns:
            None
        """
        self.acquire()
        try:
            if self.client:
                self.client.close()
            super().close()
        finally:
            self.release()
