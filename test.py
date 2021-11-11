import init
import load_points
import network
import net_modification
import analysis
import plotting
import utilities
import pandapower as pp

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



pp_network = network.convert_network_dictionary_to_pp(dict_network)
pp.rundcpp(pp_network)
print(pp_network.res_bus)
