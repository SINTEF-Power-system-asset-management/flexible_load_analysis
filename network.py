"""Module for network-related operations.

Notes
----------
The point of isolating network-related operations is such that the
chosen graph-representation may be changed at will, without needing to
change code outside this module.

"""
import pandapower as pp
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


def convert_network_dictionary_to_graph(dict_network): # NetworkX
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
    # plot_network(nx_network)

    print("Successfully converted to internal graph-representation")
    return nx_network


def convert_network_dictionary_to_pp(dict_network):
    """Function for converting MATPOWER-formatted array to Pandapower-net
    
    Parameters
    ----------
    dict_network : dict
        Dictionary of MATPOWER-formatted dictionaries, keyed by column.

    Returns
    ----------
    pp_network : PandaPower.attrdict()
        PandaPower-formatted network.

    Notes
    ----------
    - Uses pypower-format as intermediate format.
    - dict_network is keyed by column name, while pypower uses pure arrays.
    """
    ppc = {}
    for filename in dict_network:
        list_columns = [dict_network[filename][key] for key in dict_network[filename]]
        tup_columns = tuple(list_columns)
        ppc[filename] = (np.column_stack(tup_columns)).astype(np.float64)
    ppc["baseMVA"] = 125    # Hard-coded, needs flexibility
    pp_network = pp.converter.from_ppc(ppc, f_hz=50, validate_conversion=False)
    print("Successfully converted MATPOWER-formatted array to pandapower format")
    return pp_network

def list_nodes(pp_network): 
    """Lists all nodes of network.
    """
    return list(dict_network['bus']['bus_i'])


def list_children_of_node(node, pp_network):
    """Return child-nodes of a node in directed network.
    """
    dict_branch = dict_network['branch']
    x = []

    for i in range(len(dict_branch['fbus'])):
        if dict_branch['fbus'][i] == node:
            x.append(dict_branch['tbus'][i])
    return x


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
