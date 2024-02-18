from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING

from .utilities import Undefined, UndefinedType, make_hashable

if TYPE_CHECKING:
    from typing import Any

__all__: tuple[str, ...] = (
    "Error",
    "ErrorEnum",
)


class ErrorEnum(IntEnum):
    """
    An enumeration of error codes that indicates the error type that occurred.
    """

    #: Error occurred due the serialization or deserialization.
    PARSE_ERROR: int = -32700
    #: Error occurred due the receiving an invalid :class:`jsonrpc.Request` object.
    INVALID_REQUEST: int = -32600
    #: Error occurred due the invoking a missing user-function.
    METHOD_NOT_FOUND: int = -32601
    #: Error occurred due the receiving an invalid user-function's arguments.
    INVALID_PARAMETERS: int = -32602
    #: Error occurred due the unexpected internal errors.
    INTERNAL_ERROR: int = -32603


@dataclass(kw_only=True, slots=True)
class Error(Exception):
    """
    Base class for all encountered errors in the JSON-RPC protocol.
    """

    #: The :py:class:`int` object that indicates the error type that occurred.
    code: int
    #: The :py:class:`str` object that contains a short description of the error.
    message: str
    #: An any type of object that contains additional information about the error.
    data: Any = Undefined

    def __hash__(self) -> int:
        return hash((self.__class__, self.code, self.message, make_hashable(self.data)))

    def __str__(self) -> str:
        return f"{self.message!s}\u0020\u0028{self.code:d}\u0029"

    @property
    def json(self) -> dict[str, Any]:
        """
        Returns the :py:class:`dict` object needed for the serialization.

        Example output::

            >>> error: Error = Error(
            ...     code=ErrorEnum.INTERNAL_ERROR,
            ...     message="Unexpected error",
            ...     data={"additional": "information"}
            ... )
            >>> error.json
            {"code": -32603, "message": "Unexpected error", "data": {"additional": "information"}}
        """
        obj: dict[str, Any] = {"code": self.code, "message": self.message}

        if not isinstance(data := self.data, UndefinedType):
            obj |= {"data": data}

        return obj
