import io
from hashlib import sha256
import unittest
from pygit.blob import FileBlob, MemBlob
from . import TEST_STRING, LENGTH

header = b'blob' + LENGTH
formatted = header + TEST_STRING
formatted_hash = sha256(formatted).hexdigest()

class _TestBlob(unittest.TestCase):

    def test_hash(self) -> None:
        self.assertEqual(self.blob1.hash(), formatted_hash)

    def test_size_and_header(self) -> None:
        self.assertEqual(self.blob1._size(), len(TEST_STRING))
        self.assertEqual(self.blob1._header(), header)

class TestMemBlob(_TestBlob):

    def setUp(self) -> None:
        self.blob1 = MemBlob(TEST_STRING)

    def test_bytes(self) -> None:
        self.assertEqual(bytes(self.blob1), formatted)

    def test_singleton(self) -> None:
        blob2 = MemBlob(TEST_STRING)
        self.assertIs(self.blob1, blob2)

class TestFileBlob(_TestBlob):

    def setUp(self) -> None:
        self.file = io.BytesIO(TEST_STRING)
        self.blob1 = FileBlob(self.file)

    def test_bytes(self) -> None:
        with self.assertRaises(NotImplementedError):
            bytes(self.blob1)

if __name__ == '__main__':
    unittest.main()
