from typing import BinaryIO, Optional, Union
from hashlib import sha256
from zlib import compress

class Serializable:
    """Objects of this type are serializable to a string to write to disk."""

    _cached_hash = None

    def __bytes__(self) -> bytes:
        """The data to write to disk."""
        raise NotImplementedError

    def _hash(self):
        """Unique hash that identifies this serializable object."""
        return sha256(bytes(self))

    def __hash(self):
        """Cache the implementation-defined hash and return it."""
        if self._cached_hash is None:
            self._cached_hash = self._hash()
        return self._cached_hash

    def hash(self) -> str:
        """String hash of this object."""
        return self.__hash().hexdigest()

    def bhash(self) -> bytes:
        """Bytes hash of this object."""
        return self.__hash().digest()

    def __hash__(self) -> int:
        """Integer hash of this object."""
        return int.from_bytes(self.bhash(), 'big', signed=False)

    def dump(self, file: Union[BinaryIO, str],
             compression_level: Optional[int] = -1) -> None:
        """Write the data to disk.

        If ``file`` is a string, the corresponding file is opened
        for writing in binary mode.
        Otherwise, it had better support the .write() method.
        If ``compression_level`` is None, no compression at all
        is applied to the data (it is written unchanged).
        Otherwise, its value is passed onto zlib.compress().
        """
        if compression_level is None:
            s = bytes(self)
        else:
            s = compress(bytes(self), compression_level)
        if isinstance(file, str):
            with open(file, 'wb') as f:
                f.write(s)
        else:
            file.write(s)