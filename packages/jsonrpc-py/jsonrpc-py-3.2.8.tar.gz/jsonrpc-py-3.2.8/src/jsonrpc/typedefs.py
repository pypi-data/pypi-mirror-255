from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Protocol, TypedDict, TypeVar, Union

if TYPE_CHECKING:
    from collections.abc import Iterable, MutableMapping
    from typing import Literal, NotRequired, TypeAlias

__all__: tuple[str, ...] = (
    "AnyCallable",
    "ASGIReceiveCallable",
    "ASGIReceiveEvent",
    "ASGISendCallable",
    "ASGISendEvent",
    "ASGIVersions",
    "Func",
    "HTTPConnectionScope",
    "HTTPDisconnectEvent",
    "HTTPRequestEvent",
    "HTTPResponseBodyEvent",
    "HTTPResponseStartEvent",
    "LifespanScope",
    "LifespanShutdownCompleteEvent",
    "LifespanShutdownEvent",
    "LifespanShutdownFailedEvent",
    "LifespanStartupCompleteEvent",
    "LifespanStartupEvent",
    "LifespanStartupFailedEvent",
    "Scope",
)

AnyCallable: TypeAlias = Callable[..., Any]
Func = TypeVar("Func", bound=AnyCallable)


class ASGIVersions(TypedDict):
    spec_version: Literal["2.0", "2.1", "2.2", "2.3"]
    version: Literal["2.0", "3.0"]


class HTTPConnectionScope(TypedDict):
    type: Literal["http"]
    asgi: ASGIVersions
    http_version: Literal["1.0", "1.1", "2"]
    method: str
    scheme: NotRequired[str]
    path: str
    raw_path: NotRequired[bytes | None]
    query_string: bytes
    root_path: NotRequired[str]
    headers: Iterable[tuple[bytes, bytes]]
    client: NotRequired[tuple[str, int] | None]
    server: NotRequired[tuple[str, int | None] | None]
    state: NotRequired[MutableMapping[str, Any]]
    extensions: NotRequired[MutableMapping[str, MutableMapping[object, object]] | None]


class HTTPRequestEvent(TypedDict):
    type: Literal["http.request"]
    body: NotRequired[bytes]
    more_body: NotRequired[bool]


class HTTPResponseStartEvent(TypedDict):
    type: Literal["http.response.start"]
    status: int
    headers: Iterable[tuple[bytes, bytes]]
    trailers: NotRequired[bool]


class HTTPResponseBodyEvent(TypedDict):
    type: Literal["http.response.body"]
    body: NotRequired[bytes]
    more_body: NotRequired[bool]


class HTTPDisconnectEvent(TypedDict):
    type: Literal["http.disconnect"]


class LifespanScope(TypedDict):
    type: Literal["lifespan"]
    asgi: ASGIVersions
    state: NotRequired[MutableMapping[str, Any]]


class LifespanStartupEvent(TypedDict):
    type: Literal["lifespan.startup"]


class LifespanStartupCompleteEvent(TypedDict):
    type: Literal["lifespan.startup.complete"]


class LifespanStartupFailedEvent(TypedDict):
    type: Literal["lifespan.startup.failed"]
    message: NotRequired[str]


class LifespanShutdownEvent(TypedDict):
    type: Literal["lifespan.shutdown"]


class LifespanShutdownCompleteEvent(TypedDict):
    type: Literal["lifespan.shutdown.complete"]


class LifespanShutdownFailedEvent(TypedDict):
    type: Literal["lifespan.shutdown.failed"]
    message: NotRequired[str]


Scope: TypeAlias = Union[
    HTTPConnectionScope,
    LifespanScope,
]
ASGIReceiveEvent: TypeAlias = Union[
    HTTPRequestEvent,
    HTTPDisconnectEvent,
    LifespanStartupEvent,
    LifespanShutdownEvent,
]
ASGISendEvent: TypeAlias = Union[
    HTTPResponseStartEvent,
    HTTPResponseBodyEvent,
    HTTPDisconnectEvent,
    LifespanStartupCompleteEvent,
    LifespanStartupFailedEvent,
    LifespanShutdownCompleteEvent,
    LifespanShutdownFailedEvent,
]


class ASGIReceiveCallable(Protocol):
    async def __call__(self) -> ASGIReceiveEvent: ...


class ASGISendCallable(Protocol):
    async def __call__(self, event: ASGISendEvent, /) -> None: ...
