import data_loading
from utilities import print_dictionary_recursive


def initialize_config_and_data(str_config_path):
    """Loads configuration file and creates timeseries from the data-sources.

    Returns
    ----------
    dict_config : dict
        Dictionary containing loaded configuration-file.
    dict_data : dict
        Pairs of data-sources as strings and loaded datafiles on timeseries-format.
    dict_network : dict
        Dictionary of network-information required to build graph-representation.
    """
    ## Loading config ###
    print("Preparing to load config-file:", str_config_path)
    dict_config = data_loading.load_config(str_config_path)
    print("Loaded the following config-file:")
    print("----------------------------------------")
    print_dictionary_recursive(dict_config)
    print("----------------------------------------")
    print("Do you want to override any parameters (No)/Yes?")
    str_input = str.lower(input())
    if str_input == 'y' or str_input == 'yes':
        raise(Exception("Not configured yet"))

    ### Loading data ###
    print("Beginning to load data...")
    dict_data_config = dict_config["data"]
    dict_data = {}
    for data_source in dict_data_config:
        dict_data[data_source] = data_loading.load_data_and_create_timeseries(
            dict_data_config[data_source])
        print("Successfully loaded:", data_source)

    ### Loading network ###
    print("Beginning to load network...")
    dict_network_config = dict_config["network"]
    dict_network = data_loading.load_network_from_directory(
        dict_network_config)

    print("Successfully loaded all components")
    return dict_config, dict_data, dict_network
