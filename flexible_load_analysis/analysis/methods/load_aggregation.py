"""Aggregation of all loads "downstream" to some other node.
"""
import numpy as np

from ...objects import network, radial_network_traversal, timeseries as ts


def aggregate_load_of_node(agg_node, d_loads, d_network, reference_node=None):
    """Finds timeseries of total load experienced by a node.

    Parameters:
    ----------
    agg_node : node-name
        Node which to aggregate load at.
    d_loads : nodes
        Container indexable by node-names of load-timeseries at that node.
    d_network : Dict
        Matpower-formatted dictionary of network.
    reference_node : node-name
        Supply (reference) node of network. 

    Returns:
    ----------
    ts_sum : timeseries
        Calculated aggregated load at str_load_ID.
    
    Notes:
    ----------
    Assumes radial distribution.
    """

    if not network.node_in_network(agg_node, d_network):
        raise Exception(f"Error: Node [{agg_node}] missing from network")
    
    if reference_node is None:
        reference_node = network.get_reference_bus_ID(d_network)
    
    ts_agg = np.empty((0))

    contributing_nodes = radial_network_traversal.all_loads_below(agg_node, d_network, d_loads, reference_node)

    if contributing_nodes:
        all_timestamps = [d_loads[n][:,0] for n in contributing_nodes]
        most_timestamps = all_timestamps[np.argmax([t.shape[0] for t in all_timestamps])]
        ts_agg = np.zeros((most_timestamps.shape[0],2),dtype=object)
        ts_agg[:,0] = most_timestamps

    for n in contributing_nodes:
        ts_agg = ts.add_timeseries(ts_agg, d_loads[n])

    contributing_nodes.sort()
    print(f"Nodes contributing to aggregate: {contributing_nodes}")
    return ts_agg