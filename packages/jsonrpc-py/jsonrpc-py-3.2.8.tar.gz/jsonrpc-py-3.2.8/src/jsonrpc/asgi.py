from __future__ import annotations

import re
from asyncio import CancelledError
from collections import UserDict
from collections.abc import MutableSequence
from dataclasses import dataclass
from functools import singledispatchmethod
from http import HTTPMethod, HTTPStatus
from io import DEFAULT_BUFFER_SIZE, BytesIO
from typing import TYPE_CHECKING, Generic, TypeVar

from .dispatcher import AsyncDispatcher
from .errors import Error
from .lifespan import LifespanEvents, LifespanManager
from .requests import BatchRequest, Request
from .responses import BatchResponse, Response
from .serializers import JSONSerializer
from .utilities import BackgroundTask, CancellableGather

if TYPE_CHECKING:
    from collections.abc import Generator
    from typing import Any, ClassVar, TypeAlias

    from .typedefs import ASGIReceiveCallable, ASGISendCallable, HTTPConnectionScope, Scope

__all__: tuple[str, ...] = ("ASGIHandler",)

KT = TypeVar("KT")
VT = TypeVar("VT")

#: ---
#: Useful typing aliases.
AnyRequest: TypeAlias = Request | Error | BatchRequest
AnyResponse: TypeAlias = Response | BatchResponse | None

#: ---
#: Ensure that "Content-Type" is a valid JSON header.
JSON_CTYPE_REGEXB: re.Pattern[bytes] = re.compile(
    rb"(?:application/|[\w.-]+/[\w.+-]+?\+)json$",
    flags=re.IGNORECASE,
)


