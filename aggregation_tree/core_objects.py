class TreeNode:
    """
    A CalculatedTreeNode is essentially a tree object, since we branch off from this using the add_child() method.
    """
    __slots__ = ['name', 'parent', 'children', '_value']

    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.children = []

    def add_child(self, child_name, aggregation_function=None, value=None):
        if (aggregation_function is None and value is None) or (aggregation_function is not None and value is not None):
            raise ValueError("When adding a child node, either specify a value or an aggregation function. Adding a "
                             "value will make it a free parameter, and adding a function will make it calculated.")
        if aggregation_function is not None:
            new_node = CalculatedTreeNode(child_name, aggregation_function, self)
        else:
            new_node = FreeParameterTreeNode(child_name, value, self)

        self.children.append(new_node)
        return new_node


class FreeParameterTreeNode(TreeNode):
    def __init__(self, name, value, parent=None):
        super().__init__(name, parent)
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class CalculatedTreeNode(TreeNode):
    __slots__ = ['aggregation_function']

    def __init__(self, name, aggregation_function=None, parent=None):
        super().__init__(name, parent)
        self.aggregation_function = aggregation_function

    @property
    def value(self):
        if self.aggregation_function is None:
            return self._value
        return self.aggregation_function(self.get_children_values())

    def get_children_values(self):
        return [child.value for child in self.children]

