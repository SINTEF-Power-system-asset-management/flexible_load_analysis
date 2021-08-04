import init
import load_points
import network
import network_modification
import analysis
import plotting

print()
print("#############################################################################################")
print("##                              Generic Load Modelling                                     ##")
print("#############################################################################################")
print()

STR_CONFIG_PATH = "example_data\\example_config.toml"
dict_config, dict_data, dict_network = init.initialize_config_and_data(
    STR_CONFIG_PATH)

# Network datastructures
n_loads = load_points.prepare_all_nodes(dict_config, dict_data)         # Leaf-Nodes
g_network = network.convert_network_dictionary_to_graph(dict_network)   # Graph

n_loads, g_network = network_modification.interactively_modify_network(dict_config, n_loads, g_network)

# Commented to avoid errors while reconfiguring.
#plotting.plot_selection(dict_config, dict_data_ts, dict_model)

# Todo: write to file
