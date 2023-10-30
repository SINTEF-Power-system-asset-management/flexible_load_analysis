import unittest

from flexible_load_analysis.objects import radial_network_traversal as trav
from tests.init_test_data import load_test_loads_and_network

# TODO: Make test case allow for other network than test-network, i.e. make
# known correct test-outcomes be initalized by setUp and choice of dataset

class RadialTravelsalTestCase(unittest.TestCase):
    def __init__(self, methodName, *args, **kwargs) -> None:
        super().__init__(methodName)
        for key, val in kwargs.items():
            self.__setattr__(key, val)

    def setUp(self) -> None:
        d_loads, d_network = load_test_loads_and_network(single_radial=self.bool_single_radial)
        self.load_data = d_loads
        self.network_data = d_network
        if self.bool_single_radial:
            self.reference_node = None
        else:
            self.reference_node = "B1"

    def tearDown(self) -> None:
        self.load_data = None
        self.network_data = None

    def test_find_parent(self):
        known_child_parent_pairs = [
            ("B2", "B1"),
            ("B3", "B2"),
            ("B4", "B2"),
            ("B5", "B3"),
            ("B6", "B4"),
            ("B7", "B5"),
            ("B8", "B5"),
            ("B9", "B6"),
            ]
        for node, actual_parent in known_child_parent_pairs:
            found_parent = trav.find_parent(node, self.network_data, self.reference_node)
            self.assertEqual(found_parent, actual_parent, f"Node {node} got incorrect parent {found_parent}, expected {actual_parent}")

    def test_all_buses_below(self):
        known_node_below_arr_pairs = [
            ("B1", ["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9"]),
            ("B2", ["B3", "B4", "B5", "B6", "B7", "B8", "B9"]),
            ("B3", ["B5", "B7", "B8"]),
            ("B4", ["B6", "B9"]),
            ("B5", ["B7", "B8"]),
            ("B6", ["B9"]),
            ("B7", []),
            ("B8", []),
            ("B9", []),
        ]
        for node, actual_belows in known_node_below_arr_pairs:
            found_below = trav.all_buses_below(node, self.network_data, self.reference_node)
            self.assertCountEqual(found_below, actual_belows, f"Node {node} found incorrect nodes below {found_below}, expected {actual_belows}")

    def test_all_leaf_nodes_below(self):
        known_node_leaf_arr_pairs = [
            ("B1", ["B7", "B8", "B9"]),
            ("B2", ["B7", "B8", "B9"]),
            ("B3", ["B7", "B8"]),
            ("B4", ["B9"]),
            ("B5", ["B7", "B8"]),
            ("B6", ["B9"]),
            ("B7", []),
            ("B8", []),
            ("B9", []),
        ]
        for node, actual_leafs in known_node_leaf_arr_pairs:
            found_leafs = trav.all_leaf_nodes_below(node, self.network_data, self.reference_node)
            self.assertCountEqual(found_leafs, actual_leafs, f"Node {node} found incorrect leaf-nodes below {found_leafs}, expected {actual_leafs}")
        
    def test_all_leaf_nodes_in_radial(self):
        actual_leafs = ["B7", "B8", "B9"]
        found_leafs = trav.all_leaf_nodes_in_radial(self.network_data, self.reference_node)
        self.assertCountEqual(found_leafs, actual_leafs, f"Found incorrect leaf-nodes {found_leafs}, expected {actual_leafs}")

    def test_path_to_node(self):
        fnode_tnode_path_pairs = [
            (("B1", "B3"), ["B1", "B2", "B3"]),
            (("B1", "B7"), ["B1", "B2", "B3", "B5", "B7"]),
            (("B2", "B7"), ["B2", "B3", "B5", "B7"]),
            (("B7", "B1"), None),
            (("B1", "B9"), ["B1", "B2", "B4", "B6", "B9"]),
        ]
        for (from_node, to_node), known_path in fnode_tnode_path_pairs:
            found_path = trav.path_to_node(from_node, to_node, self.network_data, self.reference_node)
            self.assertEqual(found_path, known_path, f"Found incorrect path from {from_node} to {to_node}: {found_path}. Expected: {known_path}")

    def test_all_paths_from_node(self):
        fnode = "B1"
        known_paths_to_leafs = [
            ["B1", "B2", "B3", "B5", "B7"],
            ["B1", "B2", "B3", "B5", "B8"],
            ["B1", "B2", "B4", "B6", "B9"],
        ]
        found_paths_to_leafs = trav.all_paths_from_node(fnode, self.network_data, self.reference_node)
        self.assertCountEqual(found_paths_to_leafs, known_paths_to_leafs)


class SingleRadialCase(RadialTravelsalTestCase):
    def __init__(self, methodName) -> None:
        super().__init__(methodName, bool_single_radial=True)


class TwoRadialsCase(RadialTravelsalTestCase):
    def __init__(self, methodName) -> None:
        super().__init__(methodName, bool_single_radial=False)


test_cases = [SingleRadialCase, TwoRadialsCase]

def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    for test_class in test_cases:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    return suite
