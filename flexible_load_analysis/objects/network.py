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
import warnings

import pandapower as pp
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

from .. import utilities


def plot_network(dict_network):
    """
    Convert to NetworkX and plot the topology
    """
    nx_network = convert_network_dictionary_to_graph(dict_network)
    plt.subplot(111)
    pos = nx.kamada_kawai_layout(nx_network)

    node_voltage_lvls = dict_network["bus"]["BASE_KV"].astype(np.float64)

    nx_edges = list(nx_network.edges)
    not_active_inds = np.where(dict_network["branch"]["BR_STATUS"] == "0")[0]
    not_active_edges = np.stack((
            dict_network["branch"]["F_BUS"],
            dict_network["branch"]["T_BUS"]),
            axis=1)[not_active_inds]
    not_active_edges_mp = np.array([str((a[0], a[1])) for a in not_active_edges])
    not_active_edges_nx = np.array([str(tup) for tup in nx_edges])
    not_active_idx = np.in1d(not_active_edges_nx, not_active_edges_mp).nonzero()[0]
    
    edge_status = np.array(["#006600"] * len(nx_edges))
    edge_status[not_active_idx] = "#660000"
    edge_status = list(edge_status)

    nx.draw(nx_network, pos=pos, with_labels=True, font_weight='bold', cmap="Set1" ,node_color=node_voltage_lvls, edge_color=edge_status)
    plt.show()
    return


def convert_network_dictionary_to_graph(dict_network, directed=False): # NetworkX
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
    if directed:
        nx_network = nx.DiGraph()
    else:
        nx_network = nx.Graph()
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
    warnings.warn(f"Directed networks are no longer supported. Please refer to {list_currently_connected_nodes} or {all_buses_below}", DeprecationWarning)

    dict_branch = dict_network['branch']
    x = []

    for i in range(len(dict_branch['F_BUS'])):
        if dict_branch['F_BUS'][i] == node:
            x.append(dict_branch['T_BUS'][i])
    return x


def find_parent(node, dict_network, reference_node=None):
    """Finds the parent of ```node''' in a radial network, that being the node in the network which leads from ```node''' towards the ```reference_node'''.
    """
    if reference_node is None: reference_node = get_reference_bus_ID(dict_network)

    node_currently_exploring = None
    explored = []
    queue = [reference_node]
    if node == reference_node:
        parent = None
    else:
        # Bredde-først-søk for å finne node som leder fra reference til agg_node
        while queue:
            node_currently_exploring = queue.pop()
            new_children = list_currently_connected_nodes(node_currently_exploring, dict_network)
            if node in new_children:
                # noden vi undersøker er har noden vi ønsker å finne som barn <=> noden vi undersøker er foreldren
                parent = node_currently_exploring
                break
            explored.append(node_currently_exploring)
            # Kun søk noder med lavere eller lik spenning
            for n in new_children:
                if (n not in explored) and (voltage_for_node_id(n, dict_network) <= voltage_for_node_id(node_currently_exploring, dict_network)):
                    queue.append(n)
        else:
            # Kommer hit dersom vi aldri break-er fra while
            print(f"Unable to find route from [{reference_node}] to [{node}]")
            return np.empty((0))

    return parent  


def all_buses_below(node, dict_network, reference_node=None):
    """Finds all bus-IDs which are below ```node''', meaning they are further away from ```reference_node'''. Warning: Result includes input ```node'''.
    """
    # OBS: Resultatet inkluderer noden vi aggregerer fra.

    if reference_node is None: reference_node = get_reference_bus_ID(dict_network)
    parent_node = find_parent(node, dict_network, reference_node)

    node_currently_exploring = node
    # Vi skal bare utforske nedover
    queue = [node for node in list_currently_connected_nodes(node, dict_network) if node != parent_node]
    explored = [node]
    # BFS hvor man bruker [list_currently_connected(cur_parent) - [cur_parent]] som queue
    while queue:
        node_currently_exploring = queue.pop()
        explored.append(node_currently_exploring)
        new_children = list_currently_connected_nodes(node_currently_exploring, dict_network)
        # Kun søk noder med lavere eller lik spenning
        for n in new_children:
            if (n not in explored) and (voltage_for_node_id(n, dict_network) <= voltage_for_node_id(node_currently_exploring, dict_network)):
                queue.append(n)
    return explored


def all_loads_below(node, dict_network, dict_loads, reference_node=None):
    """Finds all bus-IDs which have load-timeseries and are further away from ```reference_node''' than input ```node'''
    """
    if reference_node is None: reference_node = get_reference_bus_ID(dict_network)
    buses_below = all_buses_below(node, dict_network, reference_node)
    loads_below = [bus for bus in buses_below if bus in dict_loads]
    return loads_below


def list_currently_connected_nodes(node, dict_network):
    """Returns IDs of all nodes connected to specified node. Ignores nodes connected by non-active branch.
    """
    dict_branch = dict_network['branch']
    x = []

    for i in range(len(dict_branch['F_BUS'])):
        if dict_branch['F_BUS'][i] == node and dict_branch["BR_STATUS"][i] == "1":
            x.append(dict_branch['T_BUS'][i])
        elif dict_branch['T_BUS'][i] == node and dict_branch["BR_STATUS"][i] == "1":
            x.append(dict_branch['F_BUS'][i])
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
    dict_branch['TAP'] = np.append(dict_branch['TAP'], '1')
    dict_branch['SHIFT'] = np.append(dict_branch['SHIFT'], '0')
    dict_branch['BR_STATUS'] = np.append(dict_branch['BR_STATUS'], '1')
    dict_branch['ANGMIN'] = np.append(dict_branch['ANGMIN'], '0')
    dict_branch['ANGMAX'] = np.append(dict_branch['ANGMAX'], '0')
    dict_branch['PF'] = np.append(dict_branch['PF'], '0')
    dict_branch['QF'] = np.append(dict_branch['QF'], '0')
    dict_branch['PT'] = np.append(dict_branch['PT'], '0')
    dict_branch['QT'] = np.append(dict_branch['QT'], '0')
    dict_branch['MU_SF'] = np.append(dict_branch['MU_SF'], '0')
    dict_branch['MU_ST'] = np.append(dict_branch['MU_ST'], '0')
    dict_branch['MU_ANGMIN'] = np.append(dict_branch['MU_ANGMIN'], '0')
    dict_branch['MU_ANGMAX'] = np.append(dict_branch['MU_ANGMAX'], '0')
    
    return dict_network


