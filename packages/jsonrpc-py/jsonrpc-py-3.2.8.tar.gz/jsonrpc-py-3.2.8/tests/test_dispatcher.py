from __future__ import annotations

from collections.abc import MutableMapping
from types import FunctionType, LambdaType
from typing import TYPE_CHECKING, TypeVar
from unittest import IsolatedAsyncioTestCase as AsyncioTestCase

from jsonrpc import AsyncDispatcher, Error, ErrorEnum

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import NoReturn

T = TypeVar("T")


class TestDispatcher(AsyncioTestCase):
    def setUp(self) -> None:
        self.dispatcher: AsyncDispatcher = AsyncDispatcher()

    def test_inheritance(self) -> None:
        self.assertIsInstance(self.dispatcher, MutableMapping)

    def test_register_not_function(self) -> None:
        with self.assertRaises(RuntimeError) as context:
            self.dispatcher.register(print)

        self.assertIn("isn't a user-defined function", str(context.exception))

    def test_register_already_defined(self) -> None:
        test_lambda: Callable[..., None] = lambda: None
        self.dispatcher.register(test_lambda, function_name="test_lambda")
        self.assertIn("test_lambda", self.dispatcher)
        self.assertIsInstance(self.dispatcher["test_lambda"], LambdaType)
        self.assertEqual(self.dispatcher["test_lambda"], test_lambda)

        with self.assertRaises(RuntimeError) as context:
            self.dispatcher.register(test_lambda, function_name="test_lambda")

        self.assertIn("is already defined", str(context.exception))

    async def test_dispatch_non_existent_function(self) -> None:
        with self.assertRaises(Error) as context:
            await self.dispatcher.dispatch("non_existent_function")

        self.assertEqual(context.exception.code, ErrorEnum.METHOD_NOT_FOUND)

    async def test_dispatch_non_existent_parameter(self) -> None:
        test_lambda: Callable[[T], T] = lambda obj: obj
        self.dispatcher.register(test_lambda, function_name="test_lambda")
        self.assertIn("test_lambda", self.dispatcher)
        self.assertIsInstance(self.dispatcher["test_lambda"], LambdaType)
        self.assertEqual(self.dispatcher["test_lambda"], test_lambda)

        with self.assertRaises(Error) as context:
            await self.dispatcher.dispatch("test_lambda", non_existent_parameter="non_existent_parameter")

        self.assertEqual(context.exception.code, ErrorEnum.INVALID_PARAMETERS)

    async def test_dispatch_division(self) -> None:
        @self.dispatcher.register(function_name="my_div")
        def div(a: float, b: float) -> float:
            return a / b

        self.assertNotIn("div", self.dispatcher)
        self.assertIn("my_div", self.dispatcher)
        self.assertIsInstance(self.dispatcher["my_div"], FunctionType)
        self.assertEqual(self.dispatcher["my_div"], div)

        with self.assertRaises(Error) as context:
            await self.dispatcher.dispatch("my_div", 10, 0)

        self.assertEqual(context.exception.code, ErrorEnum.INTERNAL_ERROR)
        self.assertIn("division by zero", context.exception.message)

    async def test_dispatch_raising(self) -> None:
        @self.dispatcher.register
        def raising(*, code: int, message: str) -> NoReturn:
            raise Error(code=code, message=message)

        self.assertIn("raising", self.dispatcher)
        self.assertIsInstance(self.dispatcher["raising"], FunctionType)
        self.assertEqual(self.dispatcher["raising"], raising)

        with self.assertRaises(Error) as context:
            await self.dispatcher.dispatch("raising", code=ErrorEnum.INTERNAL_ERROR, message="for testing purposes")

        self.assertEqual(context.exception.code, ErrorEnum.INTERNAL_ERROR)
        self.assertEqual(context.exception.message, "for testing purposes")
