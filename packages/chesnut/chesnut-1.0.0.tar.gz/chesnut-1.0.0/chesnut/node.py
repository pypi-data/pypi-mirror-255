"""
Chesnut provides a generic tree node class that can be used to represent a hierarchical data structure. It contains a
single class, Node which can be linked to parent and children nodes to form a tree. The Node class provides methods to
traverse the tree and filter nodes by type based on their subclass.
"""

from abc import ABC
from typing import Generic, List, Optional, TypeVar, Union

# This allows Node to be used as a type hint for itself
NodeT = TypeVar("NodeT", bound="Node")


class Node(Generic[NodeT], ABC):
    """
    A node within a tree structure. This is intended to be subclassed to provide filtering for specific types of nodes.
    It is expected that further node specific state and methods will be added to subclasses.
    """

    def __init__(self, parent: Optional[NodeT] = None, children: Optional[List[NodeT]] = None):
        """
        Initialise the node with a parent and children, if there's no parent then it's considered the root of the tree

        Args:
            parent (optional[Node]): The parent node (if any), defaults to None for the root node
            children (optional[List[Node]]): The child nodes (if any), defaults to an empty list
        """
        assert parent is None or isinstance(parent, Node), "Parent must be a Node or None"
        self.parent: Union[NodeT, None] = parent
        """The parent is a single node that is directly above this node in the tree"""
        self.children: List[NodeT] = children or []
        """Children are the nodes that are directly below this node in the tree"""
        if parent is not None:
            self.parent.children.append(self)

    @property
    def height(self) -> int:
        """
        Height is the number of edges on the longest path from the node to a leaf (smallest is 0)

        Returns:
            int: The height of the node
        """
        return max([child.height for child in self.children] or [-1]) + 1

    @property
    def depth(self) -> int:
        """
        Depth is the number of edges from the node to the root (smallest is 0)

        Returns:
            int: The depth of the node
        """
        return len(self.ancestors)

    @property
    def descendants(self) -> List[NodeT]:
        """
        Descendants are child nodes of this node and all children recursively

        Returns:
            List[Node]: The list of descendant nodes
        """
        return self.children + [descendant for child in self.children for descendant in child.descendants]


    @property
    def siblings(self) -> List[NodeT]:
        """
        Siblings are nodes that share the same parent

        Returns:
            List[Node]: The list of sibling nodes
        """
        return [child for child in self.parent.children if child is not self] if self.parent is not None else []

    @property
    def ancestors(self) -> List[NodeT]:
        """
        Ancestors are the parent nodes of this node and all parents recursively

        Returns:
            List[Node]: The list of ancestor nodes
        """
        return [self.parent] + self.parent.ancestors if self.parent is not None else []

    @property
    def root(self) -> NodeT:
        """
        The root node of the tree, which is the topmost node

        Returns:
            Node: The root node of the tree
        """
        return self.parent.root if self.parent is not None else self

    @property
    def is_root(self) -> bool:
        """
        Check if this node is the root of the tree (i.e. it has no parent)

        Returns:
            bool: True if this node is the root of the tree, otherwise False
        """
        return self.parent is None

    @property
    def is_leaf(self) -> bool:
        """
        Check if this node is a leaf node (i.e. it has no children)

        Returns:
            bool: True if this node is a leaf node, otherwise False
        """
        return len(self.children) == 0

    def children_by_type(self, node_types: Union[NodeT, List[NodeT]]) -> List[NodeT]:
        """
        Children by a given type, you can inherit from Node and use this method to filter children by type

        Args:
            node_types (Union[Node, List[Node]]): The type of nodes to return, a single type or a list of types

        Returns:
            List[Node]: The list of child nodes of the given type
        """
        return [child for child in self.children if isinstance(child, node_types)]

    def descendants_by_type(self, node_types: Union[NodeT, List[NodeT]]) -> List[NodeT]:
        """
        Descendants by a given type, you can inherit from Node and use this method to filter descendants by type

        Args:
            node_types (Union[Node, List[Node]]): The type of nodes to return, a single type or a list of types

        Returns:
            List[Node]: The list of descendant nodes of the given type
        """
        return [descendant for descendant in self.descendants if isinstance(descendant, node_types)]

    def siblings_by_type(self, node_types: Union[NodeT, List[NodeT]]) -> List[NodeT]:
        """
        Siblings by a given type, you can inherit from Node and use this method to filter siblings by type

        Args:
            node_types: (Union[Node, List[Node]): The type of nodes to return, a single type or a list of types

        Returns:
            List[Node]: The list of sibling nodes of the given type
        """
        return [sibling for sibling in self.siblings if isinstance(sibling, node_types)]

    def ancestors_by_type(self, node_types: Union[NodeT, List[NodeT]]) -> List[NodeT]:
        """
        Ancestors by a given type, you can inherit from Node and use this method to filter ancestors by type

        Args:
            node_types: (Union[Node, List[Node]): The type of nodes to return, a single type or a list of types

        Returns:
            List[Node]: The list of ancestor nodes of the given type
        """
        return [ancestor for ancestor in self.ancestors if isinstance(ancestor, node_types)]

    def has_children_by_type(self, node_types: Union[NodeT, List[NodeT]]) -> bool:
        """Check if this node has any children of the specified object type

        Args:
            node_types: (Union[Node, List[Node]): The type of nodes to check for, a single type or a list of types

        Returns:
            bool: True if this node has children of the specified type, otherwise False
        """
        return any(isinstance(child, node_types) for child in self.children)

    def has_descendants_by_type(self, node_types: Union[NodeT, List[NodeT]]) -> bool:
        """Check if this node has any descendants of the specified object type

        Args:
            node_types: (Union[Node, List[Node]): The type of nodes to check for, a single type or a list of types

        Returns:
            bool: True if this node has descendants of the specified type, otherwise False
        """
        return any(isinstance(descendant, node_types) for descendant in self.descendants)

    def has_siblings_by_type(self, node_types: Union[NodeT, List[NodeT]]) -> bool:
        """Check if this node has any siblings of the specified object type

        Args:
            node_types: (Union[Node, List[Node]): The type of nodes to check for, a single type or a list of types

        Returns:
            bool: True if this node has siblings of the specified type, otherwise False
        """
        return any(isinstance(sibling, node_types) for sibling in self.siblings)

    def has_ancestors_by_type(self, node_types: Union[NodeT, List[NodeT]]) -> bool:
        """Check if this node has any ancestors of the specified object type

        Args:
            node_types: (Union[Node, List[Node]): The type of nodes to check for, a single type or a list of types

        Returns:
            bool: True if this node has ancestors of the specified type, otherwise False
        """
        return any(isinstance(ancestor, node_types) for ancestor in self.ancestors)

    def __repr__(self) -> str:
        """
        Return a string representation of the node for debugging

        Returns:
            str: A string representation of the node
        """
        repr_str = f"{self.__class__.__name__}()"
        return repr_str
