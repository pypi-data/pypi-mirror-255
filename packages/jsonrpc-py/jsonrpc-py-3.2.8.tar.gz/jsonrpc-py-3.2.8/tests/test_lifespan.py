from __future__ import annotations

from asyncio import Queue
from typing import TYPE_CHECKING
from unittest import IsolatedAsyncioTestCase as AsyncioTestCase, TestCase
from unittest.mock import AsyncMock, MagicMock

from jsonrpc import ASGIHandler, LifespanEvents

if TYPE_CHECKING:
    from typing import Any, NoReturn


class TestLifespanEvents(TestCase):
    def setUp(self) -> None:
        self.events: LifespanEvents = LifespanEvents()

    def test_on_startup(self) -> None:
        @self.events.on_startup
        def startup_callback() -> None:
            return None

        self.assertTrue(self.events.startup_events)
        self.assertIn(startup_callback, self.events.startup_events)

        del startup_callback
        self.assertFalse(self.events.startup_events)

    def test_on_shutdown(self) -> None:
        @self.events.on_shutdown
        def shutdown_callback() -> None:
            return None

        self.assertTrue(self.events.shutdown_events)
        self.assertIn(shutdown_callback, self.events.shutdown_events)

        del shutdown_callback
        self.assertFalse(self.events.startup_events)


class TestLifespanManager(AsyncioTestCase):
    def setUp(self) -> None:
        self.app: ASGIHandler = ASGIHandler()
        self.receive_channel: Queue[dict[str, Any]] = Queue()
        self.send_channel: Queue[dict[str, Any]] = Queue()

    async def test_lifespan_startup_complete(self) -> None:
        sync_mock, async_mock = MagicMock(), AsyncMock()

        @self.app.events.on_startup
        def sync_startup_callback(*args: Any, **kwargs: Any) -> Any:
            return sync_mock(*args, **kwargs)

        @self.app.events.on_startup
        async def async_startup_callback(*args: Any, **kwargs: Any) -> Any:
            return await async_mock(*args, **kwargs)

        self.assertTrue(self.app.events.startup_events)
        self.assertIn(sync_startup_callback, self.app.events.startup_events)
        self.assertIn(async_startup_callback, self.app.events.startup_events)

        self.receive_channel.put_nowait({"type": "lifespan.startup"})
        await self.app({"type": "lifespan"}, self.receive_channel.get, self.send_channel.put)

        result: dict[str, Any] = await self.send_channel.get()
        self.assertDictEqual(result, {"type": "lifespan.startup.complete"})
        sync_mock.assert_called_once_with()
        async_mock.assert_awaited_once_with()

    async def test_lifespan_startup_failed(self) -> None:
        @self.app.events.on_startup
        async def startup_callback() -> NoReturn:
            raise Exception("for testing purposes")

        self.assertTrue(self.app.events.startup_events)
        self.assertIn(startup_callback, self.app.events.startup_events)

        with self.assertRaises(Exception) as context:
            self.receive_channel.put_nowait({"type": "lifespan.startup"})
            await self.app({"type": "lifespan"}, self.receive_channel.get, self.send_channel.put)

        match await self.send_channel.get():
            case {"type": "lifespan.startup.failed", **kwargs}:  # noqa: F841
                self.assertEqual(str(context.exception), "for testing purposes")
            case _ as event:
                self.fail(f"Unexpected {event=}")

    async def test_lifespan_shutdown_complete(self) -> None:
        sync_mock, async_mock = MagicMock(), AsyncMock()

        @self.app.events.on_shutdown
        def sync_shutdown_callback(*args: Any, **kwargs: Any) -> Any:
            return sync_mock(*args, **kwargs)

        @self.app.events.on_shutdown
        async def async_shutdown_callback(*args: Any, **kwargs: Any) -> Any:
            return await async_mock(*args, **kwargs)

        self.assertTrue(self.app.events.shutdown_events)
        self.assertIn(sync_shutdown_callback, self.app.events.shutdown_events)
        self.assertIn(async_shutdown_callback, self.app.events.shutdown_events)

        self.receive_channel.put_nowait({"type": "lifespan.shutdown"})
        await self.app({"type": "lifespan"}, self.receive_channel.get, self.send_channel.put)

        result: dict[str, Any] = await self.send_channel.get()
        self.assertDictEqual(result, {"type": "lifespan.shutdown.complete"})
        sync_mock.assert_called_once_with()
        async_mock.assert_awaited_once_with()

    async def test_lifespan_shutdown_failed(self) -> None:
        @self.app.events.on_shutdown
        async def shutdown_callback() -> NoReturn:
            raise Exception("for testing purposes")

        self.assertTrue(self.app.events.shutdown_events)
        self.assertIn(shutdown_callback, self.app.events.shutdown_events)

        with self.assertRaises(Exception) as context:
            self.receive_channel.put_nowait({"type": "lifespan.shutdown"})
            await self.app({"type": "lifespan"}, self.receive_channel.get, self.send_channel.put)

        match await self.send_channel.get():
            case {"type": "lifespan.shutdown.failed", **kwargs}:  # noqa: F841
                self.assertEqual(str(context.exception), "for testing purposes")
            case _ as event:
                self.fail(f"Unexpected {event=}")
