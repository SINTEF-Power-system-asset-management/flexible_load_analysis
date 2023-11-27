import warnings
import copy

import numpy as np

from ..analysis.methods.load_aggregation import aggregate_load_of_node
from .radial_network_traversal import all_buses_below
from . import network, net_modification

def simplify_net(dict_loads, dict_network, unifying_voltage_kV, reference_bus=None):
    # First find the nodes with the highest impedance, these should not be simplified away [TIR]
    # Also reduce network to single voltage level
    # This is acieved by aggregating up all leaf-nodes connected to the same substation
    # Then combining both sides of the substation into one, increasing its impedance accordingly.

    warnings.warn("Experimental features!")
    if reference_bus is None: reference_bus = network.get_reference_bus_ID(dict_network)

    # Find all pairs of buses which make up a trafo
    trafo_bus_pairs = network.get_all_transformer_bus_pairs(dict_network)
    # We only want to simplify nodes beneath the reference bus (inclusive)
    candidate_nodes = all_buses_below(reference_bus, dict_network, reference_bus) + [reference_bus]
    trafo_bus_pairs = [p for p in trafo_bus_pairs if (p[0] in candidate_nodes and p[1] in candidate_nodes)]


    # for each pair, aggregate the load at the pair and store in a single timeseries to be
    # associated with the combined node
    dict_loads_simplified = copy.deepcopy(dict_loads)
    dict_network_simplified = copy.deepcopy(dict_network)
    nodes_removed_so_far = []
    for (f_bus, t_bus) in trafo_bus_pairs:
        if network.voltage_for_node_id(f_bus, dict_network_simplified) == unifying_voltage_kV:
            inner_node = f_bus
            outer_node = t_bus
        elif network.voltage_for_node_id(t_bus, dict_network_simplified) == unifying_voltage_kV:
            inner_node = t_bus
            outer_node = f_bus
        else:
            continue
            #raise Exception("Transformer present in network which doesn't match unifying voltage level")

        if network.voltage_for_node_id(outer_node, dict_network_simplified) > unifying_voltage_kV:
            # Simplifying upwards a transformer

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
            
        else:
            # If the node in question already was simplified away in a previous step
            if outer_node in nodes_removed_so_far:
                continue
            # Simplifying downwards a transformer
            # Here, the highest impedance of a removed node should really be added to the impedance of outer_node...
            nodes_to_remove = all_buses_below(outer_node, dict_network_simplified, reference_bus)
            new_load_ts = aggregate_load_of_node(outer_node, dict_loads_simplified, dict_network_simplified, reference_bus)
            for n in nodes_to_remove:
                net_modification.remove_node_from_net(dict_loads_simplified, dict_network_simplified, n)
            nodes_removed_so_far += nodes_to_remove
            if np.any(new_load_ts): dict_loads_simplified[outer_node] = new_load_ts

            network.convert_trafo_branch_to_equivalent_impedance(f_bus, t_bus, dict_network_simplified)
            network.set_voltage_level(outer_node, unifying_voltage_kV, dict_network_simplified)

    return dict_loads_simplified, dict_network_simplified