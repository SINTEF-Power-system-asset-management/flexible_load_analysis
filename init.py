import toml
import data_loading
import utilities

def load_config():  # Move to "loading"-module?
    dict_config = toml.load("config.toml")
    return dict_config 

def initialize_config_and_data():
    ## Loading config ###
    dict_config = load_config()
    print("Loaded the following config-file:")
    print("----------------------------------------")
    utilities.print_dictionary_recursive(dict_config)
    print("----------------------------------------")
    print("Do you want to override any parameters (No)/Yes?")
    str_input = str.lower(input())
    if str_input == 'y' or str_input == 'yes':
        raise(Exception("Not configured yet"))


    ### Loading data ###
    print("Beginning to load data...")
    dict_data_config = dict_config["data"]
    dict_data_ts = {}
    for data_source in dict_data_config:
        dict_data_ts[data_source] = data_loading.load_data_and_create_timeseries(dict_data_config[data_source])
        print("Successfully loaded: ", data_source)
    
    return dict_config, dict_data_ts    # Bad? Consider implementing dict_config as getter-setter, so it doesn't have to be passed around as much?