class ASGIHandler(UserDict[KT, VT], Generic[KT, VT]):
    """
    Base class representing the ``ASGI`` entry point.
    Its subclassing the :py:class:`collections.UserDict` object
    for providing the user-defined data storage.

    For example::

        >>> app = ASGIHandler()
        >>> app["my_private_key"] = "foobar"
        >>> app["my_private_key"]
        "foobar"
    """

    __slots__: tuple[str, ...] = ()

    #: The default content type of the responses.
    content_type: ClassVar[str] = "application/json"

    #: Class variable representing the :class:`jsonrpc.AsyncDispatcher` object
    #: used by this class for routing user-defined functions by default.
    dispatcher: ClassVar[AsyncDispatcher] = AsyncDispatcher()

    #: Class variable representing the :class:`jsonrpc.JSONSerializer` object
    #: used by this class for data serialization by default.
    serializer: ClassVar[JSONSerializer] = JSONSerializer()

    #: Class variable representing the :class:`jsonrpc.LifespanEvents` object
    #: used by this class for storing the user-defined functions that running
    #: when application is initiated and shutting down.
    events: ClassVar[LifespanEvents] = LifespanEvents()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.data!r})"

    async def __call__(self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
        match scope:
            case {"type": "http", **kwargs}:  # noqa: F841
                await HTTPHandler(scope, receive, send, self)  # type: ignore[arg-type]
            case {"type": "lifespan", **kwargs}:  # noqa: F841
                await LifespanManager(receive, send, self.events)
            case _:
                raise ValueError("Only ASGI/HTTP connections are allowed.")


class RequestAborted(Exception):
    """
    The request was closed before it was completed, or timed out.
    """


@dataclass(kw_only=True, slots=True)
class HTTPException(Exception):
    status: HTTPStatus


@dataclass(slots=True)
class HTTPHandler:
    scope: HTTPConnectionScope
    receive: ASGIReceiveCallable
    send: ASGISendCallable
    app: ASGIHandler[Any, Any]

    def __await__(self) -> Generator[Any, None, None]:
        #: ---
        #: Create a suitable iterator by calling __await__ on a coroutine.
        return self.__await_impl__().__await__()

    async def __await_impl__(self) -> None:
        try:
            #: ---
            #: Might be "405 Method Not Allowed" or "415 Unsupported Media Type".
            self.negotiate_content()

            #: ---
            #: Might be "400 Bad Request" or abort.
            try:
                payload: bytes = await self.read_request_body()
            except RequestAborted:
                return
            if not payload:
                raise HTTPException(status=HTTPStatus.BAD_REQUEST)

            #: ---
            #: Should be "200 OK" or "204 No Content".
            if not (payload := await self.parse_payload(payload)):
                await self.send_response(status=HTTPStatus.NO_CONTENT)
            else:
                await self.send_response(payload=payload)

        #: ---
        #: Should be sent as is.
        except HTTPException as exc:
            await self.send_response(status=exc.status)
        #: ---
        #: Must be "504 Gateway Timeout" only.
        except (TimeoutError, CancelledError):
            await self.send_response(status=HTTPStatus.GATEWAY_TIMEOUT)

    def negotiate_content(self) -> None:
        if self.scope["method"] != HTTPMethod.POST:
            raise HTTPException(status=HTTPStatus.METHOD_NOT_ALLOWED)
        for key, value in self.scope["headers"]:
            if key == b"content-type" and not JSON_CTYPE_REGEXB.match(value):
                raise HTTPException(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    async def read_request_body(self) -> bytes:
        with BytesIO() as raw_buffer:
            while True:
                match await self.receive():
                    case {"type": "http.request", **kwargs}:
                        raw_buffer.write(kwargs.get("body", b""))  # type: ignore[arg-type]
                        if not kwargs.get("more_body", False):
                            break
                    case {"type": "http.disconnect"}:
                        raise RequestAborted("Client was disconnected too early.")

            return raw_buffer.getvalue()

    async def send_response(
        self,
        *,
        status: HTTPStatus = HTTPStatus.OK,
        payload: bytes = b"",
        buffer_size: int = DEFAULT_BUFFER_SIZE,
    ) -> None:
        headers: list[tuple[bytes, bytes]] = [
            (b"content-type", self.app.content_type.encode("ascii")),
        ]
        if status == HTTPStatus.METHOD_NOT_ALLOWED:
            headers.append((b"allow", HTTPMethod.POST.encode("ascii")))
            headers.sort()
        #: ---
        #: Initial response message:
        await self.send({"type": "http.response.start", "status": status.value, "headers": headers})
        #: ---
        #: Yield chunks of response:
        with BytesIO(payload) as raw_buffer:
            try:
                while chunk := raw_buffer.read(buffer_size):
                    await self.send({"type": "http.response.body", "body": chunk, "more_body": True})
            finally:
                #: ---
                #: Final closing message:
                await self.send({"type": "http.response.body", "body": b"", "more_body": False})

    async def parse_payload(self, payload: bytes) -> bytes:
        def write_error(error: Error) -> bytes:
            response: Response = Response(error=error, response_id=None)
            return self.app.serializer.serialize(response.json)

        try:
            obj: Any = self.app.serializer.deserialize(payload)
        except Error as error:
            return write_error(error)

        is_batch_request: bool = isinstance(obj, MutableSequence) and len(obj) >= 1
        request: AnyRequest = (BatchRequest if is_batch_request else Request).from_json(obj)  # type: ignore[attr-defined]

        if not (response := await self.process_request(request)):
            return b""

        try:
            return self.app.serializer.serialize(response.json)
        except Error as error:
            return write_error(error)

    @singledispatchmethod
    async def process_request(self, obj: AnyRequest) -> AnyResponse:
        raise NotImplementedError(f"Unsupported type {type(obj).__name__!r}")

    @process_request.register
    async def _(self, obj: Error) -> Response:
        return Response(error=obj, response_id=None)

    @process_request.register
    async def _(self, obj: Request) -> Response | None:
        background_task: BackgroundTask[Any] = BackgroundTask.from_coroutine(
            self.app.dispatcher.dispatch(
                obj.method,
                *obj.args,
                **obj.kwargs,
            )
        )
        if obj.is_notification:
            return None
        try:
            result: Any = await background_task
            return Response(body=result, response_id=obj.request_id)
        except Error as error:
            return Response(error=error, response_id=obj.request_id)

    @process_request.register
    async def _(self, obj: BatchRequest) -> BatchResponse:
        responses: tuple[AnyResponse, ...] = await CancellableGather(map(self.process_request, obj))
        return BatchResponse([response for response in responses if isinstance(response, Response)])
