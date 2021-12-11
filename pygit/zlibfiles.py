from types import FunctionType
from typing import BinaryIO
import zlib

WBITS = -15

def _zlib_and_copy(infile: BinaryIO, outfile: BinaryIO,
                   flate: FunctionType, chunk_size: int):
    infile_read = infile.read
    outfile_write = outfile.write
    while data := infile_read(chunk_size):
        data = flate(data)
        outfile_write(data)
    # flushing must be done by caller

def compress_and_copy(infile: BinaryIO, outfile: BinaryIO,
                      level: int = -1, chunk_size: int = 64 * 1024):
    """Compress ``infile`` and write the compressed data to ``outfile``."""
    compress = zlib.compressobj(level=level, wbits=WBITS)
    _zlib_and_copy(infile, outfile, compress.compress, chunk_size)
    outfile.write(compress.flush())

def decompress_and_copy(infile: BinaryIO, outfile: BinaryIO,
                        chunk_size: int = 64 * 1024):
    """Decompress ``infile`` and write the compressed data to ``outfile``."""
    decompress = zlib.decompressobj(wbits=WBITS)
    _zlib_and_copy(infile, outfile, decompress.decompress, chunk_size)
    outfile.write(decompress.flush())