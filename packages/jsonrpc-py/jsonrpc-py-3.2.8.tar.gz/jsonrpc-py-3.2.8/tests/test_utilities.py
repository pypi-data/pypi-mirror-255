from __future__ import annotations

import gc
from asyncio import create_task, sleep, wait_for
from dataclasses import is_dataclass
from typing import TYPE_CHECKING
from unittest import IsolatedAsyncioTestCase as AsyncioTestCase, TestCase
from unittest.mock import AsyncMock, MagicMock, sentinel

from jsonrpc.utilities import BackgroundTask, CancellableGather, PrioritizedItem, Undefined, UndefinedType, ensure_async, make_hashable

if TYPE_CHECKING:
    from typing import Any, Literal, NoReturn


class TestBackgroundTask(AsyncioTestCase):
    async def test_from_coroutine(self) -> None:
        mock: AsyncMock = AsyncMock(return_value="for testing purposes")
        background_task: BackgroundTask[str] = BackgroundTask.from_coroutine(mock(1, 2, 3, key="value"))

        self.assertEqual(hash(background_task), hash((BackgroundTask, background_task.task_id)))
        self.assertTrue(background_task.registry)
        self.assertIn(background_task, background_task.registry)

        result: str = await background_task
        self.assertEqual(result, "for testing purposes")
        self.assertFalse(background_task.registry)
        self.assertNotIn(background_task, background_task.registry)

    async def test_with_gc_collect(self) -> None:
        async def eternity() -> None:
            await sleep(3600.0)

        BackgroundTask.from_coroutine(eternity())
        self.assertTrue(BackgroundTask.registry)

        gc.collect()
        gc.collect()
        gc.collect()

        del eternity
        self.assertTrue(BackgroundTask.registry)

    def tearDown(self) -> None:
        BackgroundTask.registry.clear()


class TestCancellableGather(AsyncioTestCase):
    def test_prioritized_item(self) -> None:
        self.assertTrue(is_dataclass(prioritized_item := PrioritizedItem(0, "for testing purposes")))
        self.assertEqual(prioritized_item, PrioritizedItem(0, b"for testing purposes"))
        self.assertNotEqual(prioritized_item, PrioritizedItem(123, "for testing purposes"))
        self.assertLess(prioritized_item, PrioritizedItem(1, "the other one"))
        self.assertNotEqual(prioritized_item, "for testing purposes")

        with self.assertRaises(TypeError):
            prioritized_item < "for testing purposes"  # noqa: B015

    async def test_awaited_once(self) -> None:
        mocks: set[AsyncMock] = {AsyncMock(return_value=i) for i in ("a", "b", "c")}

        async def inner(mock: AsyncMock) -> Any:
            return await mock()

        results: tuple[str, ...] = await CancellableGather(map(inner, mocks))
        self.assertCountEqual(results, ("a", "b", "c"))

        for mock in mocks:
            with self.subTest(mock=mock):
                mock.assert_awaited_once()

    async def test_preserved_order(self) -> None:
        results: tuple[str, ...] = await CancellableGather(
            (
                sleep(0.004, "a"),  # <-- accepted latest but should be first in results
                sleep(0.002, "b"),  # <-- accepted second and should be second in results
                sleep(0.001, "c"),  # <-- accepted first but should be third in results
                sleep(0.003, "d"),  # <-- accepted third but should be latest in results
            )
        )
        self.assertTupleEqual(results, ("a", "b", "c", "d"))

    async def test_exception(self) -> None:
        first_exception_mock: AsyncMock = AsyncMock(side_effect=Exception("first exception"))
        second_exception_mock: AsyncMock = AsyncMock(side_effect=Exception("second exception"))

        async def inner(mock: AsyncMock) -> Any:
            return await mock()

        with self.assertRaises(Exception) as context:
            await CancellableGather(map(inner, (first_exception_mock, second_exception_mock)))

        self.assertRegex(str(context.exception), r"(?:first|second) exception")
        first_exception_mock.assert_awaited_once()
        second_exception_mock.assert_awaited_once()

    async def test_timeout_error(self) -> None:
        hello_task, world_task = (
            create_task(sleep(3600.0, "hello")),
            create_task(sleep(3600.0, "world")),
        )
        with self.assertRaises(TimeoutError):
            await CancellableGather(
                [
                    wait_for(hello_task, timeout=0.001),
                    wait_for(world_task, timeout=0.002),
                ]
            )
        self.assertTrue(hello_task.cancelled())
        self.assertTrue(world_task.cancelled())

    async def test_exception_group(self) -> None:
        async def inner() -> NoReturn:
            raise ExceptionGroup(
                "one",
                (
                    Exception("for testing purposes"),  # <-- this should be raised first
                    ExceptionGroup(
                        "two",
                        (
                            Exception("2"),
                            Exception("3"),
                        ),
                    ),
                    ExceptionGroup(
                        "three",
                        (
                            Exception("4"),
                            Exception("5"),
                        ),
                    ),
                ),
            )

        with self.assertRaises(Exception) as context:
            await CancellableGather([inner()])

        self.assertEqual(str(context.exception), "for testing purposes")


class TestAsyncioUtilities(AsyncioTestCase):
    async def test_ensure_async(self) -> None:
        for mock in (
            MagicMock(return_value=sentinel.sync_def),
            AsyncMock(return_value=sentinel.async_def),
        ):
            with self.subTest(mock=mock):
                result: Any = await ensure_async(mock, 1, 2, 3, key="value")
                self.assertIs(result, mock.return_value)
                mock.assert_called_once_with(1, 2, 3, key="value")


class TestHashable(TestCase):
    def test_equality(self) -> None:
        tests: tuple[tuple[Any, Any], ...] = (
            ([], ()),
            (["a", 1], ("a", 1)),
            ({}, ()),
            ({"a"}, ("a",)),
            (frozenset({"a"}), {"a"}),
            ({"a": 1, "b": 2}, (("a", 1), ("b", 2))),
            ({"b": 2, "a": 1}, (("a", 1), ("b", 2))),
            (("a", ["b", 1]), ("a", ("b", 1))),
            (("a", {"b": 1}), ("a", (("b", 1),))),
        )
        for actual, expected in tests:
            with self.subTest(actual=actual):
                self.assertEqual(make_hashable(actual), expected)

    def test_count_equality(self) -> None:
        tests: tuple[tuple[Any, Any], ...] = (
            ({"a": 1, "b": ["a", 1]}, (("a", 1), ("b", ("a", 1)))),
            ({"a": 1, "b": ("a", [1, 2])}, (("a", 1), ("b", ("a", (1, 2))))),
        )
        for actual, expected in tests:
            with self.subTest(actual=actual):
                self.assertCountEqual(make_hashable(actual), expected)

    def test_unhashable(self) -> None:
        class Unhashable:
            __hash__: Literal[None] = None

        with self.assertRaises(TypeError) as context:
            make_hashable(Unhashable())

        self.assertIn("unhashable type", str(context.exception))


class TestUndefined(TestCase):
    def test_hash(self) -> None:
        self.assertEqual(hash(Undefined), 0xDEADBEEF)

    def test_equality(self) -> None:
        self.assertEqual(Undefined, UndefinedType())
        self.assertNotEqual(Undefined, None)

    def test_is_truth(self) -> None:
        self.assertFalse(Undefined)
