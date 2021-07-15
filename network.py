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
    nx_network = nx.Graph()
    # Todo: Add color based on voltage-level.
    nx_network.add_nodes_from(dict_network["bus"]["bus_i"])
    nx_network.add_edges_from(
        np.stack((
            dict_network["branch"]["fbus"],
            dict_network["branch"]["tbus"]),
            axis=1))
    # plt.subplot(111)
    #nx.draw(nx_network, with_labels=True, font_weight='bold')
    plt.show()
    return nx_network
