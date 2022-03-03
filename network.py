"""Module for network-related operations.

Notes
----------
The network is stored as a dictionary of dictionaries, keyed by 
MATPOWER-struct names and columns in these structs.

Beware that rates in MATPOWER are given in MegaWatt, while
the load-timeseries are implicitly in KiloWatt.

The point of isolating network-related operations is such that the
chosen graph-representation may be changed at will, without needing to
change code outside this module.

"""
import pandapower as pp
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import utilities


def plot_network(dict_network):
    """
    Convert to NetworkX and plot the topology
    """
    nx_network = convert_network_dictionary_to_graph(dict_network)
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
    nx_network.add_nodes_from(dict_network["bus"]["BUS_I"])
    nx_network.add_edges_from(
        np.stack((
            dict_network["branch"]["F_BUS"],
            dict_network["branch"]["T_BUS"]),
            axis=1))
    # plot_network(nx_network)

    #print("Successfully converted to internal graph-representation")
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
    return list(dict_network['bus']['BUS_I'])


def list_children_of_node(node, dict_network):
    """Return child-nodes of a node in directed network.
    """
    dict_branch = dict_network['branch']
    x = []

    for i in range(len(dict_branch['F_BUS'])):
        if dict_branch['F_BUS'][i] == node:
            x.append(dict_branch['T_BUS'][i])
    return x


def node_in_network(n_node, g_network):
    return (n_node in g_network["bus"]["BUS_I"])


def add_node(dict_network, n_node, n_parent_node):
    """Adds a node and edge branching off a parent-node
        For the added node and branch, standard values are assumed.
        These standard values effectively assumes no impedance and high 
        capacity of the new lines.
    """
    dict_bus = dict_network['bus']

    # Adding the node to the dictionary of buses
    dict_bus['BUS_I'] = np.append(dict_bus['BUS_I'],n_node)
    dict_bus['BUS_TYPE'] = np.append(dict_bus['BUS_TYPE'],'1')
    dict_bus['PD'] = np.append(dict_bus['PD'],'0')
    dict_bus['QD'] = np.append(dict_bus['QD'],'0')
    dict_bus['GS'] = np.append(dict_bus['GS'],'0')
    dict_bus['BS'] = np.append(dict_bus['BS'],'0')
    dict_bus['BUS_AREA'] = np.append(dict_bus['BUS_AREA'],'1')
    dict_bus['VM'] = np.append(dict_bus['VM'],'0')
    dict_bus['VA'] = np.append(dict_bus['VA'],'0')
    dict_bus['BASE_KV'] = np.append(dict_bus['BASE_KV'],'0')
    dict_bus['ZONE'] = np.append(dict_bus['ZONE'],'1')
    dict_bus['VMAX'] = np.append(dict_bus['VMAX'],'1.04')
    dict_bus['VMIN'] = np.append(dict_bus['VMIN'],'0.96')

    dict_branch = dict_network['branch']

    # Adding the branch to the dictionary of branches
    dict_branch['F_BUS'] = np.append(dict_branch['F_BUS'], n_parent_node)
    dict_branch['T_BUS'] = np.append(dict_branch['T_BUS'], n_node)
    dict_branch['BR_R'] = np.append(dict_branch['BR_R'], '0')
    dict_branch['BR_X'] = np.append(dict_branch['BR_X'], '0')
    dict_branch['BR_B'] = np.append(dict_branch['BR_B'], '0')
    dict_branch['RATE_A'] = np.append(dict_branch['RATE_A'], '1000')
    dict_branch['RATE_B'] = np.append(dict_branch['RATE_B'], '1000')
    dict_branch['RATE_C'] = np.append(dict_branch['RATE_C'], '1000')
    # dict_branch['ratio'] = np.append(dict_branch['ratio'], '0')
    # dict_branch['angle'] = np.append(dict_branch['angle'], '0')
    dict_branch['BR_STATUS'] = np.append(dict_branch['BR_STATUS'], '1')
    return dict_network


def remove_node(dict_network, n_node):
    """Removes a node and connected edges from the network
    """
    dict_bus = dict_network['bus']

    # Find index of the node to be deleted
    node_index = np.where(dict_bus['BUS_I'] == n_node)

    # Remove node name and all attributes from the bus dictionary
    dict_bus['BUS_I'] = np.delete(dict_bus['BUS_I'],node_index[0][0])
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
    FBUS_Index = np.where(dict_branch['F_BUS'] == n_node)[0].tolist()
    TBUS_Index = np.where(dict_branch['T_BUS'] == n_node)[0].tolist()
    branch_index = FBUS_Index+TBUS_Index # indices of branches to delete

    # Delete all branches that are connected to the node
    for i in branch_index:
        dict_branch['FBUS'] = np.delete(dict_branch['FBUS'], i)
        dict_branch['TBUS'] = np.delete(dict_branch['TBUS'], i)
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


def input_until_node_in_network_appears(dict_network):
    bool_ID_in_network = False
    while not bool_ID_in_network:
        print("Please select a node")
        str_ID = utilities.input_until_expected_type_appears(str)
        if node_in_network(str_ID, dict_network):
            bool_ID_in_network = True
        else:
            print("Could not find", str_ID, "in network, try again!")
    return str_ID