from __future__ import annotations

from asyncio import CancelledError
from functools import partial
from inspect import isfunction, signature
from typing import TYPE_CHECKING, overload
from weakref import WeakValueDictionary

from .errors import Error, ErrorEnum
from .typedefs import AnyCallable
from .utilities import ensure_async

if TYPE_CHECKING:
    from collections.abc import Callable
    from inspect import BoundArguments
    from typing import Any

    from .typedefs import Func

__all__: tuple[str, ...] = ("AsyncDispatcher",)


class AsyncDispatcher(WeakValueDictionary[str, AnyCallable]):
    """
    The :py:class:`weakref.WeakValueDictionary` subclass representing the storage of user-defined functions.
    """

    __slots__: tuple[str, ...] = ()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    @overload
    def register(self, user_function: Func, /) -> Func: ...

    @overload
    def register(self, user_function: Func, *, function_name: str | None = ...) -> Func: ...

    @overload
    def register(self, *, function_name: str | None = ...) -> Callable[[Func], Func]: ...

    def register(self, user_function: Func | None = None, *, function_name: str | None = None) -> Any:
        """
        Adds a user-defined function to the dispatcher.

        Example usage::

            >>> @dispatcher.register
            ... def truediv(a: float, b: float) -> float:
            ...     return a / b

        Also you can pass the different function's name::

            >>> @dispatcher.register(function_name="slow_greetings")
            ... async def _(name: str) -> str:
            ...     return await sleep(3600.0, f"Greetings, {name} !!")

        :param user_function: The :py:data:`types.FunctionType` object representing the user-defined function.
        :param function_name: An optional function's name. If it is omitted, attribute ``__name__`` will be used instead.
        :raises RuntimeError: If the ``user_function`` isn't passed by the :py:func:`inspect.isfunction` method,
            or function with the provided name is already defined in the :class:`jsonrpc.AsyncDispatcher` class.
        :returns: The unmodified ``user_function`` object, passed in the parameters.
        """
        if user_function is None:
            return partial(self.register, function_name=function_name)

        if not isfunction(user_function):
            raise RuntimeError(f"{type(user_function).__name__!r} isn't a user-defined function")

        if (function_name := user_function.__name__ if function_name is None else function_name) in self:
            raise RuntimeError(f"{function_name!r} is already defined in {self[function_name].__module__!r}")

        self[function_name] = user_function
        return user_function

    async def dispatch(self, function_name: str, /, *args: Any, **kwargs: Any) -> Any:
        """
        Invoke the user-defined function by passed in parameters function's name.

        Example usage::

            >>> dispatcher = AsyncDispatcher()
            >>> await dispatcher.dispatch("sum", a=12, b=34)
            46

        :param function_name: The user-defined function's name.
        :param args: Positional arguments for the provided function.
        :param kwargs: Keyword arguments for the provided function.
        :raises jsonrpc.Error: If the function doesn't exists in the :class:`jsonrpc.AsyncDispatcher` class,
            passed invalid parameters or unexpected internal error has raised. See also :class:`jsonrpc.ErrorEnum`.
        :returns: Result of execution the user-defined function.
        """
        try:
            user_function: AnyCallable = self[function_name]
        except KeyError as exc:
            raise Error(code=ErrorEnum.METHOD_NOT_FOUND, message=f"Function {function_name!r} isn't found") from exc

        try:
            params: BoundArguments = signature(user_function).bind(*args, **kwargs)
        except TypeError as exc:
            raise Error(code=ErrorEnum.INVALID_PARAMETERS, message=f"Invalid parameters: {exc!s}") from exc

        try:
            return await ensure_async(user_function, *params.args, **params.kwargs)
        except (TimeoutError, CancelledError, Error):
            raise
        except Exception as exc:
            raise Error(code=ErrorEnum.INTERNAL_ERROR, message=f"Unexpected internal error: {exc!s}") from exc
