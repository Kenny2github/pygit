import os
from .abstract import Serializable
from .blob import Blob
from .tree import Tree

TYPE_STRS = {
    b'blob': Blob,
    b'tree': Tree,
}

def dump_obj(obj: Serializable, cwd: str = '.'):
    """Dump an object into a file named after its hash.

    The file will be created inside ``cwd``.
    """
    obj.dump(os.path.join(cwd, obj.hash()))

def dump_tree(tree: Tree, cwd: str = '.'):
    """Dump a tree into a file named after its hash.
    Dump all of its child blobs too.

    The file(s) will be created inside ``cwd``.
    """
    for blob in tree.walk():
        dump_obj(blob, cwd)
    dump_obj(tree, cwd)