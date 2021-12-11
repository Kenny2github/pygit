import io
import zlib
import unittest
from pygit.zlibfiles import compress_and_copy, decompress_and_copy, WBITS
from . import TEST_STRING

class TestZlibFiles(unittest.TestCase):

    infile = io.BytesIO(TEST_STRING)

    def test_compress(self) -> None:
        for level in range(-1, 10):
            with self.subTest(compression_level=level):
                compress = zlib.compressobj(level=level, wbits=WBITS)
                expected_out = compress.compress(
                    TEST_STRING) + compress.flush()
                self.infile.seek(0)

                outfile = io.BytesIO()
                compress_and_copy(self.infile, outfile, level=level)
                self.assertEqual(outfile.getvalue(), expected_out)

                outfile.seek(0)
                infile = io.BytesIO()
                decompress_and_copy(outfile, infile)
                self.assertEqual(infile.getvalue(), TEST_STRING)

if __name__ == '__main__':
    unittest.main()
