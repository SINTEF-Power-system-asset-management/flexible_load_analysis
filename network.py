"""Module for network-related operations.

Notes
----------
The point of isolating network-related operations is such that the
chosen graph-representation may be changed at will, without needing to
change code outside this module.

"""
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


def plot_network(nx_network):
    """Graphically represents the topology
    """
    plt.subplot(111)
    nx.draw(nx_network, with_labels=True, font_weight='bold')
    plt.show()
    return

def convert_network_dictionary_to_graph(dict_network):
    """Function for converting MATPOWER-formatted array to NetworkX-graph

    Parameters
    ----------
    dict_network : dict
        Dictionary of MATPOWER-formatted dictionaries, keyed by column.

    Returns
    ----------
    nx_network : nx.Graph()
        Graph representation of network.
    """
    print("Converting MATPOWER-network to NetworkX...")
    nx_network = nx.DiGraph()
    nx_network.add_nodes_from(dict_network["bus"]["bus_i"])
    nx_network.add_edges_from(
        np.stack((
            dict_network["branch"]["fbus"],
            dict_network["branch"]["tbus"]),
            axis=1))
    #plot_network(nx_network)

    print("Successfully converted to internal graph-representation")
    return nx_network

def list_nodes(g_network):
    """Lists all nodes of network.
    """
    return list(nx.nodes(g_network))

def list_children_of_node(node, g_network):
    """Return child-nodes of a node in directed network.
    """
    return list(g_network.successors(node))
    
def add_node(g_network, n_node, n_parent_node):
    """Adds a node and edge branching off a parent-node
    """
    g_network.add_node(n_node)
    g_network.add_edge(n_parent_node, n_node)
    return g_network

def remove_node(g_network, n_node):
    """Removes a node and connected edges from the network
    """
    g_network.remove_node(n_node)
    return g_network