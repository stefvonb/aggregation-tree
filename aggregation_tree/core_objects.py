class TreeNode:
    """
    A CalculatedTreeNode is essentially a tree object, since we branch off from this using the add_child() method.
    """
    __slots__ = ['name', 'parent', 'children', '_value', 'shared_variable_tree_space']

    def __init__(self, name, parent=None, shared_variable_tree_space=None):
        self.name = name
        self.parent = parent
        self.children = []
        # When we add nodes in a SharedVariableTreeSpace, then they need a reference to that space's variables
        self.shared_variable_tree_space = shared_variable_tree_space

        if self.shared_variable_tree_space is not None:
            self.shared_variable_tree_space.add_variable(self.identifier, None)

    def add_child(self, child_name, aggregation_function=None, value=None):
        if (aggregation_function is None and value is None) or (aggregation_function is not None and value is not None):
            raise ValueError("When adding a child node, either specify a value or an aggregation function. Adding a "
                             "value will make it a free parameter, and adding a function will make it calculated.")
        if aggregation_function is not None:
            new_node = CalculatedTreeNode(child_name, aggregation_function, self, self.shared_variable_tree_space)
        else:
            new_node = FreeParameterTreeNode(child_name, value, self, self.shared_variable_tree_space)

        self.children.append(new_node)
        return new_node

    @property
    def identifier(self):
        return f"node_value_{self.name}_{id(self)}"


class FreeParameterTreeNode(TreeNode):
    def __init__(self, name, value, parent=None, shared_variable_tree_space=None):
        super().__init__(name, parent, shared_variable_tree_space)
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class CalculatedTreeNode(TreeNode):
    __slots__ = ['aggregation_function']

    def __init__(self, name, aggregation_function=None, parent=None, shared_variable_tree_space=None):
        super().__init__(name, parent, shared_variable_tree_space)
        self.aggregation_function = aggregation_function

    @property
    def value(self):
        return self.aggregation_function(self.get_children_values())

    def get_children_values(self):
        return [child.value for child in self.children]


class SharedVariableTreeSpace:
    __slots__ = ['tree_seeds', 'variable_store']

    def __init__(self):
        self.tree_seeds = {}
        self.variable_store = {}

    def add_seed_node(self, name, aggregation_function):
        new_node = CalculatedTreeNode(name, aggregation_function)
        self.tree_seeds[name] = new_node
        return new_node

    def add_variable(self, key, value):
        if key in self.variable_store:
            raise KeyError(f"Key '{key}' already exists in the variable store.")
        self.variable_store[key] = value

    def update_variable(self, key, value):
        if key not in self.variable_store:
            raise KeyError(f"Key '{key}' does not exist in the variable store.")
        self.variable_store[key] = value

    def get_variable(self, key):
        if key not in self.variable_store:
            raise KeyError(f"Key '{key}' does not exist in the variable store.")
        return self.variable_store[key]
