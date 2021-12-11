from __future__ import annotations
from functools import partial
import os
from shutil import copyfileobj
from hashlib import sha256
from typing import BinaryIO, Optional, Type, Union
from .abstract import Serializable
from .zlibfiles import compress_and_copy

class Blob(Serializable):
    """Serializable binary data."""

    def _size(self) -> int:
        raise NotImplementedError

    def _header(self) -> bytes:
        return b'blob' + self._size().to_bytes(8, 'big', signed=False)

    def __repr__(self) -> str:
        return f'<blob {self.hash()}>'

class MemBlob(Blob):
    """Serializable binary data, held in memory. This object is immutable."""
    content: bytes

    _instances = {}

    def __new__(cls: Type[MemBlob], *args, **kwargs) -> MemBlob:
        inst: MemBlob = object.__new__(cls)
        inst.__init__(*args, **kwargs)
        key = hash(inst)
        return cls._instances.setdefault(key, inst)

    def __init__(self, content: Optional[bytes] = None) -> None:
        self.content = content or b''

    def _size(self) -> int:
        return len(self.content)

    def __bytes__(self) -> bytes:
        return self._header() + self.content

class FileBlob(Blob):
    """Serializable binary data, held in a file object."""
    file: BinaryIO

    def __init__(self, file: Union[BinaryIO, str]) -> None:
        """If a file object is passed, it must support seeking."""
        if isinstance(file, str):
            file = open(file, 'rb')
        self.file = file

    def __del__(self):
        try:
            self.file.close()
        except (AttributeError, TypeError):
            pass # don't bother calling a close method if it doesn't exist

    def _size(self) -> int:
        return self.file.seek(0, os.SEEK_END)

    def _hash(self, chunk_size=1024):
        sha = sha256(self._header())
        self.file.seek(0, os.SEEK_SET)
        while chunk := self.file.read(chunk_size):
            sha.update(chunk)
        return sha

    def dump(self, file: Union[BinaryIO, str],
             compression_level: Optional[int] = -1) -> None:
        header = self._header()
        self.file.seek(0, os.SEEK_SET)
        if compression_level is None:
            copy = copyfileobj
        else:
            copy = partial(compress_and_copy, level=compression_level)
        if isinstance(file, str):
            with open(file, 'wb') as f:
                f.write(header)
                copy(self.file, f)
        else:
            file.write(header)
            copy(self.file, file)
