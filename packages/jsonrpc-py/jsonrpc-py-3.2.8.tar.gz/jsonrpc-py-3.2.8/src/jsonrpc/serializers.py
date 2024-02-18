from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from .errors import Error, ErrorEnum

try:
    from ujson import dumps as _ujson_dumps, loads as _ujson_loads

    json_encode = partial(_ujson_dumps, ensure_ascii=False, escape_forward_slashes=False)
    json_decode = partial(_ujson_loads)
except ImportError:
    from json import dumps as _json_dumps, loads as _json_loads

    json_encode = partial(_json_dumps, ensure_ascii=False, separators=(",", ":"))
    json_decode = partial(_json_loads)

if TYPE_CHECKING:
    from typing import Any

__all__: tuple[str, ...] = ("JSONSerializer",)


class JSONSerializer:
    """
    Simple class for JSON serialization and deserialization.
    """

    __slots__: tuple[str, ...] = ()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def serialize(self, obj: Any, /) -> bytes:
        """
        Returns the JSON representation of a value.

        :param obj: An any type of object that must be JSON serializable.
        :raises jsonrpc.Error: If any exception has occurred due the serialization or/and encoding to :py:class:`bytes`.
        :returns: The :py:class:`bytes` object containing the serialized Python data structure.
        """
        try:
            return json_encode(obj).encode("utf-8")
        except Exception as exc:
            raise Error(code=ErrorEnum.PARSE_ERROR, message="Failed to serialize object to JSON") from exc

    def deserialize(self, obj: bytes, /) -> Any:
        """
        Returns the value encoded in JSON in appropriate Python type.

        :param obj: The :py:class:`bytes` object containing the serialized JSON document.
        :raises jsonrpc.Error: If any exception has occurred due the deserialization or/and decoding from :py:class:`bytes`.
        :returns: An any type of object containing the deserialized Python data structure.
        """
        try:
            return json_decode(obj)
        except Exception as exc:
            raise Error(code=ErrorEnum.PARSE_ERROR, message="Failed to deserialize object from JSON") from exc
