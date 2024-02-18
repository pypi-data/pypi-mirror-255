from __future__ import annotations

import re
from collections import UserList
from collections.abc import MutableMapping, MutableSequence
from dataclasses import dataclass
from numbers import Number
from typing import TYPE_CHECKING

from .errors import Error, ErrorEnum
from .utilities import Undefined, UndefinedType, make_hashable

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Any, Self

__all__: tuple[str, ...] = (
    "BatchRequest",
    "Request",
)

#: ---
#: Method names that begin with the word rpc followed by a
#: period character (U+002E or ASCII 46) are reserved for
#: rpc-internal methods and extensions and MUST NOT be used
#: for anything else.
INTERNAL_METHOD_REGEX: re.Pattern[str] = re.compile(r"^rpc\.", flags=re.IGNORECASE)


@dataclass(kw_only=True, slots=True)
class Request:
    """
    Base JSON-RPC request object.
    """

    #: The :py:class:`str` object containing the name of the method.
    method: str
    #: The object of type :py:class:`list` or :py:class:`dict` that holds the parameter values
    #: to be used during the invocation of the method.
    #: May be omitted if provided method has no parameters for example.
    params: list[Any] | dict[str, Any] | UndefinedType = Undefined
    #: The :py:class:`str` object or any type of :py:class:`numbers.Number` object which represents an identifier
    #: of the request instance. May be omitted. If its value omitted, the request assumed to be a notification.
    request_id: str | float | UndefinedType = Undefined

    def __post_init__(self) -> None:
        self._validate_method()
        self._validate_params()
        self._validate_request_id()

    def __hash__(self) -> int:
        return hash((self.__class__, self.method, make_hashable(self.params), self.request_id))

    def _validate_method(self) -> None:
        if not isinstance(self.method, str) or INTERNAL_METHOD_REGEX.match(self.method):
            raise Error(
                code=ErrorEnum.INVALID_REQUEST,
                message="Request method must be a string and should not have a 'rpc.' prefix",
            )

    def _validate_params(self) -> None:
        if not isinstance(self.params, MutableSequence | MutableMapping | UndefinedType):
            raise Error(
                code=ErrorEnum.INVALID_REQUEST,
                message=f"Request params must be a sequence or mapping, not a {type(self.params).__name__!r}",
            )

    def _validate_request_id(self) -> None:
        if not isinstance(self.request_id, str | Number | UndefinedType):
            raise Error(
                code=ErrorEnum.INVALID_REQUEST,
                message=f"Request id must be an optional string or number, not a {type(self.request_id).__name__!r}",
            )

    @property
    def args(self) -> tuple[Any, ...]:
        """
        Returns the :py:class:`tuple` object containing positional arguments of the method.
        """
        return tuple(params) if isinstance(params := self.params, MutableSequence) else ()

    @property
    def kwargs(self) -> dict[str, Any]:
        """
        Returns the :py:class:`dict` object containing keyword arguments of the method.
        """
        return dict(params) if isinstance(params := self.params, MutableMapping) else {}

    @property
    def is_notification(self) -> bool:
        """
        Returns :py:data:`True` if the identifier of the request is omitted, :py:data:`False` elsewise.
        """
        return isinstance(self.request_id, UndefinedType)

    @classmethod
    def from_json(cls, obj: dict[str, Any], /) -> Self | Error:
        """
        The class method for creating the :class:`jsonrpc.Request` object from :py:class:`dict` object.
        Unlike the :class:`jsonrpc.Request` constructor, doesn't raises any exceptions by validations,
        it returns the :class:`jsonrpc.Error` as is.

        Example usage::

            >>> Request.from_json({"jsonrpc": "2.0", "method": "foobar", "id": 1})
            Request(method="foobar", params=Undefined, request_id=1)
            >>> Request.from_json({"not_jsonrpc": True})
            Error(code=-32600, message="Invalid request object", data={"not_jsonrpc": True})
        """
        try:
            match obj:
                case {"jsonrpc": "2.0", "method": method, "params": params, "id": request_id}:
                    return cls(method=method, params=params, request_id=request_id)
                case {"jsonrpc": "2.0", "method": method, "params": params}:
                    return cls(method=method, params=params)
                case {"jsonrpc": "2.0", "method": method, "id": request_id}:
                    return cls(method=method, request_id=request_id)
                case {"jsonrpc": "2.0", "method": method}:
                    return cls(method=method)
                case _:
                    raise Error(code=ErrorEnum.INVALID_REQUEST, message="Invalid request object", data=obj)
        except Error as error:
            return error


class BatchRequest(UserList[Request | Error]):
    """
    The :py:class:`collections.UserList` subclass representing the collection
    of :class:`jsonrpc.Request` and :class:`jsonrpc.Error` objects.
    """

    __slots__: tuple[str, ...] = ()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.data!r})"

    def __hash__(self) -> int:
        return hash((self.__class__, tuple(self.data)))

    @classmethod
    def from_json(cls, iterable: Iterable[dict[str, Any]], /) -> Self:
        """
        The class method for creating the :class:`jsonrpc.BatchRequest` object from :py:class:`collections.abc.Iterable`
        of :py:class:`dict` objects.
        Similar to :func:`jsonrpc.Request.from_json` function it doesn't raises any exceptions.

        Example usage::

            >>> BatchRequest.from_json([
            ...     {"jsonrpc": "2.0", "method": "foobar", "id": 1},
            ...     {"not_jsonrpc": True}
            ... ])
            BatchRequest([Request(\u2026), Error(\u2026)])
        """
        return cls(map(Request.from_json, iterable))
