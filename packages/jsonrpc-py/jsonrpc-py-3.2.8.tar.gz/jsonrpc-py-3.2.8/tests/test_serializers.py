from __future__ import annotations

from collections.abc import MutableSequence
from unittest import TestCase

from jsonrpc import Error, ErrorEnum, JSONSerializer


class TestJSONSerializer(TestCase):
    def setUp(self) -> None:
        self.serializer: JSONSerializer = JSONSerializer()

    def test_serialize(self) -> None:
        self.assertIsInstance(self.serializer.serialize([1, 2, 3]), bytes)
        self.assertEqual(self.serializer.serialize(None), b"null")

        with self.assertRaises(Error) as context:
            self.serializer.serialize(object())

        self.assertEqual(context.exception.code, ErrorEnum.PARSE_ERROR)
        self.assertEqual(context.exception.message, "Failed to serialize object to JSON")

    def test_deserialize(self) -> None:
        self.assertIsInstance(sequence := self.serializer.deserialize(b"[1, 2, 3]"), MutableSequence)
        self.assertListEqual(sequence, [1, 2, 3])

        with self.assertRaises(Error) as context:
            self.serializer.deserialize(b"hello world")

        self.assertEqual(context.exception.code, ErrorEnum.PARSE_ERROR)
        self.assertEqual(context.exception.message, "Failed to deserialize object from JSON")
