from __future__ import annotations

from asyncio import create_task, shield
from dataclasses import dataclass, field
from traceback import format_exc
from typing import TYPE_CHECKING
from weakref import WeakSet

from .utilities import CancellableGather, ensure_async

if TYPE_CHECKING:
    from asyncio import Task
    from collections.abc import Generator
    from typing import Any

    from .typedefs import AnyCallable, ASGIReceiveCallable, ASGISendCallable, Func

__all__: tuple[str, ...] = (
    "LifespanEvents",
    "LifespanManager",
)


@dataclass(slots=True)
class LifespanEvents:
    """
    Simple class for storing the user-defined functions that running
    when application is initiated and shutting down.
    """

    #: The :py:class:`weakref.WeakSet` collection of startup functions.
    startup_events: WeakSet[AnyCallable] = field(default_factory=WeakSet)

    #: The :py:class:`weakref.WeakSet` collection of shutdown functions.
    shutdown_events: WeakSet[AnyCallable] = field(default_factory=WeakSet)

    def on_startup(self, user_function: Func, /) -> Func:
        """
        Decorator for the adding a function which will be executed
        when application is initiated.

        Example usage::

            >>> @app.events.on_startup
            ... def startup_callback() -> None:
            ...     print("Some important message.")

        :param user_function: The :py:class:`collections.abc.Callable` object representing the user-defined function.
        :returns: The unmodified ``user_function`` object, passed in the parameters.
        """
        self.startup_events.add(user_function)
        return user_function

    def on_shutdown(self, user_function: Func, /) -> Func:
        """
        Decorator for the adding a function which will be executed
        when application is shutting down.

        Example usage::

            >>> @app.events.on_shutdown
            ... async def shutdown_callback() -> None:
            ...     await important_function()

        :param user_function: The :py:class:`collections.abc.Callable` object representing the user-defined function.
        :returns: The unmodified ``user_function`` object, passed in the parameters.
        """
        self.shutdown_events.add(user_function)
        return user_function


@dataclass(slots=True)
class LifespanManager:
    receive: ASGIReceiveCallable
    send: ASGISendCallable
    events: LifespanEvents

    def __await__(self) -> Generator[Any, None, None]:
        #: ---
        #: Create a suitable iterator by calling __await__ on a coroutine.
        return self.__await_impl__().__await__()

    async def __await_impl__(self) -> None:
        match await self.receive():
            case {"type": "lifespan.startup"}:
                startup_task: Task[None] = create_task(self.on_startup(self.events.startup_events))
                await shield(startup_task)
            case {"type": "lifespan.shutdown"}:
                shutdown_task: Task[None] = create_task(self.on_shutdown(self.events.shutdown_events))
                await shield(shutdown_task)

    async def on_startup(self, startup_events: WeakSet[AnyCallable], /) -> None:
        try:
            if startup_events:
                await CancellableGather(map(ensure_async, startup_events))
        except BaseException:
            await self.send({"type": "lifespan.startup.failed", "message": format_exc()})
            raise
        else:
            await self.send({"type": "lifespan.startup.complete"})

    async def on_shutdown(self, shutdown_events: WeakSet[AnyCallable], /) -> None:
        try:
            if shutdown_events:
                await CancellableGather(map(ensure_async, shutdown_events))
        except BaseException:
            await self.send({"type": "lifespan.shutdown.failed", "message": format_exc()})
            raise
        else:
            await self.send({"type": "lifespan.shutdown.complete"})
