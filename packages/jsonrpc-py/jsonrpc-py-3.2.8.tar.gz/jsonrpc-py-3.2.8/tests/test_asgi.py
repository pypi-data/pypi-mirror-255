from __future__ import annotations

from asyncio import Event, Queue, get_running_loop, sleep, wait_for
from collections.abc import MutableMapping
from http import HTTPMethod, HTTPStatus
from typing import TYPE_CHECKING
from unittest import IsolatedAsyncioTestCase as AsyncioTestCase, TestCase
from unittest.mock import AsyncMock
from uuid import uuid4

from httpx import AsyncClient

from jsonrpc import ASGIHandler, ErrorEnum

if TYPE_CHECKING:
    from typing import Any, Literal
    from uuid import UUID

    from httpx import Response


class AnyNonEmptyString:
    __slots__: tuple[str, ...] = ("test_case",)

    def __init__(self, test_case: TestCase) -> None:
        self.test_case: TestCase = test_case

    def __eq__(self, string: str) -> Literal[True]:
        self.test_case.assertIsInstance(string, str)
        self.test_case.assertGreater(len(string), 0)
        return True


class TestASGIHandler(AsyncioTestCase):
    def setUp(self) -> None:
        self.app: ASGIHandler = ASGIHandler()
        self.receive_channel: AsyncMock = AsyncMock()
        self.send_channel: AsyncMock = AsyncMock()

    def test_inheritance(self) -> None:
        self.assertIsInstance(self.app, MutableMapping)

    async def test_supported_scopes(self) -> None:
        with self.assertRaises(ValueError) as context:
            await self.app({"type": "websocket"}, self.receive_channel, self.send_channel)

        self.assertEqual(str(context.exception), "Only ASGI/HTTP connections are allowed.")
        self.receive_channel.assert_not_called()
        self.send_channel.assert_not_called()


