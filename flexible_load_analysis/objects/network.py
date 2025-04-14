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


### Conversions

def plot_network(dict_network, draw_figure=True, **plot_kwargs):
    """
    Convert to NetworkX and plot the topology
    """
    nx_network = convert_network_dictionary_to_graph(dict_network)
    if "ax" not in plot_kwargs: plt.subplot(111)
    pos = nx.kamada_kawai_layout(nx_network)

    node_voltage_lvls = dict_network["bus"]["BASE_KV"].astype(np.float64)

    nx_edges = np.array(list(nx_network.edges))
    num_edges = nx_edges.shape[0]
    inactive_idxs = (dict_network["branch"]["BR_STATUS"].astype(np.float64) == 0)
    inactive_edges = np.stack((
            dict_network["branch"]["F_BUS"],
            dict_network["branch"]["T_BUS"]),
            axis=1)[inactive_idxs]
    inactive_nx_idxs = np.zeros((num_edges), dtype=bool)
    if inactive_edges.any(): inactive_nx_idxs = ((nx_edges == inactive_edges) | (nx_edges == np.flip(inactive_edges, axis=1))).all(axis=1)

    edge_status = np.array(["#006600"] * num_edges)
    edge_status[inactive_nx_idxs] = "#660000"

    nx.draw(nx_network, pos=pos, with_labels=True, font_weight='bold', cmap="Set1" ,node_color=node_voltage_lvls, edge_color=edge_status, **plot_kwargs)
    if draw_figure: plt.show()
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



### Members

def list_nodes(dict_network): 
    """Lists all nodes of network.
    """
    return list(dict_network['bus']['BUS_I'])


def list_children_of_node(node, dict_network):
    """Return child-nodes of a node in directed network.
    """
    warnings.warn(f"Directed networks are no longer supported. Please refer to {list_currently_connected_nodes}", DeprecationWarning)

    dict_branch = dict_network['branch']
    x = []

    for i in range(len(dict_branch['F_BUS'])):
        if dict_branch['F_BUS'][i] == node:
            x.append(dict_branch['T_BUS'][i])
    return x


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
    return (str(n_node) in g_network["bus"]["BUS_I"].astype(str))



### Modification

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
    dict_bus['LG'] = np.append(dict_bus['LG'], '0')  
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
    bus_indeces_to_keep = np.where(~(dict_bus['BUS_I'] == n_node))

    # Remove node name and all attributes from the bus dictionary
    for column in dict_bus:
        dict_bus[column] = dict_bus[column][bus_indeces_to_keep]

    dict_branch = dict_network['branch']
    # Find index / indices of branches that are connected to the node
    FBUS_indices = (dict_branch['F_BUS'] == n_node)
    TBUS_indices = (dict_branch['T_BUS'] == n_node)
    branch_indices_to_keep = np.where(~(FBUS_indices | TBUS_indices))

    # Delete all branches that are connected to the node
    for column in dict_branch:
        dict_branch[column] = dict_branch[column][branch_indices_to_keep]
    return dict_network


def set_voltage_level(str_bus, new_base_kV, dict_network):
    bus_idx = np.where(dict_network["bus"]["BUS_I"] == str_bus)
    dict_network["bus"]["BASE_KV"][bus_idx] = new_base_kV
    return dict_network


def set_line_impedance_of_branch(f_bus, t_bus, new_impedance, dict_network):
    branch_idx = find_branch_index(f_bus, t_bus, dict_network)
    dict_network["branch"]["BR_R"][branch_idx] = np.real(new_impedance)
    dict_network["branch"]["BR_X"][branch_idx] = np.imag(new_impedance)
    return dict_network


def set_branch_tap(f_bus, t_bus, new_tap, dict_network):
    branch_idx = find_branch_index(f_bus, t_bus, dict_network)
    dict_network["branch"]["TAP"][branch_idx] = new_tap
    return dict_network


def convert_trafo_branch_to_equivalent_impedance(f_bus, t_bus, dict_network):
    #TODO: Source?
    branch_idx = find_branch_index(f_bus, t_bus, dict_network)
    N1overN2 = dict_network["branch"]["TAP"].astype(np.float64)[branch_idx]
    old_impedance = get_impedance_of_branch(f_bus, t_bus, dict_network)
    new_impedance = old_impedance * N1overN2**2
    set_line_impedance_of_branch(f_bus, t_bus, new_impedance, dict_network)
    set_branch_tap(f_bus, t_bus, 0, dict_network)
    # TODO: Deal with shift?
    pass



### Accessing

def voltage_for_node_id(node, d_network):
    if node is None: return np.nan
    node_idx = np.where(d_network["bus"]["BUS_I"] == node)
    return d_network["bus"]["BASE_KV"][node_idx].astype(np.float64)


def is_reference_bus(str_bus, dict_network):
    bus_idx = np.where(dict_network["bus"]["BUS_I"].astype(str) == str_bus)
    return dict_network["bus"]["BUS_TYPE"][bus_idx].astype(int) == 3


def find_branch_index(bus1, bus2, dict_network):
    branch_mask =   ((dict_network["branch"]["F_BUS"] == bus1) & (dict_network["branch"]["T_BUS"] == bus2)) | \
                    ((dict_network["branch"]["F_BUS"] == bus2) & (dict_network["branch"]["T_BUS"] == bus1))
    branch_idx = np.where(branch_mask)[0]
    assert branch_idx.size == 1 # Or else there exists multiple branches between buses 1 and 2
    return branch_idx


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


def get_impedance_of_branch(f_bus, t_bus, dict_network):
    pairs = list(zip(dict_network["branch"]["F_BUS"], dict_network["branch"]["T_BUS"]))
    for i in range(len(pairs)):
        if pairs[i] == (f_bus, t_bus) or pairs[i] == (t_bus, f_bus):
            return dict_network["branch"]["BR_R"].astype(np.float64)[i] + 1j*dict_network["branch"]["BR_X"].astype(np.float64)[i]
    else:
        raise(Exception(f"Branch {(f_bus, t_bus)} not found in network"))


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


def get_all_transformer_bus_pairs(dict_network):
    trafo_branches = np.where(dict_network["branch"]["TAP"].astype(np.float64) != 0)
    return list(zip(dict_network["branch"]["F_BUS"][trafo_branches], dict_network["branch"]["T_BUS"][trafo_branches]))
