import init
import preprocessing
import modelling
import plotting

print()
print("#############################################################################################")
print("##                              Generic Load Modelling                                     ##")
print("#############################################################################################")
print()

STR_CONFIG_PATH = "example_data\\example_config.toml"
dict_config, dict_data_ts = init.initialize_config_and_data(STR_CONFIG_PATH)

dict_data_ts = preprocessing.preprocess_data(dict_config["preprocessing"], dict_data_ts)

dict_model = modelling.model_load(dict_config["modelling"], dict_data_ts)

plotting.plot_selection(dict_config, dict_data_ts, dict_model)

# Todo: write to file