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
        return f"node_value_{self.name}_{hex(id(self))}"

    def __repr__(self):
        return f"{type(self).__name__}: {self.name}"


class FreeParameterTreeNode(TreeNode):
    def __init__(self, name, value, parent=None, shared_variable_tree_space=None):
        super().__init__(name, parent, shared_variable_tree_space)
        self._value = value

        if self.shared_variable_tree_space is not None:
            # Free parameters should have a value, so we update the shared variable store here
            self.shared_variable_tree_space.update_variable(self.identifier, self._value)

            # If the value is a shared variable, add this node to the variable's linked_nodes
            if isinstance(value, SharedVariable):
                self.shared_variable_tree_space.linked_nodes[value.name].append(self)

    @property
    def value(self):
        if isinstance(self._value, SharedVariable):
            return self._value.underlying_value
        return self._value


class CalculatedTreeNode(TreeNode):
    __slots__ = ['aggregation_function', 'stored_value']

    def __init__(self, name, aggregation_function=None, parent=None, shared_variable_tree_space=None):
        super().__init__(name, parent, shared_variable_tree_space)
        self.aggregation_function = aggregation_function
        self.stored_value = None

    @property
    def value(self):
        # If the value has not been calculated, we must calculate it first
        if self.stored_value is None:
            self.stored_value = self.aggregation_function(self.get_children_values())

        return self.stored_value

    def get_children_values(self):
        return [child.value for child in self.children]

    def mark_to_recalculate(self):
        current_node = self

        while current_node is not None and current_node.stored_value is not None:
            current_node.stored_value = None
            current_node = current_node.parent


class SharedVariable:
    """
    Since we can't refer to primitive types by reference, we wrap them here as shared variables.
    """
    __slots__ = ['name', 'underlying_value']

    def __init__(self, name, value):
        self.name = name
        self.underlying_value = value

    def __repr__(self):
        return f"{self.name}: {self.underlying_value} <{hex(id(self))}>"


class SharedVariableTreeSpace:
    __slots__ = ['tree_seeds', 'shared_variable_store', 'linked_nodes']

    def __init__(self):
        self.tree_seeds = {}
        self.shared_variable_store = {}
        self.linked_nodes = {}

    def add_seed_node(self, name, aggregation_function):
        new_node = CalculatedTreeNode(name, aggregation_function, shared_variable_tree_space=self)
        self.tree_seeds[name] = new_node
        return new_node

    def add_variable(self, key, value):
        if key in self.shared_variable_store:
            raise KeyError(f"Key '{key}' already exists in the variable store.")
        self.shared_variable_store[key] = SharedVariable(key, value)
        self.linked_nodes[key] = []

    def update_variable(self, key, value):
        if key not in self.shared_variable_store:
            raise KeyError(f"Key '{key}' does not exist in the variable store.")
        self.shared_variable_store[key].underlying_value = value

        # Determine which nodes to recalculate
        for node in self.linked_nodes[key]:
            node.parent.mark_to_recalculate()

    def get_variable(self, key):
        if key not in self.shared_variable_store:
            raise KeyError(f"Key '{key}' does not exist in the variable store.")
        return self.shared_variable_store[key]
