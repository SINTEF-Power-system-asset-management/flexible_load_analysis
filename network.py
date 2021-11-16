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

def list_nodes(dict_network): 
    """Lists all nodes of network.
    """
    return list(dict_network['bus']['bus_i'])


def list_children_of_node(node, dict_network):
    """Return child-nodes of a node in directed network.
    """
    dict_branch = dict_network['branch']
    x = []

    for i in range(len(dict_branch['fbus'])):
        if dict_branch['fbus'][i] == node:
            x.append(dict_branch['tbus'][i])
    return x


def add_node(dict_network, n_node, n_parent_node):
    """Adds a node and edge branching off a parent-node
    """
    dict_bus = dict_network['bus']

    # Adding the node to the dictionary of buses
    dict_bus['bus_i'] = np.append(dict_bus['bus_i'],n_node)
    dict_bus['type'] = np.append(dict_bus['type'],'1')
    dict_bus['Pd'] = np.append(dict_bus['Pd'],'0')
    dict_bus['Qd'] = np.append(dict_bus['Qd'],'0')
    dict_bus['Gs'] = np.append(dict_bus['Gs'],'0')
    dict_bus['Bs'] = np.append(dict_bus['Bs'],'0')
    dict_bus['area'] = np.append(dict_bus['area'],'1')
    dict_bus['Vm'] = np.append(dict_bus['Vm'],'0')
    dict_bus['Va'] = np.append(dict_bus['Va'],'0')
    dict_bus['baseKV'] = np.append(dict_bus['baseKV'],'0')
    dict_bus['zone'] = np.append(dict_bus['zone'],'1')
    dict_bus['Vmax'] = np.append(dict_bus['Vmax'],'1.04')
    dict_bus['Vmin'] = np.append(dict_bus['Vmin'],'0.96')

    dict_branch = dict_network['branch']

    # Adding the branch to the dictionary of branches
    dict_branch['fbus'] = np.append(dict_branch['fbus'], n_parent_node)
    dict_branch['tbus'] = np.append(dict_branch['tbus'], n_node)
    dict_branch['r'] = np.append(dict_branch['r'], '0')
    dict_branch['x'] = np.append(dict_branch['x'], '0')
    dict_branch['b'] = np.append(dict_branch['b'], '0')
    dict_branch['rateA'] = np.append(dict_branch['rateA'], '1000')
    dict_branch['rateB'] = np.append(dict_branch['rateB'], '1000')
    dict_branch['rateC'] = np.append(dict_branch['rateC'], '1000')
    dict_branch['ratio'] = np.append(dict_branch['ratio'], '0')
    dict_branch['angle'] = np.append(dict_branch['angle'], '0')
    dict_branch['status'] = np.append(dict_branch['status'], '1')
    return dict_network


def remove_node(dict_network, n_node):
    """Removes a node and connected edges from the network
    """
    dict_bus = dict_network['bus']

    # Find index of the node to be deleted
    node_index = np.where(dict_bus['bus_i'] == n_node)

    # Remove node name and all attributes from the bus dictionary
    dict_bus['bus_i'] = np.delete(dict_bus['bus_i'],node_index[0][0])
    dict_bus['type'] = np.delete(dict_bus['type'],node_index[0][0])
    dict_bus['Pd'] = np.delete(dict_bus['Pd'],node_index[0][0])
    dict_bus['Qd'] = np.delete(dict_bus['Qd'],node_index[0][0])
    dict_bus['Gs'] = np.delete(dict_bus['Gs'],node_index[0][0])
    dict_bus['Bs'] = np.delete(dict_bus['Bs'],node_index[0][0])
    dict_bus['area'] = np.delete(dict_bus['area'],node_index[0][0])
    dict_bus['Vm'] = np.delete(dict_bus['Vm'],node_index[0][0])
    dict_bus['Va'] = np.delete(dict_bus['Va'],node_index[0][0])
    dict_bus['baseKV'] = np.delete(dict_bus['baseKV'],node_index[0][0])
    dict_bus['zone'] = np.delete(dict_bus['zone'],node_index[0][0])
    dict_bus['Vmax'] = np.delete(dict_bus['Vmax'],node_index[0][0])
    dict_bus['Vmin'] = np.delete(dict_bus['Vmin'],node_index[0][0])


    dict_branch = dict_network['branch']

    # Find index / indices of branches that are connected to the node
    fbus_index = np.where(dict_branch['fbus'] == n_node)[0].tolist()
    tbus_index = np.where(dict_branch['tbus'] == n_node)[0].tolist()
    branch_index = fbus_index+tbus_index # indices of branches to delete

    # Delete all branches that are connected to the node
    for i in branch_index:
        dict_branch['fbus'] = np.delete(dict_branch['fbus'], i)
        dict_branch['tbus'] = np.delete(dict_branch['tbus'], i)
        dict_branch['r'] = np.delete(dict_branch['r'], i)
        dict_branch['x'] = np.delete(dict_branch['x'], i)
        dict_branch['b'] = np.delete(dict_branch['b'], i)
        dict_branch['rateA'] = np.delete(dict_branch['rateA'], i)
        dict_branch['rateB'] = np.delete(dict_branch['rateB'], i)
        dict_branch['rateC'] = np.delete(dict_branch['rateC'], i)
        dict_branch['ratio'] = np.delete(dict_branch['ratio'], i)
        dict_branch['angle'] = np.delete(dict_branch['angle'], i)
        dict_branch['status'] = np.delete(dict_branch['status'], i)
    return dict_network
