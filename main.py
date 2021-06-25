import init
import preprocessing

print()
print("#############################################################################################")
print("##                              Generic Load Modelling                                     ##")
print("#############################################################################################")
print()

dict_config, dict_data_ts = init.initialize_config_and_data()

dict_data_ts = preprocessing.preprocess_data(dict_config, dict_data_ts)