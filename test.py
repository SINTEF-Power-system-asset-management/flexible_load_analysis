from flexibility import flexibility_need as fn
import init
import load_points
import network
import net_modification
import interactive_analysis
import plotting
import utilities
import pandapower as pp
import numpy as np

print()
print("#############################################################################################")
print("##                              Generic Load Modelling                                     ##")
print("#############################################################################################")
print()

STR_CONFIG_PATH = "example_data/example_config.toml"
dict_config, dict_data, dict_network = init.initialize_config_and_data(
    STR_CONFIG_PATH)

# Network datastructures
dict_loads_ts = load_points.prepare_all_loads(dict_config, dict_data)         # Leaf-Nodes
#dict_network = network.convert_network_dictionary_to_graph(dict_network)   # Graph

#dict_loads_ts, dict_network = net_modification.interactively_modify_net(dict_config, dict_loads_ts, dict_network)

str_node = "30001"
str_limit = 65.0
l_overloads = fn.find_overloads(dict_loads_ts[str_node], str_limit)

for i in l_overloads:
    print(i)