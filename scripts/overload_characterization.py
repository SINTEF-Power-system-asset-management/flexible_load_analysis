import numpy as np

from flexible_load_analysis.data_initialization import data_loading as init, preprocessing
from flexible_load_analysis import utilities as util
from flexible_load_analysis.flexibility.overload_synthesis import *
from flexible_load_analysis.flexibility.flexibility_analysis import *

if __name__ == "__main__":

    np.random.seed(0)

    STR_CONFIG_PATH = "in_data/example_data/example_config.toml"
    dict_config, dict_data, dict_network = init.initialize_config_and_data(
        STR_CONFIG_PATH)

    # Data-structure
    dict_loads_ts, dict_preprocessing_log = preprocessing.preprocess_all_loads(dict_config, dict_data)
    
    add_N_random_loads(dict_loads_ts, dict_network, agg_index=1, num_iterations=50, plot_aggregate=True, plot_histogram=True)
    
    # Pr. now, choice to increase load nr. 18 is chosen arbritarily
    flex_need = increase_single_load(dict_loads_ts, dict_network, customer_index=8, aggregation_index=1, fl_increase=1200)

    # Temperature-correlation
    ts_temperature_historical = util.get_first_value_of_dictionary(dict_data["temperature_measurements"])
    overload_temperature_correlation(ts_temperature_historical, flex_need)
