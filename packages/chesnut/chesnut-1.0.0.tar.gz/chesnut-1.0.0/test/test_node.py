"""The tests mock a filesystem as an example to demonstrate the use of the Node class."""

from copy import deepcopy

from chesnut.node import Node


class FSNode(Node):
    """A generic filesystem node."""

    def __init__(self, name, parent=None):
        super().__init__(parent=parent)
        self.name = name


class Directory(FSNode):
    """A directory node."""

    def __init__(self, name, parent=None):
        super().__init__(name, parent=parent)


class File(FSNode):
    """A generic file node."""

    def __init__(self, name, parent=None):
        super().__init__(name, parent=parent)


class ImageFile(File):
    """An image file node."""

    def __init__(self, name, parent=None):
        super().__init__(name, parent=parent)


class TextFile(File):
    """A text file node."""

    def __init__(self, name, parent=None):
        super().__init__(name, parent=parent)


test_fs = Directory('test_fs')
dir1 = Directory('dir1', parent=test_fs)
dir2 = Directory('dir2', parent=test_fs)
dir1a = Directory('dir1a', parent=dir1)
dir1b = Directory('dir1b', parent=dir1)
image1 = ImageFile('image1', parent=dir1)
text1 = TextFile('text1', parent=dir1)
text1a = TextFile('text1a', parent=dir1a)


def test_creation():
    """Adds a new node to the filesystem and checks the parent-child
    relationship, creates a deepcopy to avoid modifying the original
    tree."""
    current_test_fs = deepcopy(test_fs)
    new_dir = Directory('new_dir', parent=current_test_fs)
    assert new_dir in current_test_fs.children
    assert new_dir.parent == current_test_fs


def test_parent():
    """Checks the parent of the nodes."""
    assert test_fs.parent is None
    assert dir1.parent == test_fs
    assert dir2.parent == test_fs
    assert dir1a.parent == dir1
    assert dir1b.parent == dir1
    assert image1.parent == dir1
    assert text1.parent == dir1
    assert text1a.parent == dir1a


def test_children():
    """Checks the children of the nodes, converts to a set to avoid order issues."""
    assert set(test_fs.children) == {dir1, dir2}
    assert set(dir1.children) == {dir1a, dir1b, image1, text1}
    assert set(dir1a.children) == {text1a}
    assert set(dir2.children) == set()


def test_height():
    """Checks the height of the nodes."""
    assert test_fs.height == 3
    assert dir1.height == 2
    assert dir2.height == 0
    assert dir1a.height == 1
    assert dir1b.height == 0
    assert image1.height == 0
    assert text1.height == 0
    assert text1a.height == 0


def test_depth():
    """Checks the depth of the nodes."""
    assert test_fs.depth == 0
    assert dir1.depth == 1
    assert dir2.depth == 1
    assert dir1a.depth == 2
    assert dir1b.depth == 2
    assert image1.depth == 2
    assert text1.depth == 2
    assert text1a.depth == 3


def test_descendants():
    """Checks the descendants of the nodes, converts to a set to avoid order issues."""
    assert set(test_fs.descendants) == {dir1, dir2, dir1a, dir1b, image1, text1, text1a}
    assert set(dir1.descendants) == {dir1a, dir1b, image1, text1, text1a}
    assert set(dir1a.descendants) == {text1a}
    assert set(dir2.descendants) == set()


def test_siblings():
    """Checks the siblings of the nodes, converts to a set to avoid order issues."""
    assert set(test_fs.siblings) == set()
    assert set(dir1.siblings) == {dir2}
    assert set(dir2.siblings) == {dir1}
    assert set(dir1a.siblings) == {dir1b, image1, text1}
    assert set(dir1b.siblings) == {dir1a, image1, text1}
    assert set(image1.siblings) == {text1, dir1a, dir1b}
    assert set(text1.siblings) == {image1, dir1a, dir1b}
    assert set(text1a.siblings) == set()


def test_ancestors():
    """Checks the ancestors of the nodes, converts to a set to avoid order issues."""
    assert set(test_fs.ancestors) == set()
    assert set(dir1.ancestors) == {test_fs}
    assert set(dir2.ancestors) == {test_fs}
    assert set(dir1a.ancestors) == {dir1, test_fs}
    assert set(dir1b.ancestors) == {dir1, test_fs}
    assert set(image1.ancestors) == {dir1, test_fs}
    assert set(text1.ancestors) == {dir1, test_fs}
    assert set(text1a.ancestors) == {dir1a, dir1, test_fs}


def test_root():
    """Checks the root of the nodes."""
    nodes = [test_fs, dir1, dir2, dir1a, dir1b, image1, text1, text1a]
    for node in nodes:
        assert node.root == test_fs


