class TreeNode:
    __slots__ = ['id', 'parent', 'children', '_value', 'aggregation_function']

    def __init__(self, name, aggregation_function=None, value=None, parent=None):
        self.id = name
        self.parent = parent
        self.aggregation_function = aggregation_function
        if aggregation_function is None:
            assert(value is not None)
        self._value = value
        self.children = []

    def add_child(self, child_id):
        self.children.append(TreeNode(child_id, self))

    @property
    def value(self):
        if self.aggregation_function is None:
            return self._value
        return self.aggregation_function(self.get_children_values())

    def get_children_values(self):
        return [child.value for child in self.children]

    @value.setter
    def value(self, value):
        self._value = value
