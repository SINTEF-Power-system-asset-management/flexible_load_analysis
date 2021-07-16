import init
import load_points
import network
import plotting

print()
print("#############################################################################################")
print("##                              Generic Load Modelling                                     ##")
print("#############################################################################################")
print()

STR_CONFIG_PATH = "config.toml"
dict_config, dict_data, dict_network = init.initialize_config_and_data(STR_CONFIG_PATH)

dict_loads = load_points.prepare_all_nodes(dict_config, dict_data)

g_network = network.convert_network_dictionary_to_graph(dict_network)

# Commented to avoid errors while reconfiguring.
#plotting.plot_selection(dict_config, dict_data_ts, dict_model)

# Todo: write to file