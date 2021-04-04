import unittest
from aggregation_tree.core_objects import CalculatedTreeNode


class TestAggregationTree(unittest.TestCase):
    def test_simple_addition(self):
        top_node = CalculatedTreeNode("result", lambda x: sum(x))
        top_node.add_child("child_1", value=2)
        top_node.add_child("child_2", value=3)

        self.assertEqual(top_node.value, 5)

    @staticmethod
    def multiply_list(input_list):
        result = 1
        for element in input_list:
            result *= element
        return result

    def test_simple_multiplication(self):
        top_node = CalculatedTreeNode("result", self.multiply_list)

        top_node.add_child("child_1", value=10)
        top_node.add_child("child_2", value=20)
        top_node.add_child("child_3", value=0.2)

        self.assertEqual(top_node.value, 40)

    def test_three_layers(self):
        final_result = CalculatedTreeNode("result", lambda x: sum(x))

        second_layer_node_1 = final_result.add_child("sub_result_1", self.multiply_list)
        second_layer_node_2 = final_result.add_child("sub_result_2", lambda x: max(x))

        second_layer_node_1.add_child("multiply_1", value=2)
        second_layer_node_1.add_child("multiply_2", value=7)
        second_layer_node_1.add_child("multiply_3", value=3)

        second_layer_node_2.add_child("max_1", value=25)
        second_layer_node_2.add_child("max_2", value=24.4)

        # Answer should be 25 + 2*3*7 = 67
        self.assertEqual(final_result.value, 67)


if __name__ == '__main__':
    unittest.main()
