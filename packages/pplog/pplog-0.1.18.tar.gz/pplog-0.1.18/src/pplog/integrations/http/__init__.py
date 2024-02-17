"""Defines the interface for HTTP hook. These are used instead of a real
library implementation, so we avoid putting too many dependencies in pplog.
"""
from dataclasses import dataclass


@dataclass
class Request:
    """Request interface for fastapi middleware"""

    url: str
    method: str


@dataclass
class Response:
    """Response interface for fastapi middleware"""

    status_code: str
