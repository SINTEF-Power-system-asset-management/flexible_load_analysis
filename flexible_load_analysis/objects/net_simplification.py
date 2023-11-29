import warnings
import copy

import numpy as np

from ..analysis.methods.load_aggregation import aggregate_load_of_node
from .radial_network_traversal import all_buses_below
from . import network, net_modification

def simplify_net(dict_loads, dict_network, unifying_voltage_kV, reference_bus=None):
    """Takes a net (network and associated load-timeseries) and simplifies it into a single voltage level.

    Parameters
    ----------
    dict_loads : dict
        Dictionary of load-timeseries, keyed by load-point ID.
    dict_network : dict
        Dictionary of MATPOWER-formatted dictionaries, keyed by column.
    unifying_voltage_kV : float
        Voltage level to simplify the network into.
    reference_bus (optional) : str
        Reference bus of radial to simplify. Not necessary in networks with single radial.
    
    Returns
    ----------
    dict_loads_simplified : dict
        Dictionary of aggregated load-timeseries, keyed by ID of simplification points.
    dict_network_simplified : dict
        Simplified network of single voltage level and with transformers reduced to lines.

    Notes
    ----------
    In a network with multiple radials, only the radial associated with `reference_bus` will be simplified.
    Simplification entails converting transformers into lines of equivalent impedance,
    aggregating all loads below transformers into a single timeseries,
    and changing voltage level of all buses to that of `unifying_voltage_kV`.
    """
    warnings.warn("Experimental features!")
    if reference_bus is None: reference_bus = network.get_reference_bus_ID(dict_network)

    # Find all (unordered) pairs of buses which make up a trafo
    trafo_bus_pairs = network.get_all_transformer_bus_pairs(dict_network)
    # We only want to simplify nodes beneath the reference bus (inclusive), not nodes of other radials
    candidate_nodes = all_buses_below(reference_bus, dict_network, reference_bus) + [reference_bus]
    trafo_bus_pairs = [p for p in trafo_bus_pairs if (p[0] in candidate_nodes and p[1] in candidate_nodes)]

    # For each pair, aggregate the load and change voltage levels.
    dict_loads_simplified = copy.deepcopy(dict_loads)
    dict_network_simplified = copy.deepcopy(dict_network)
    nodes_removed_so_far = []
    for (f_bus, t_bus) in trafo_bus_pairs:
        # Since f_bus, t_bus in a trafo not necessarily is ordered by voltage, 
        # we first need to find which bus is on the same side as our target voltage leve.
        if network.voltage_for_node_id(f_bus, dict_network_simplified) == unifying_voltage_kV:
            inner_node = f_bus
            outer_node = t_bus
        elif network.voltage_for_node_id(t_bus, dict_network_simplified) == unifying_voltage_kV:
            inner_node = t_bus
            outer_node = f_bus
        else:
            # If one of the trafo-pairs are not connected to the subgrid of voltage level unifying_voltage.
            # For now we simply elect to not simplify them.
            # TODO: Can be handled by simply removing these buses?
            continue

        if outer_node in nodes_removed_so_far:      #TODO: Er det riktig aa ha dette her?
            continue

        # Now there are three cases:
        # 1. The transformer in question is transforming up the radial, relative to the subnet of voltage unifying_voltage
        # 2. The transformer is transforming down the radial, relative to the subnet of interest
        # 3. The transformer in question is not connected to the subnet of interest.
        if network.voltage_for_node_id(outer_node, dict_network_simplified) > unifying_voltage_kV:
            # 1. Simplifying upwards a transformer

            # Special case when the high voltage side of the transformer is the reference bus
            # Then this can simply be made to the lower voltage level,
            # with impedance corrected
            if network.is_reference_bus(outer_node, dict_network_simplified):
                # Reference bus stays as a reference bus
                network.convert_trafo_branch_to_equivalent_impedance(f_bus, t_bus, dict_network_simplified)
                network.set_voltage_level(outer_node, unifying_voltage_kV, dict_network_simplified)

            # if the high voltage side, however, is connected to a larger network then 
            # this must be handled differently, possibly by simply throwing this part
            # of the network away
            else:
                # For now, simply throw an error
                print(f"{inner_node},{outer_node}")
                raise(NotImplementedError("Method for simplifying net of higher voltage values is not yet implemented."))
            
        elif network.voltage_for_node_id(outer_node, dict_network_simplified) < unifying_voltage_kV:
            # 2. Simplifying downwards a transformer
            # TODO: the highest impedance of a removed node should really be added to the impedance of outer_node
            nodes_to_remove = all_buses_below(outer_node, dict_network_simplified, reference_bus)
            new_load_ts = aggregate_load_of_node(outer_node, dict_loads_simplified, dict_network_simplified, reference_bus)
            for n in nodes_to_remove:
                net_modification.remove_node_from_net(dict_loads_simplified, dict_network_simplified, n)
            nodes_removed_so_far += nodes_to_remove
            if np.any(new_load_ts): dict_loads_simplified[outer_node] = new_load_ts

            network.convert_trafo_branch_to_equivalent_impedance(f_bus, t_bus, dict_network_simplified)
            network.set_voltage_level(outer_node, unifying_voltage_kV, dict_network_simplified)

        else:
            # 3. Transformer is not connected to subnet of interest
            pass

    return dict_loads_simplified, dict_network_simplified