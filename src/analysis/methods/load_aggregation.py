"""Aggregation of all loads "downstream" to some other node.
"""
import numpy as np
import objects.timeseries as ts
import objects.network as network

def voltage_for_node_id(node, d_network):
    node_idx = np.where(d_network["bus"]["BUS_I"] == node)
    return d_network["bus"]["BASE_KV"][node_idx]

def aggregate_load_of_node(agg_node, d_network, d_loads, reference_node):
    """Finds timeseries of total load experienced by a node.

    Parameters:
    ----------
    agg_node : node-name
        Node which to aggregate load at.
    d_network : Dict
        Matpower-formatted dictionary of network.
    d_loads : nodes
        Container indexable by node-names of load-timeseries at that node.
    reference_node : node-name
        Supply (reference) node of network. 

    Returns:
    ----------
    ts_sum : timeseries
        Calculated aggregated load at str_load_ID.
    """

    if not network.node_in_network(agg_node, d_network):
        raise Exception(f"Error: Node [{agg_node}] missing from network")
    
    prev_node = None
    explored = []
    queue = [reference_node]
    if agg_node != reference_node:
        # Bredde-først-søk for å finne node som leder fra reference til agg_node
        while queue:
            prev_node = queue.pop()
            explored.append(prev_node)
            # Denne funksjonen fungerer fortsatt? Bør endres til å gi alle noder som er knyttet til input-noden,
            # altså uavhengig om branch-en går A->B eller B->A, dette er egentlig samme.
            new_children = network.list_children_of_node(prev_node, d_network)
            if agg_node in new_children:
                break
            # Kun søk noder med lavere eller lik spenning
            for n in new_children:
                if (not n in explored) and (voltage_for_node_id(n, d_network) <= voltage_for_node_id(prev_node, d_network)):
                    queue.append(n)
        else:
            raise Exception(f"Unable to find route from [{reference_node}] to [{agg_node}] without breaking voltage restriction")

        # Siden vi antar radielt nett er det kun én buss som "leder fra referansen til node".
        # Dette er prev_node fra BFS. Altså: I radielle nett har man i enhver driftssituasjon kun
        # én "forelder", og denne har vi nå funnet.
        parent_node = prev_node
    else:
        # I tilfellet hvor vi aggregerer på referansen
        parent_node = None

    # Aggregering blir samme bredde-først søk fra agg_node til alle dens koblinger UNNTATT forelderen
    ts_agg = np.empty((0))
    prev_node = agg_node
    # Vi skal søke for alle koblinger unntatt parent_node fra forrige BFS
    queue = network.list_children_of_node(agg_node, d_network) - [parent_node]
    while queue:
        prev_node = queue.pop()
        explored.append(prev_node)

        if prev_node in d_loads:
            ts_agg = ts.add_timeseries(ts_agg, d_loads[prev_node])
            # Sanity-check: forventer at noder som kommer hit (altså har en last-tidsserie) også vil ha tom
            # new_children-objekt.
        # Denne funksjonen fungerer fortsatt? Bør endres til å gi alle noder som er knyttet til input-noden,
        # altså uavhengig om branch-en går A->B eller B->A, dette er egentlig samme.
        new_children = network.list_children_of_node(prev_node, d_network)
        # Kun søk noder med lavere eller lik spenning
        for n in new_children:
            if (not n in explored) and (voltage_for_node_id(n, d_network) <= voltage_for_node_id(prev_node, d_network)):
                queue.append(n)

    return ts_agg