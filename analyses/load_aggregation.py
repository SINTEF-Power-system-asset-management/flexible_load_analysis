"""Aggregation of all loads "downstream" to some other node.
"""

import timeseries as ts
import network

def aggregate_load_of_node(str_load_ID, dict_loads_ts, g_network):
    """Finds timeseries of total load experienced by a node.

    Parameters:
    ----------
    str_load_ID : node-name
        Node which to aggregate load at.
    dict_loads_ts : nodes
        Container indexable by node-names of load-timeseries at that node.
    g_network : graph
        Directed graph of network-topology of loads.

    Returns:
    ----------
    ts_sum : timeseries
        Calculated aggregated load at str_load_ID.

    Notes:
    ----------
    Will calculate recursively, stopping at nodes which have no children which
    are then treated as customers.

    """
    if not network.node_in_network(str_load_ID, g_network):
        raise Exception("Error: Node missing from network")
    list_children = network.list_children_of_node(str_load_ID, g_network)

    ts_sum = []
    try:
        ts_sum = dict_loads_ts[str(str_load_ID)]
    except KeyError:
        print("Warning: Load-point", str_load_ID, "is missing timeseries!")
        ts_sum = []
    if list_children:
        for str_child in list_children:
            ts_child = aggregate_load_of_node(
                str_child, dict_loads_ts, g_network)
            ts_sum = ts.add_timeseries(ts_sum, ts_child)
    return ts_sum