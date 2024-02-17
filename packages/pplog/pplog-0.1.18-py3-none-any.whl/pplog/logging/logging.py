""" Main logging module """


import logging
import sys
from typing import Any, Dict, List, Optional


#  pylint:disable=line-too-long
#  Adapted from UAPC-TPL
def setup_logging(config: Dict[str, Any], logging_handlers: Optional[List[logging.Handler]] = None):
    """Set basic logging configuration.
    Configuration of the root logger (existing handlers attached to the root logger are removed and closed) to log
    any message to stdout.
    Configuration of the "project" logger with or without (depending on the logging_conf) SplunkHandler which sends
    custom logs to Splunk. Since project logger is a child of root logger all messages send via that logger are also
    send to stdout.
    Python logging module organizes loggers in a hierarchy. All loggers are descendants of the root logger.
    Each logger passes log messages on to its parent. Which means if you create module level loggers using the
    logging.getLogger("__name__") approach they are configured to send logs (depending on the logging_conf) to Splunk.
    Args:
        config: project configuration as python dictionary
            E.g.: ```
            logging {
                level = INFO
                splunk {
                    event_grid_topic_endpoint = https://...azure.net/api/events
                }
            }
            ```
        handlers: logging Handler instances
    Returns:
        LOGGER, the logger of that module
    """
    logging_conf = config["logging"]
    # one-shot configuration of root logger
    # log basically everything to stdout
    logging.basicConfig(
        level=logging_conf["level"],
        stream=sys.stdout,
        format="%(asctime)s - %(name)s - [%(levelname)s] - [%(filename)s:%(lineno)d] [%(funcName)s] - %(message)s",
    )
    # configure project logger
    # since it's a child of the root logger, everything that
    # is logged via the project logger is also put to stdout

    if logging_handlers:
        for handler in logging_handlers:
            logging.getLogger().addHandler(handler)

    # raise log-level for py4j/spark logger
    spark_logger = logging.getLogger("py4j.java_gateway")
    spark_logger.setLevel(logging.ERROR)

    spark_logger = logging.getLogger("azure.core")
    spark_logger.setLevel(logging.ERROR)

    project_logger_name = __name__.rsplit(".", maxsplit=1)[
        0
    ]  # assuming __name__ is used for module level logger names
    project_logger = logging.getLogger(project_logger_name)
    project_logger.info("Logging initialized!")
