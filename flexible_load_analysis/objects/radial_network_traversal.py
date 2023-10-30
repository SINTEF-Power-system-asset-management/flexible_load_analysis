"""
Module for performing traversal and search of an assumed radially operated network.
This means the network has a well-defined reference node and that node voltage levels decrease going
down the branches of the network.

Module does not depend on the internal representation of said network, as long as the network-module provides
necessary interface.
"""

from .network import get_reference_bus_ID, list_currently_connected_nodes, voltage_for_node_id, list_nodes, get_impedance_of_branch



def find_prev_and_next_nodes(n_network, reference_node=None):
    """Makes dictionaries of 'prev_node' and 'next_node' (list) in network, taking different voltage levels into account.
    Beware: Returned dictionaries only contains keys for nodes which a path to was found.
    Meaning: If a node is not in the returned dictionary then it means there was no path found from ref_node to that node.
    """
    if reference_node is None: reference_node = get_reference_bus_ID(n_network)
    prev_node = {}
    prev_node[reference_node] = None
    queue = [reference_node]
    explored = []
    while queue:
        node_currently_exploring = queue.pop(0)
        connected_nodes = list_currently_connected_nodes(node_currently_exploring, n_network)
        explored.append(node_currently_exploring)
        # Kun søk noder med lavere eller lik spenning
        for n in connected_nodes:
            if (n not in explored) and (voltage_for_node_id(n, n_network) <= voltage_for_node_id(node_currently_exploring, n_network)):
                queue.append(n)
                prev_node[n] = node_currently_exploring
    
    next_node = {}
    for node, prev in prev_node.items():
        if prev in next_node:
            next_node[prev].append(node) 
        else: 
            next_node[prev] = [node]
    return prev_node, next_node


def find_parent(node, n_network, reference_node=None):
    """Finds the parent of ```node''' in a radial network, that being the node in the network which leads from ```node''' towards the ```reference_node'''.
    """
    if reference_node is None: reference_node = get_reference_bus_ID(n_network)
    prevs, _ = find_prev_and_next_nodes(n_network, reference_node)
    if node not in prevs:
        raise(Exception(f"Did not find path from {reference_node} to {node}"))
    else: 
        parent = prevs[node]
    return parent  


def all_buses_below(node, n_network, reference_node=None):
    """Finds all bus-IDs which are below ```node''', meaning they are further away from ```reference_node'''.
    
    Notes:
    ----------
    ```node''' is not part of the returned list. I.e. ```node''' is not further away from itself.
    """

    if reference_node is None: reference_node = get_reference_bus_ID(n_network)
    _, nexts = find_prev_and_next_nodes(n_network, reference_node)

    def _nodes_below(node, nexts):
        nodes_below_here = []
        for child in nexts.get(node, []):
            nodes_below_here += [child]
            nodes_below_here += _nodes_below(child, nexts)
        return nodes_below_here
    
    below = _nodes_below(node, nexts)
    return below


def all_loads_below(node, n_network, dict_loads, reference_node=None):
    """Finds all bus-IDs which have load-timeseries and are further away from ```reference_node''' than input ```node'''
    """
    if reference_node is None: reference_node = get_reference_bus_ID(n_network)
    buses_below = all_buses_below(node, n_network, reference_node)
    loads_below = [bus for bus in buses_below if bus in dict_loads]
    return loads_below


def all_leaf_nodes_below(node, n_network, reference_node=None):
    """Finds all bus-IDs below ```node''' which have no children.
    """

    if reference_node is None: reference_node = get_reference_bus_ID(n_network)
    # Does not use nexts from prev_next since this does not include nodes with no children
    _, nexts = find_prev_and_next_nodes(n_network)
    all_below = all_buses_below(node, n_network, reference_node)
    childless = []
    for n in all_below:
        if n not in nexts: childless.append(n)
    return childless


def path_to_node(from_node, to_node, n_network, reference_node=None):
    """Finds the path (list of nodes) between ```from_node''' and ```to_node'''. Output list includes both endpoints
    """
    if reference_node is None: reference_node = get_reference_bus_ID(n_network)
    prevs, _ = find_prev_and_next_nodes(n_network, reference_node)
    parent = from_node
    path = [parent]
    while parent in prevs:
        parent = prevs[parent]
        path.append(parent)
        if parent == to_node:
            break
    else:
        raise(Exception(f"Did not find path from {from_node} to {to_node}"))
    return path


def all_paths_from_node(from_node, n_network, reference_node=None):
    """Gives all paths (list of nodes) from ```from_node''' to a leaf node of the radial network.
    """
    if reference_node is None: reference_node = get_reference_bus_ID(n_network)

    all_endpoints = all_leaf_nodes_below(from_node, n_network, reference_node)
    all_paths = []
    for to_node in all_endpoints:
        all_paths.append(path_to_node(from_node, to_node, n_network, reference_node))
    return all_paths



# Impedance between nodes in radial network

def total_impedance_of_path(path, n_network):
    """Returns total impedance of a path (list of nodes) in a radial network.
    """
    tot_impedance = 0 + 0j
    path = path.copy()
    from_node = path.pop(0)
    while path:
        to_node = path.pop(0)
        tot_impedance += get_impedance_of_branch(from_node, to_node, n_network)
        from_node = to_node
    return tot_impedance


def impedance_for_all_paths_in_network(n_network, reference_node=None):
    """Returns dict of path-impedance pairs for all paths (list of nodes) from reference node in a radial network.
    """
    if reference_node is None: reference_node = get_reference_bus_ID(n_network)

    all_paths = all_paths_from_node(reference_node, n_network, reference_node)
    impedances = {}
    for path in all_paths:
        impedances[path] = total_impedance_of_path(path, n_network)
    return impedances


def path_of_highest_impedance(n_network, reference_node=None):
    """Finds path from reference-node to leaf-nodes in radial network with highest imepedance.
    """

    if reference_node is None: reference_node = get_reference_bus_ID(n_network)

    path_impedances = impedance_for_all_paths_in_network(n_network, reference_node)
    path_impedances = {path: abs(Z) for path, Z in path_impedances.items()}
    return max(path_impedances, key=path_impedances.get)
