from __future__ import annotations

from dataclasses import is_dataclass
from unittest import TestCase

from jsonrpc import Error, ErrorEnum
from jsonrpc.utilities import Undefined


class TestError(TestCase):
    def test_inheritance(self) -> None:
        error: Error = Error(code=ErrorEnum.INTERNAL_ERROR, message="Internal Error")
        self.assertTrue(is_dataclass(error))
        self.assertIsInstance(error, Exception)

    def test_hash(self) -> None:
        for actual, expected in (
            (
                hash(Error(code=ErrorEnum.PARSE_ERROR, message="Parse Error")),
                hash((Error, ErrorEnum.PARSE_ERROR, "Parse Error", Undefined)),
            ),
            (
                hash(Error(code=ErrorEnum.INVALID_REQUEST, message="Invalid Request", data=[1, 2, 3])),
                hash((Error, ErrorEnum.INVALID_REQUEST, "Invalid Request", (1, 2, 3))),
            ),
        ):
            with self.subTest(actual=actual, expected=expected):
                self.assertEqual(actual, expected)

    def test_str(self) -> None:
        error: Error = Error(code=ErrorEnum.METHOD_NOT_FOUND, message="Method Not Found")
        self.assertEqual(str(error), f"{error.message!s}\u0020\u0028{error.code:d}\u0029")

    def test_json(self) -> None:
        for actual, expected in (
            (
                Error(code=ErrorEnum.INVALID_PARAMETERS, message="Invalid Parameters").json,
                {"code": ErrorEnum.INVALID_PARAMETERS, "message": "Invalid Parameters"},
            ),
            (
                Error(code=ErrorEnum.INTERNAL_ERROR, message="Internal Error", data={"additional": "information"}).json,
                {"code": ErrorEnum.INTERNAL_ERROR, "message": "Internal Error", "data": {"additional": "information"}},
            ),
        ):
            with self.subTest(actual=actual, expected=expected):
                self.assertDictEqual(actual, expected)
