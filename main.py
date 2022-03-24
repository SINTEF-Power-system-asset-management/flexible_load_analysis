import init
import load_points
import network
import net_modification
import interactive_analysis
import plotting
import utilities

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

dict_results = {}
bool_continue_modification_and_analysis = True
while bool_continue_modification_and_analysis:
    dict_results = interactive_analysis.interactively_choose_analysis(dict_config, dict_results, dict_loads_ts, dict_network)
    
    dict_loads_ts, dict_network = net_modification.interactively_modify_net(dict_config, dict_loads_ts, dict_network)

    print("Continue modification and analysis?")
    str_choice = utilities.input_until_acceptable_response(['y','n'])
    if str_choice == 'n':
        bool_continue_modification_and_analysis = False