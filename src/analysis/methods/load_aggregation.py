"""Aggregation of all loads "downstream" to some other node.
"""
import numpy as np
import objects.timeseries as ts
import objects.network as network

def _voltage_for_node_id(node, d_network):
    node_idx = np.where(d_network["bus"]["BUS_I"] == node)
    return d_network["bus"]["BASE_KV"][node_idx]

def aggregate_load_of_node(agg_node, d_loads, d_network, reference_node):
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
    
    # Since aggregation function should work even in a network of two radials, the first step is 
    # to find which node in the radial of agg_node lies between agg_node and reference_node, and 
    # which node(s) lie below agg_node. That way only the nodes below are used for aggregating the load.
    
    # This is achieved by a breadth-first-search from reference_node to agg_node.
    prev_node = None
    explored = []
    queue = [reference_node]
    if agg_node != reference_node:
        # Bredde-først-søk for å finne node som leder fra reference til agg_node
        while queue:
            prev_node = queue.pop()
            explored.append(prev_node)
            new_children = network.list_currently_connected_nodes(prev_node, d_network)
            if agg_node in new_children:
                break
            # Kun søk noder med lavere eller lik spenning
            for n in new_children:
                if (not n in explored) and (_voltage_for_node_id(n, d_network) <= _voltage_for_node_id(prev_node, d_network)):
                    queue.append(n)
        else:
            print(f"Unable to find route from [{reference_node}] to [{agg_node}]")
            return np.empty((0))

        # Siden vi antar radielt nett er det kun én buss som "leder fra referansen til node".
        # Dette er prev_node fra BFS når de break-er. Altså: I radielle nett har man i enhver driftssituasjon kun
        # én "forelder", og denne har vi nå funnet.
        parent_of_agg = prev_node
    else:
        # I tilfellet hvor vi aggregerer på referansen
        parent_of_agg = None


    # Aggregation then continues with finding all customers below agg_node (that is - all nodes connected to agg_node but excluding
    # parent_of_agg) and aggregating their loads.
    ts_agg = np.empty((0))
    prev_node = agg_node
    contributing_nodes = []
    # Vi skal søke for alle koblinger unntatt parent_node fra forrige BFS
    queue = [node for node in network.list_currently_connected_nodes(agg_node, d_network) if node != parent_of_agg]
    explored = [agg_node]
    while queue:
        prev_node = queue.pop()
        explored.append(prev_node)

        if prev_node in d_loads:
            ts_agg = ts.add_timeseries(ts_agg, d_loads[prev_node])
            contributing_nodes.append(prev_node)
            # Sanity-check: forventer at noder som kommer hit (altså har en last-tidsserie) også vil ha tom
            # new_children-objekt.
        new_children = network.list_currently_connected_nodes(prev_node, d_network)
        # Kun søk noder med lavere eller lik spenning
        for n in new_children:
            if (not n in explored) and (_voltage_for_node_id(n, d_network) <= _voltage_for_node_id(prev_node, d_network)):
                queue.append(n)

    contributing_nodes.sort()
    print(f"Nodes contributing to aggregate: {contributing_nodes}")
    return ts_agg