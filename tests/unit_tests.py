import unittest, time
from aggregation_tree.trees import CalculatedTreeNode, SharedVariableTreeSpace, \
    SmartTreeSpace, ThreadedSmartTreeSpace


def multiply_list(input_list):
    result = 1
    for element in input_list:
        result *= element
    return result


def half_second_add(input_list):
    time.sleep(0.5)
    return sum(input_list)


class TestTreeNodes(unittest.TestCase):
    def test_simple_addition(self):
        top_node = CalculatedTreeNode("result", lambda x: sum(x))
        top_node.add_child("child_1", value=2)
        top_node.add_child("child_2", value=3)

        self.assertEqual(top_node.value, 5)

    def test_simple_multiplication(self):
        top_node = CalculatedTreeNode("result", multiply_list)

        top_node.add_child("child_1", value=10)
        top_node.add_child("child_2", value=20)
        top_node.add_child("child_3", value=0.2)

        self.assertEqual(top_node.value, 40)

    def test_three_layers(self):
        final_result = CalculatedTreeNode("result", lambda x: sum(x))

        second_layer_node_1 = final_result.add_child("sub_result_1", multiply_list)
        second_layer_node_2 = final_result.add_child("sub_result_2", lambda x: max(x))

        second_layer_node_1.add_child("multiply_1", value=2)
        second_layer_node_1.add_child("multiply_2", value=7)
        second_layer_node_1.add_child("multiply_3", value=3)

        second_layer_node_2.add_child("max_1", value=25)
        second_layer_node_2.add_child("max_2", value=24.4)

        # Answer should be 25 + 2*3*7 = 67
        self.assertEqual(final_result.value, 67)

    def test_adding_function_for_free_parameter_fails(self):
        main_node = CalculatedTreeNode("result", lambda x: sum(x))
        self.assertRaises(ValueError, lambda: main_node.add_child("child", lambda x: sum(x), 5.0))

    def test_adding_free_and_calculated_nodes(self):
        main_node = CalculatedTreeNode("result", lambda x: sum(x))
        main_node.add_child("free_param", value=20)
        sub_node = main_node.add_child("calculated_node", lambda x: max(x))
        sub_node.add_child("lowest_param", value=2)
        sub_node.add_child("lowest_param_2", value=5)

        self.assertEqual(main_node.value, 25)


class TestSharedVariableTreeSpace(unittest.TestCase):
    def test_adding_node_populates_storage(self):
        tree_space = SharedVariableTreeSpace()

        node = tree_space.add_seed_node("results", lambda x: sum(x))

        self.assertTrue(node.identifier in tree_space.shared_variable_store)
        self.assertEqual(None, tree_space.get_variable(node.identifier).underlying_value)

    def test_can_use_shared_variables_for_free_parameters(self):
        tree_space = SharedVariableTreeSpace()

        tree_space.add_variable("x", 20.0)
        tree_space.add_variable("y", 25.0)

        top_node = tree_space.add_seed_node("x+y", lambda x: sum(x))

        top_node.add_child("x_node", value=tree_space.get_variable("x"))
        top_node.add_child("y_node", value=tree_space.get_variable("y"))

        self.assertEqual(top_node.value, 45.0)

        tree_space.update_variable("x", 15.0)

        self.assertEqual(top_node.value, 40.0)

    def adding_two_variables_same_name_throws(self):
        tree_space = SharedVariableTreeSpace()

        tree_space.add_variable("x", 100)
        self.assertRaises(KeyError, lambda: tree_space.add_variable("x", 20))


class TestSmartTreeSpace(unittest.TestCase):
    def test_adding_shared_variable_appends_linked_nodes(self):
        tree_space = SmartTreeSpace()

        tree_space.add_variable("x", 100)
        seed = tree_space.add_seed_node("final_result", lambda l: sum(l))
        seed.add_child("x", value=tree_space.get_variable("x"))
        child_node = seed.add_child("x_plus_20", aggregation_function=lambda l: sum(l))
        child_node.add_child("constant", value=20)
        child_node.add_child("x", value=tree_space.get_variable("x"))

        self.assertEqual(seed.value, 220)
        self.assertEqual(len(tree_space.linked_nodes["x"]), 2)

        tree_space.update_variable("x", 120)
        self.assertEqual(seed.value, 260)

    def test_smart_tree_space_saves_time(self):
        tree_space = SmartTreeSpace()

        top_node = tree_space.add_seed_node("result", lambda x: sum(x))
        slow_node_1 = top_node.add_child("slow_node_1", half_second_add)
        slow_node_2 = top_node.add_child("slow_node_2", half_second_add)

        tree_space.add_variable("x", 10)
        tree_space.add_variable("y", 20)

        slow_node_1.add_child("x_node", value=tree_space.get_variable("x"))
        slow_node_2.add_child("y_node", value=tree_space.get_variable("y"))

        t0 = time.perf_counter()
        first_value = top_node.value
        self.assertTrue(time.perf_counter() - t0 > 1)
        self.assertEqual(first_value, 30)

        # Change just one variable
        tree_space.update_variable("x", 20)
        t0 = time.perf_counter()
        second_value = top_node.value
        self.assertTrue(0.5 < time.perf_counter() - t0 < 1)
        self.assertEqual(second_value, 40)


class TestThreadedSmartTreeSpace(unittest.TestCase):
    def test_threaded_smart_tree_space_saves_time(self):
        tree_space = ThreadedSmartTreeSpace()

        top_node = tree_space.add_seed_node("result", lambda x: sum(x))
        slow_node_1 = top_node.add_child("slow_node_1", half_second_add)
        slow_node_2 = top_node.add_child("slow_node_2", half_second_add)

        tree_space.add_variable("a", 20)
        tree_space.add_variable("b", 30)

        slow_node_1.add_child("a_node", value=tree_space.get_variable("a"))
        slow_node_2.add_child("b_node", value=tree_space.get_variable("b"))

        t0 = time.perf_counter()
        first_value = top_node.value
        tree_space.execute_threads()
        self.assertTrue(0.5 < time.perf_counter() - t0 < 1)
        self.assertEqual(first_value, 50)


if __name__ == '__main__':
    unittest.main()
