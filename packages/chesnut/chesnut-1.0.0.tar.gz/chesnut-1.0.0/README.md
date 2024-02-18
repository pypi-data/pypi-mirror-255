<h2 align="center">
  <img src="https://raw.githubusercontent.com/m4ttm/chesnut/main/chesnut.svg", alt="Chesnut Logo" max-width="30vw">
  <a href="https://m4ttm.github.io/chesnut">docs</a> |
  <a href="https://pypi.org/project/chesnut">pip</a>
</h1>
<span class="pdoc-start">
`Chesnut` is a lightweight tree class implementation in Python that offers a simple approach to search tree structures. By inheriting from the `Node` class, you can create your custom nodes and leverage its methods for efficient tree navigation.


## Installation

Install chesnut using pip. 
```bash
pip install chesnut
```

Then you can use the `Node` class in your project.

```python
from chesnut import Node
```


## Usage

### Creating Custom Nodes
You can subclass the `Node` class to create your custom nodes and add your own attributes and methods.

```python
class CustomNode(Node):
    def __init__(self, data, parent=None):
        super().__init__(parent=parent)
        self.data = data
```

### Building a Tree

```python
# Creating nodes
root_node = CustomNode(data="Root")
child_node1 = CustomNode(data="Child 1", parent=root_node)
child_node2 = CustomNode(data="Child 2", parent=root_node)
grandchild_node = CustomNode(data="Grandchild", parent=child_node1)
```

### Using Node Attributes
For a complete list of methods, see the [documentation](https://m4ttm.github.io/chesnut/chesnut/node.html).

#### Finding Nodes

```python
# Finding the root
root = child_node1.root

# Checking if a node is the root
is_root = root_node.is_root  # True
```

#### Querying Nodes

```python
# Querying children by type
children_of_type = root_node.children_by_type(CustomNode)  # List of CustomNode instances

# Querying descendants by type
descendants_of_type = root_node.descendants_by_type(CustomNode)  # List of CustomNode instances
```

#### Checking Node Relationships

```python
# Checking if a node has children of a specific type
has_children = root_node.has_children_by_type(CustomNode)  # True or False

# Checking if a node has descendants of a specific type
has_descendants = root_node.has_descendants_by_type(CustomNode)  # True or False
```


By using the `Node` class as a base for your custom nodes, you can take advantage of its methods to easily navigate and manipulate your tree structure. This inheritance approach allows you to focus on the specific functionality of your custom nodes while benefiting from the tree-related operations provided by chesnut.


## Testing
You can run the tests with:
```bash
make test
```

Coverage can be checked at function level with:
```bash
make coverage
```

Linting can be performed with:
```bash
make lint
```


## Documentation
Documentation is available [here](https://m4ttm.github.io/chesnut). It is generated from the docstrings using [pdoc](https://pdoc.dev). You can generate this yourself using:
```bash
make docs
```
This will generate the documentation in the `docs` folder, open `docs/index.html` in your browser to see the documentation.


## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/m4ttm/chesnut/blob/main/LICENSE) file for details.

