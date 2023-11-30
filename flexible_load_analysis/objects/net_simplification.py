import warnings
import copy

import numpy as np

from ..analysis.methods.load_aggregation import aggregate_given_loads
from .radial_network_traversal import all_buses_below
from . import network, net_modification


def simplify_HV_transformer(HV_bus, LV_bus, unifying_voltage_kV, dict_network):
    # Special case when the high voltage side of the transformer is the reference bus
    # Then this can simply be made to the lower voltage level,
    # with impedance corrected
    if network.is_reference_bus(HV_bus, dict_network):
        # Reference bus stays as a reference bus
        network.convert_trafo_branch_to_equivalent_impedance(HV_bus, LV_bus, dict_network)
        network.set_voltage_level(HV_bus, unifying_voltage_kV, dict_network)

    # if the high voltage side, however, is connected to a larger network then 
    # this must be handled differently, possibly by simply throwing this part
    # of the network away
    else:
        # For now, simply throw an error
        print(f"{HV_bus},{LV_bus}")
        raise(NotImplementedError("Method for simplifying net of higher voltage values is not yet implemented."))
    
    return dict_network


def simplify_LV_transformer(HV_bus, LV_bus, unifying_voltage_kV, 
                            dict_loads, dict_network, 
                            reference_bus=None, keep_highest_impedance_loadline=None):
    # 2.1 Change voltage level of outer node of trafo
    network.set_voltage_level(LV_bus, unifying_voltage_kV, dict_network)

    # 2.2 Compute equivalent impedance of trafo-branch, optionally choosing to preserve child of highest impedance
    nodes_to_remove = all_buses_below(LV_bus, dict_network, reference_bus)
    if nodes_to_remove: 
        # OBS: Here we assume that nodes_to_remove only contains buses connected directly to LV_bus.
        # This may not necessarily be the case in a larger net with multiple voltage levels.
        # This will then fail get_impedance_of_branch
        node_impedance_pairs = [(n, network.get_impedance_of_branch(n, LV_bus, dict_network)) for n in nodes_to_remove]
        node_of_highest_impedance, highest_impedance = sorted(node_impedance_pairs, key=lambda p : p[1], reverse=True)[0]

        if keep_highest_impedance_loadline:
            nodes_to_remove.remove(node_of_highest_impedance)
            network.set_voltage_level(node_of_highest_impedance, unifying_voltage_kV, dict_network)
            additional_trafo_impedance = 0
        else:
            additional_trafo_impedance = highest_impedance
    else:
        # Case when bus has no nodes below itself
        additional_trafo_impedance = 0

    network.convert_trafo_branch_to_equivalent_impedance(HV_bus, LV_bus, dict_network)
    new_impedance = network.get_impedance_of_branch(HV_bus, LV_bus, dict_network) + additional_trafo_impedance
    network.set_line_impedance_of_branch(HV_bus, LV_bus, new_impedance, dict_network)

    # 2.3 Aggregate loads and remove child-nodes
    new_load_ts = aggregate_given_loads([n for n in nodes_to_remove if n in dict_loads], dict_loads)
    for n in nodes_to_remove:
        net_modification.remove_node_from_net(dict_loads, dict_network, n)
    if np.any(new_load_ts): dict_loads[LV_bus] = new_load_ts
    
    return dict_loads, dict_network, nodes_to_remove


def simplify_net(dict_loads, dict_network, unifying_voltage_kV, reference_bus=None, keep_highest_impedance_loadline=False):
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
    keep_highest_impedance_loadline (optional) : bool
        Decides if load of highest impedance path is excluded from being aggregated into transformer
    
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

    # For each pair, simplify it based on what type of transformer it is.
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
            # If the trafo-pair is not connected to the subgrid of voltage level unifying_voltage.
            inner_node = None
            outer_node = None

        if outer_node in nodes_removed_so_far:
            continue

        # Now there are three cases:
        # 1. The transformer in question is transforming up the radial, relative to the subnet of voltage unifying_voltage
        # 2. The transformer is transforming down the radial, relative to the subnet of interest
        # 3. The transformer in question is not connected to the subnet of interest.
        if network.voltage_for_node_id(outer_node, dict_network_simplified) > unifying_voltage_kV:
            # 1. Simplifying upwards a transformer
            simplify_HV_transformer(outer_node, inner_node, unifying_voltage_kV, dict_network_simplified)

        elif network.voltage_for_node_id(outer_node, dict_network_simplified) < unifying_voltage_kV:
            # 2. Simplifying downwards a transformer
            _, _, nodes_removed = simplify_LV_transformer(
                inner_node, outer_node, unifying_voltage_kV,
                dict_loads_simplified, dict_network_simplified,
                reference_bus=reference_bus, keep_highest_impedance_loadline=keep_highest_impedance_loadline
            )
            nodes_removed_so_far += nodes_removed

        else:
            # 3. Transformer is not connected to subnet of interest
            # For now we simply elect to not simplify them.
            # TODO: Can be handled by simply removing these buses?
            continue

    return dict_loads_simplified, dict_network_simplified