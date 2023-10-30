from flexible_load_analysis.data_initialization import data_loading, preprocessing

def load_test_loads_and_network(single_radial=False):
    if single_radial:
        STR_CONFIG_PATH = "in_data/test_data/single_radial/config.toml"
    else:
        STR_CONFIG_PATH = "in_data/test_data/two_radials/config.toml"
    dict_config, dict_data, dict_network = data_loading.initialize_config_and_data(STR_CONFIG_PATH, suppress_status=True)

    dict_loads_ts, _dict_preprocessing_log = preprocessing.preprocess_all_loads(dict_config, dict_data, suppress_status=True)

    return dict_loads_ts, dict_network


if __name__=="__main__":
    d_loads, d_network = load_test_loads_and_network()
    assert d_loads and d_network
