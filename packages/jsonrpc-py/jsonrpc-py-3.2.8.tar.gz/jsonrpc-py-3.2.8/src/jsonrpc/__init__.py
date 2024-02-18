"""
Pure zero-dependency JSON-RPC 2.0 implementation.
"""

from __future__ import annotations

from .asgi import ASGIHandler
from .dispatcher import AsyncDispatcher
from .errors import Error, ErrorEnum
from .lifespan import LifespanEvents
from .requests import BatchRequest, Request
from .responses import BatchResponse, Response
from .serializers import JSONSerializer

__all__: tuple[str, ...] = (
    "ASGIHandler",
    "AsyncDispatcher",
    "BatchRequest",
    "BatchResponse",
    "Error",
    "ErrorEnum",
    "JSONSerializer",
    "LifespanEvents",
    "Request",
    "Response",
)
