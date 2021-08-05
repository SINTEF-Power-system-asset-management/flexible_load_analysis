import init
import load_points
import network
import net_modification
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
dict_loads_ts = load_points.prepare_all_loads(dict_config, dict_data)         # Leaf-Nodes
g_network = network.convert_network_dictionary_to_graph(dict_network)   # Graph

dict_loads_ts, g_network = net_modification.interactively_modify_net(dict_config, dict_loads_ts, g_network)

# Commented to avoid errors while reconfiguring.
#plotting.plot_selection(dict_config, dict_data_ts, dict_model)

# Todo: write to file