class TestHTTPHandler(AsyncioTestCase):
    @property
    def random_id(self) -> str:
        uuid: UUID = uuid4()
        return str(uuid)

    def setUp(self) -> None:
        self.app: ASGIHandler = ASGIHandler()
        self.client: AsyncClient = AsyncClient(
            app=self.app,
            base_url="http://testserver",
            headers={"Content-Type": "application/json"},
        )

    async def asyncSetUp(self) -> None:
        await self.enterAsyncContext(self.client)

    async def test_negotiate_content_405(self) -> None:
        for request in (
            self.client.build_request(HTTPMethod.HEAD, "/testHead"),
            self.client.build_request(HTTPMethod.GET, "/testGet"),
            self.client.build_request(HTTPMethod.PUT, "/testPut"),
            self.client.build_request(HTTPMethod.PATCH, "/testPatch"),
            self.client.build_request(HTTPMethod.DELETE, "/testDelete"),
            self.client.build_request(HTTPMethod.OPTIONS, "/testOptions"),
            self.client.build_request(HTTPMethod.TRACE, "/testTrace"),
        ):
            with self.subTest(request=request):
                response: Response = await self.client.send(request)
                self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)
                self.assertEqual(response.headers["Allow"], HTTPMethod.POST)
                self.assertEqual(response.content, b"")

    async def test_negotiate_content_415(self) -> None:
        for request in (
            self.client.build_request(HTTPMethod.POST, "/", headers={"Content-Type": "multipart/form-data"}),
            self.client.build_request(HTTPMethod.POST, "/", headers={"Content-Type": "text/plain"}),
        ):
            with self.subTest(request=request):
                response: Response = await self.client.send(request)
                self.assertEqual(response.status_code, HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
                self.assertEqual(response.content, b"")

    async def test_request_aborted(self) -> None:
        scope: dict[str, Any] = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "POST",
            "scheme": "http",
            "path": "/",
            "headers": [],
        }
        receive_channel: Queue[Any] = Queue()
        receive_channel.put_nowait({"type": "http.request", "body": b"", "more_body": True})
        receive_channel.put_nowait({"type": "http.disconnect"})
        send_channel: AsyncMock = AsyncMock()

        await self.app(scope, receive_channel.get, send_channel)
        send_channel.assert_not_called()

    async def test_empty_request(self) -> None:
        response: Response = await self.client.post("/", content=b"")
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.content, b"")

    async def test_invalid_json(self) -> None:
        response: Response = await self.client.post("/", content=b'{"jsonrpc": "2.0", "method": "foobar, "params": "bar", "baz]')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertDictEqual(
            response.json(),
            {
                "jsonrpc": "2.0",
                "error": {"code": ErrorEnum.PARSE_ERROR, "message": AnyNonEmptyString(self)},
                "id": None,
            },
        )

    async def test_invalid_request_object(self) -> None:
        response: Response = await self.client.post("/", json={"jsonrpc": "2.0", "method": 1, "params": "bar"})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertDictEqual(
            response.json(),
            {
                "jsonrpc": "2.0",
                "error": {"code": ErrorEnum.INVALID_REQUEST, "message": AnyNonEmptyString(self)},
                "id": None,
            },
        )

    async def test_empty_array(self) -> None:
        response: Response = await self.client.post("/", json=[])
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertDictEqual(
            response.json(),
            {
                "jsonrpc": "2.0",
                "error": {"code": ErrorEnum.INVALID_REQUEST, "message": AnyNonEmptyString(self), "data": []},
                "id": None,
            },
        )

    async def test_invalid_not_empty_batch(self) -> None:
        response: Response = await self.client.post("/", json=[1])
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertCountEqual(
            response.json(),
            [
                {
                    "jsonrpc": "2.0",
                    "error": {"code": ErrorEnum.INVALID_REQUEST, "message": AnyNonEmptyString(self), "data": 1},
                    "id": None,
                }
            ],
        )

    async def test_invalid_batch(self) -> None:
        response: Response = await self.client.post("/", json=[1, 2, 3])
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertCountEqual(
            response.json(),
            [
                {
                    "jsonrpc": "2.0",
                    "error": {"code": ErrorEnum.INVALID_REQUEST, "message": AnyNonEmptyString(self), "data": 1},
                    "id": None,
                },
                {
                    "jsonrpc": "2.0",
                    "error": {"code": ErrorEnum.INVALID_REQUEST, "message": AnyNonEmptyString(self), "data": 2},
                    "id": None,
                },
                {
                    "jsonrpc": "2.0",
                    "error": {"code": ErrorEnum.INVALID_REQUEST, "message": AnyNonEmptyString(self), "data": 3},
                    "id": None,
                },
            ],
        )

    async def test_method_not_found(self) -> None:
        uuid: str = self.random_id
        response: Response = await self.client.post("/", json={"jsonrpc": "2.0", "method": "foobar", "id": uuid})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertDictEqual(
            response.json(),
            {
                "jsonrpc": "2.0",
                "error": {"code": ErrorEnum.METHOD_NOT_FOUND, "message": AnyNonEmptyString(self)},
                "id": uuid,
            },
        )

    async def test_invalid_parameters_args(self) -> None:
        mock: AsyncMock = AsyncMock()

        @self.app.dispatcher.register(function_name="args_only")
        async def _(*args: Any) -> Any:
            return await mock(*args)

        uuid: str = self.random_id
        response: Response = await self.client.post(
            "/",
            json={
                "jsonrpc": "2.0",
                "method": "args_only",
                "params": {"a": 1, "b": 2},
                "id": uuid,
            },
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertDictEqual(
            response.json(),
            {
                "jsonrpc": "2.0",
                "error": {"code": ErrorEnum.INVALID_PARAMETERS, "message": AnyNonEmptyString(self)},
                "id": uuid,
            },
        )
        mock.assert_not_called()

    async def test_invalid_parameters_kwargs(self) -> None:
        mock: AsyncMock = AsyncMock()

        @self.app.dispatcher.register(function_name="kwargs_only")
        async def _(**kwargs: Any) -> Any:
            return await mock(**kwargs)

        uuid: str = self.random_id
        response: Response = await self.client.post(
            "/",
            json={
                "jsonrpc": "2.0",
                "method": "kwargs_only",
                "params": [1, 2, 3],
                "id": uuid,
            },
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertDictEqual(
            response.json(),
            {
                "jsonrpc": "2.0",
                "error": {"code": ErrorEnum.INVALID_PARAMETERS, "message": AnyNonEmptyString(self)},
                "id": uuid,
            },
        )
        mock.assert_not_called()

    async def test_unexpected_internal_error(self) -> None:
        mock: AsyncMock = AsyncMock(side_effect=Exception("for testing purposes"))

        @self.app.dispatcher.register(function_name="exception")
        async def _(**kwargs: Any) -> Any:
            return await mock(**kwargs)

        uuid: str = self.random_id
        response: Response = await self.client.post("/", json={"jsonrpc": "2.0", "method": "exception", "id": uuid})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertDictEqual(
            response.json(),
            {
                "jsonrpc": "2.0",
                "error": {"code": ErrorEnum.INTERNAL_ERROR, "message": AnyNonEmptyString(self)},
                "id": uuid,
            },
        )
        mock.assert_called_once()

    async def test_positional_parameters(self) -> None:
        mock: AsyncMock = AsyncMock(return_value=True)

        @self.app.dispatcher.register(function_name="mock")
        async def _(*args: Any, **kwargs: Any) -> bool:
            return await mock(*args, **kwargs)

        uuid: str = self.random_id
        response: Response = await self.client.post(
            "/",
            json={
                "jsonrpc": "2.0",
                "method": "mock",
                "params": [1, 2, 3],
                "id": uuid,
            },
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertDictEqual(response.json(), {"jsonrpc": "2.0", "result": True, "id": uuid})
        mock.assert_awaited_once_with(1, 2, 3)

    async def test_named_parameters(self) -> None:
        mock: AsyncMock = AsyncMock(return_value=False)

        @self.app.dispatcher.register(function_name="mock")
        async def _(*args: Any, **kwargs: Any) -> bool:
            return await mock(*args, **kwargs)

        uuid: str = self.random_id
        response: Response = await self.client.post(
            "/",
            json={
                "jsonrpc": "2.0",
                "method": "mock",
                "params": {"a": 1, "b": 2, "c": 3},
                "id": uuid,
            },
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertDictEqual(response.json(), {"jsonrpc": "2.0", "result": False, "id": uuid})
        mock.assert_awaited_once_with(a=1, b=2, c=3)

    async def test_notification(self) -> None:
        loop, mock, event = get_running_loop(), AsyncMock(), Event()

        @self.app.dispatcher.register(function_name="mock")
        async def _(*args: Any, **kwargs: Any) -> None:
            try:
                await mock(*args, **kwargs)
            finally:
                loop.call_soon(event.set)

        response: Response = await self.client.post("/", json={"jsonrpc": "2.0", "method": "mock", "params": [1, 2, 3]})
        await event.wait()
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.assertEqual(response.content, b"")
        mock.assert_awaited_once_with(1, 2, 3)

    async def test_invalid_json_response(self) -> None:
        @self.app.dispatcher.register(function_name="object")
        async def _() -> Any:
            return object()

        uuid: str = self.random_id
        response: Response = await self.client.post("/", json={"jsonrpc": "2.0", "method": "object", "id": uuid})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertDictEqual(
            response.json(),
            {
                "jsonrpc": "2.0",
                "error": {"code": ErrorEnum.PARSE_ERROR, "message": AnyNonEmptyString(self)},
                "id": None,
            },
        )

    async def test_gateway_timeout(self) -> None:
        @self.app.dispatcher.register(function_name="eternity")
        async def _() -> None:
            await wait_for(sleep(3600.0), timeout=0.001)

        uuid: str = self.random_id
        response: Response = await self.client.post("/", json={"jsonrpc": "2.0", "method": "eternity", "id": uuid})
        self.assertEqual(response.status_code, HTTPStatus.GATEWAY_TIMEOUT)
        self.assertEqual(response.content, b"")

    def tearDown(self) -> None:
        self.app.dispatcher.clear()
