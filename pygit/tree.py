from collections import OrderedDict
from typing import Generator, Optional, Union

from pygit.blob import Blob
from .abstract import Serializable

TreeInternal = OrderedDict[str, Serializable]

class Tree(Serializable):
    """Tree structure containing named blobs."""
    contents: TreeInternal

    def __init__(self, contents: Optional[TreeInternal] = None) -> None:
        self.contents = contents or OrderedDict()

    def add(self, name: str, obj: Serializable, do_sort: bool = True) -> None:
        """Name an object and add it to the tree.

        The object could be another tree, a blob, et cetera.
        """
        self.contents[name] = obj

    def sort(self) -> None:
        """Sort the tree by object name. Called before serialization."""
        self.contents = OrderedDict(
            (k, self.contents[k]) for k in sorted(self.contents.keys()))

    def discard(self, ident: Union[str, Serializable]) -> None:
        """Discard an object from the tree.

        If ``ident`` is a string, the object with that name will be discarded.
        If ``ident`` is serializable, all appearances of it are removed
        (i.e. if a.bin and b.bin refer to the same object, both are removed.
        There is no indication of whether the object was present.
        """
        if isinstance(ident, str):
            del self.contents[ident]
        elif isinstance(ident, Serializable):
            self.contents = OrderedDict(
                (k, v) for k, v in self.contents.items()
                if v is not ident)
        else:
            raise TypeError(f"unexpected '{type(ident).__name__}' for ident")

    def walk(self) -> Generator[Blob, None, None]:
        """Walk the tree, yielding Blobs at all levels."""
        for v in self.contents.values():
            if isinstance(v, Blob):
                yield v
            elif isinstance(v, Tree):
                yield from v.walk()

    def __bytes__(self) -> bytes:
        result = []
        self.sort()
        for name, obj in self.contents.items():
            line = [b'\n']
            name = name.encode('utf8')
            line.append(len(name).to_bytes(8, 'big', signed=False))
            line.append(name)
            line.append(obj.bhash())
            result.append(b''.join(line))
        cont = b''.join(result)
        return b'tree' + len(cont).to_bytes(8, 'big', signed=False) + cont

    def __repr__(self) -> str:
        s = ', '.join(f'{k}: {v}' for k, v in self.contents.items())
        return f'<tree {s}>'