def remove_node(dict_network, n_node):
    """Removes a node and connected edges from the network
    """
    dict_bus = dict_network['bus']

    # Find index of the node to be deleted
    node_index = np.where(dict_bus['BUS_I'] == n_node)

    # Remove node name and all attributes from the bus dictionary
    dict_bus['BUS_I'] = np.delete(dict_bus['BUS_I'],node_index[0][0])
    dict_bus['BUS_TYPE'] = np.delete(dict_bus['BUS_TYPE'],node_index[0][0])
    dict_bus['PD'] = np.delete(dict_bus['PD'],node_index[0][0])
    dict_bus['QD'] = np.delete(dict_bus['QD'],node_index[0][0])
    dict_bus['GS'] = np.delete(dict_bus['GS'],node_index[0][0])
    dict_bus['BS'] = np.delete(dict_bus['BS'],node_index[0][0])
    dict_bus['BUS_AREA'] = np.delete(dict_bus['BUS_AREA'],node_index[0][0])
    dict_bus['VM'] = np.delete(dict_bus['VM'],node_index[0][0])
    dict_bus['VA'] = np.delete(dict_bus['VA'],node_index[0][0])
    dict_bus['BASE_KV'] = np.delete(dict_bus['BASE_KV'],node_index[0][0])
    dict_bus['ZONE'] = np.delete(dict_bus['ZONE'],node_index[0][0])
    dict_bus['VMAX'] = np.delete(dict_bus['VMAX'],node_index[0][0])
    dict_bus['VMIN'] = np.delete(dict_bus['VMIN'],node_index[0][0])


    dict_branch = dict_network['branch']

    # Find index / indices of branches that are connected to the node
    FBUS_Index = np.where(dict_branch['F_BUS'] == n_node)[0].tolist()
    TBUS_Index = np.where(dict_branch['T_BUS'] == n_node)[0].tolist()
    branch_index = FBUS_Index+TBUS_Index # indices of branches to delete

    # Delete all branches that are connected to the node
    for i in branch_index:
        dict_branch['F_BUS'] = np.delete(dict_branch['F_BUS'], i)
        dict_branch['T_BUS'] = np.delete(dict_branch['T_BUS'], i)
        dict_branch['BR_R'] = np.delete(dict_branch['BR_R'], i)
        dict_branch['BR_X'] = np.delete(dict_branch['BR_X'], i)
        dict_branch['BR_B'] = np.delete(dict_branch['BR_B'], i)
        dict_branch['RATE_A'] = np.delete(dict_branch['RATE_A'], i)
        dict_branch['RATE_B'] = np.delete(dict_branch['RATE_B'], i)
        dict_branch['RATE_C'] = np.delete(dict_branch['RATE_C'], i)
        dict_branch['TAP'] = np.delete(dict_branch['TAP'], i)
        dict_branch['SHIFT'] = np.delete(dict_branch['SHIFT'], i)
        dict_branch['BR_STATUS'] = np.delete(dict_branch['BR_STATUS'], i)
        dict_branch['ANGMIN'] = np.delete(dict_branch['ANGMIN'], i)
        dict_branch['ANGMAX'] = np.delete(dict_branch['ANGMAX'], i)
        dict_branch['PF'] = np.delete(dict_branch['PF'], i)
        dict_branch['QF'] = np.delete(dict_branch['QF'], i)
        dict_branch['PT'] = np.delete(dict_branch['PT'], i)
        dict_branch['QT'] = np.delete(dict_branch['QT'], i)
        dict_branch['MU_SF'] = np.delete(dict_branch['MU_SF'], i)
        dict_branch['MU_ST'] = np.delete(dict_branch['MU_ST'], i)
        dict_branch['MU_ANGMIN'] = np.delete(dict_branch['MU_ANGMIN'], i)
        dict_branch['MU_ANGMAX'] = np.delete(dict_branch['MU_ANGMAX'], i)
    return dict_network


def voltage_for_node_id(node, d_network):
    node_idx = np.where(d_network["bus"]["BUS_I"] == node)
    return d_network["bus"]["BASE_KV"][node_idx]


def get_reference_bus_idx(dict_network):
    ref_bus_idx = np.where(dict_network["bus"]["BUS_TYPE"].astype(int) == 3)[0]
    if ref_bus_idx.shape[0] > 1:
        raise Exception("Found multiple reference buses")
    elif ref_bus_idx.shape[0] < 1:
        raise Exception("Found no reference bus")
    else: return ref_bus_idx[0]

def get_reference_bus_ID(dict_network):
    idx = get_reference_bus_idx(dict_network)
    return dict_network["bus"]["BUS_I"][idx]


def get_reference_bus_voltage(dict_network):
    ref_bus_idx = get_reference_bus_idx(dict_network)
    return float(dict_network["bus"]["BASE_KV"][ref_bus_idx])


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
