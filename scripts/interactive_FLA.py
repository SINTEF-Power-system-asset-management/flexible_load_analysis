from flexible_load_analysis.data_initialization import data_loading, preprocessing
from flexible_load_analysis.modelling import modelling
from flexible_load_analysis.objects import net_modification
from flexible_load_analysis.analysis import interactive_analysis
from flexible_load_analysis import utilities

print()
print("#############################################################################################")
print("##                              Generic Load Modelling                                     ##")
print("#############################################################################################")
print()

STR_CONFIG_PATH = "in_data/example_data/example_config.toml"
dict_config, dict_data, dict_network = data_loading.initialize_config_and_data(
    STR_CONFIG_PATH)

dict_loads_ts, dict_preprocessing_log = preprocessing.preprocess_all_loads(dict_config, dict_data)         # Leaf-Nodes

if dict_config["modelling"]["perform_modelling"]:
    dict_loads_ts, dict_modelling_log = modelling.model_all_loads(dict_config["modelling"], dict_loads_ts)

dict_results = {}
bool_continue_modification_and_analysis = True
while bool_continue_modification_and_analysis:
    dict_results = interactive_analysis.interactively_choose_analysis(dict_config, dict_results, dict_loads_ts, dict_network)
    
    dict_loads_ts, dict_network = net_modification.interactively_modify_net(dict_config, dict_loads_ts, dict_network)

    print("Continue modification and analysis?")
    str_choice = utilities.input_until_acceptable_response(['y','n'])
    if str_choice == 'n':
        bool_continue_modification_and_analysis = False