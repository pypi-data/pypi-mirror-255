""" PPLOG base path """

import logging as log
from typing import List, Optional

from pplog.config import get_ppconfig
from pplog.logging import setup_logging


def setup_pplog(handlers: Optional[List[log.Handler]] = None) -> None:
    """Initializes pplog

    Args:
        handlers:  (List[logging.Handler], optional) = List of logging handlers. Defaults to None.

    Raises:
        ValueError: If both or neither of (config_path, parsed_config) are supplied
    """

    setup_logging(get_ppconfig(), handlers)


__all__ = ["setup_pplog"]
