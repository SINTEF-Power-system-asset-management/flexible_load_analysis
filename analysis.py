import network
import timeseries as ts

def aggregate_load_of_node(n_node, n_load_of_leaf_nodes, g_network):
    """Finds timeseries of total load experienced by a node.

    Parameters:
    ----------
    n_node : node-name
        Node which to aggregate load at.
    n_load_of_leaf_nodes : nodes
        Container indexable by node-names of load-timeseries at that node.
    g_network : graph
        Directed graph of network-topology of loads.

    Returns:
    ----------
    ts_sum : timeseries
        Calculated aggregated load at n_node.

    Notes:
    ----------
    Will calculate recursively, stopping at nodes which have no children which
    are then treated as customers.

    """
    if not n_node in g_network:
        raise Exception("Error: Node missing from network")
    list_children = network.list_children_of_node(n_node, g_network)

    ts_sum = []
    try:
        ts_sum = n_load_of_leaf_nodes[str(n_node)]
    except KeyError:
            print("Warning: Load-point", n_node, "is missing timeseries!")
            ts_sum = []
    if list_children:    
        for n_child in list_children:
            ts_child = aggregate_load_of_node(n_child, n_load_of_leaf_nodes, g_network)
            ts_sum = ts.add_timeseries(ts_sum, ts_child)
    return ts_sum