def test_is_root():
    """Checks if the nodes are root."""
    assert test_fs.is_root
    assert not dir1.is_root
    assert not dir2.is_root
    assert not dir1a.is_root
    assert not dir1b.is_root
    assert not image1.is_root
    assert not text1.is_root
    assert not text1a.is_root


def test_is_leaf():
    """Checks if the nodes are leaf."""
    assert not test_fs.is_leaf
    assert not dir1.is_leaf
    assert dir2.is_leaf
    assert not dir1a.is_leaf
    assert dir1b.is_leaf
    assert image1.is_leaf
    assert text1.is_leaf
    assert text1a.is_leaf


def test_children_by_type():
    """Checks the children by type of the nodes."""
    assert set(test_fs.children_by_type(Directory)) == {dir1, dir2}
    assert set(dir1.children_by_type(Directory)) == {dir1a, dir1b}
    assert set(dir1.children_by_type(File)) == {image1, text1}
    assert set(dir1a.children_by_type(File)) == {text1a}
    assert set(dir2.children_by_type(Directory)) == set()
    assert set(dir2.children_by_type(File)) == set()


def test_descendants_by_type():
    """Checks the descendants by type of the nodes."""
    assert set(test_fs.descendants_by_type(Directory)) == {dir1, dir2, dir1a, dir1b}
    assert set(dir1.descendants_by_type(Directory)) == {dir1a, dir1b}
    assert set(dir1.descendants_by_type(File)) == {image1, text1, text1a}
    assert set(dir1a.descendants_by_type(File)) == {text1a}
    assert set(dir2.descendants_by_type(Directory)) == set()
    assert set(dir2.descendants_by_type(File)) == set()


def test_siblings_by_type():
    """Checks the siblings by type of the nodes."""
    assert set(test_fs.siblings_by_type(Directory)) == set()
    assert set(dir1.siblings_by_type(Directory)) == {dir2}
    assert set(dir1.siblings_by_type(File)) == set()
    assert set(dir1a.siblings_by_type(File)) == {image1, text1}
    assert set(dir2.siblings_by_type(Directory)) == {dir1}
    assert set(dir2.siblings_by_type(File)) == set()


def test_ancestors_by_type():
    """Checks the ancestors by type of the nodes."""
    assert set(test_fs.ancestors_by_type(Directory)) == set()
    assert set(dir1.ancestors_by_type(Directory)) == {test_fs}
    assert set(dir1.ancestors_by_type(File)) == set()
    assert set(dir1a.ancestors_by_type(File)) == set()
    assert set(dir2.ancestors_by_type(Directory)) == {test_fs}
    assert set(dir2.ancestors_by_type(File)) == set()


def test_has_children_by_type():
    """Checks if the nodes have children by type."""
    assert test_fs.has_children_by_type(Directory)
    assert not test_fs.has_children_by_type(File)
    assert dir1.has_children_by_type(Directory)
    assert dir1.has_children_by_type(File)
    assert not dir2.has_children_by_type(Directory)
    assert not dir2.has_children_by_type(File)


def test_has_descendants_by_type():
    """Checks if the nodes have descendants by type."""
    assert test_fs.has_descendants_by_type(Directory)
    assert test_fs.has_descendants_by_type(File)
    assert dir1.has_descendants_by_type(Directory)
    assert dir1.has_descendants_by_type(File)
    assert not dir2.has_descendants_by_type(Directory)
    assert not dir2.has_descendants_by_type(File)


def test_has_siblings_by_type():
    """Checks if the nodes have siblings by type."""
    assert not test_fs.has_siblings_by_type(Directory)
    assert not test_fs.has_siblings_by_type(File)
    assert dir1.has_siblings_by_type(Directory)
    assert not dir1.has_siblings_by_type(File)
    assert dir1a.has_siblings_by_type(File)
    assert dir1a.has_siblings_by_type(Directory)
    assert dir2.has_siblings_by_type(Directory)
    assert not dir2.has_siblings_by_type(File)


def test_has_ancestors_by_type():
    """Checks if the nodes have ancestors by type."""
    assert not test_fs.has_ancestors_by_type(Directory)
    assert not test_fs.has_ancestors_by_type(File)
    assert dir1.has_ancestors_by_type(Directory)
    assert not dir1.has_ancestors_by_type(File)
    assert dir1a.has_ancestors_by_type(Directory)
    assert not dir1a.has_ancestors_by_type(File)
    assert dir2.has_ancestors_by_type(Directory)
    assert not dir2.has_ancestors_by_type(File)


def test_repr():
    """Tests the string representation of a node."""
    assert (repr(test_fs)) == 'Directory()'
    assert (repr(text1)) == 'TextFile()'
    assert (repr(dir1)) == 'Directory()'
    assert (repr(image1)) == 'ImageFile()'
