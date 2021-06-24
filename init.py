import toml
import data_loading
import utilities

def load_config():
    """
    fp_config = open('config.json', 'r')
    dict_config = json.load(fp_config)
    """
    dict_config = toml.load("config.toml")
    return dict_config 

def init():
    ## Loading config ###
    dict_config = load_config()
    print("Loaded the following config-file:")
    utilities.print_dictionary_recursive(dict_config)
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
        print("successfully loaded: ", data_source)
    
    return


init()

