import unittest

from flexible_load_analysis.objects import radial_network_traversal as trav
from .init_test_data import load_test_loads_and_network
from flexible_load_analysis.objects.network import plot_network

class RadialTravelsalTestCase(unittest.TestCase):
    def setUp(self) -> None:
        d_loads, d_network = load_test_loads_and_network(single_radial=True)
        self.load_data = d_loads
        self.network_data = d_network

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
            found_parent = trav.find_parent(node, self.network_data)
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
            found_below = trav.all_buses_below(node, self.network_data)
            self.assertCountEqual(found_below, actual_belows, f"Node {node} found incorrect nodes below {found_below}, expected {actual_belows}")

    def test_all_leaf_nodes(self):
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
            found_below = trav.all_leaf_nodes_below(node, self.network_data)
            self.assertCountEqual(found_below, actual_leafs, f"Node {node} found incorrect leaf-nodes below {found_below}, expected {actual_leafs}")

        


suite = unittest.TestLoader().loadTestsFromTestCase(RadialTravelsalTestCase)
