# Aggregation factor: The ratio between a child's load at the point of the node's aggregated max load, and the child's max load
# Norsk: "Sammenlagringsfaktor"

from .load_aggregation import aggregate_load_of_node
from .max_load import find_max_load
from ...objects import network

def aggregation_factors(str_bus_ID, dict_loads_ts, g_network): 

    ts_aggregate = aggregate_load_of_node(str_bus_ID, dict_loads_ts, g_network)
    fl_max, int_max_index = find_max_load(ts_aggregate)

    dict_aggregation_factors = {}
    list_children = network.list_children_of_node(str_bus_ID, g_network)
    for  str_child_ID in list_children:
        # find load of child at init_max_index
        ts_child = dict_loads_ts[str_child_ID]
        fl_child_load_at_max = ts_child[int_max_index,1]

        # find child's max load
        c_max, c_max_index = find_max_load(ts_child)
        dict_aggregation_factors[str_child_ID] = fl_child_load_at_max/c_max

    return dict_aggregation_factors

# Coincidence factor: Contribution of each child's load to the node's aggregated max load

def coincidence_factors(str_bus_ID, dict_loads_ts, g_network): 

    ts_aggregate = aggregate_load_of_node(str_bus_ID, dict_loads_ts, g_network)
    fl_max, int_max_index = find_max_load(ts_aggregate)

    dict_coincidence_factors = {}
    list_children = network.list_children_of_node(str_bus_ID, g_network)
    for  str_child_ID in list_children:
        # find load of child at init_max_index
        ts_child = dict_loads_ts[str_child_ID]
        fl_child_load_at_max = ts_child[int_max_index,1]

        dict_coincidence_factors[str_child_ID] = fl_child_load_at_max/fl_max
    
    return dict_coincidence_factors