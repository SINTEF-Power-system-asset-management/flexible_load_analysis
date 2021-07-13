import init
import nodes
import plotting

print()
print("#############################################################################################")
print("##                              Generic Load Modelling                                     ##")
print("#############################################################################################")
print()

STR_CONFIG_PATH = "config.toml"
dict_config, dict_data = init.initialize_config_and_data(STR_CONFIG_PATH)

dict_loads = nodes.prepare_all_nodes(dict_config, dict_data)

# Commented to avoid errors while reconfiguring.
#plotting.plot_selection(dict_config, dict_data_ts, dict_model)

# Todo: write to file