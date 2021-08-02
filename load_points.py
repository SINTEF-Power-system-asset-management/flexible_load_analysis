"""Module for implementing storage and interaction of the nodes of the network.

Notes
----------
Load-points are defined as an ID, timeseries-pair of a specific load-point.
This may be expanded to contain other fields, like customer-type or voltage-level.
Mostly relates to customers of the grid.

The point of isolating operations relating to load-points is such that the
chosen way of storing the load-points may be changed at will, without needing to
change code outside this module.

"""
import datetime as dt
import numpy as np
import preprocessing
import modelling
import utilities
import plotting


def prepare_all_nodes(dict_config, dict_data):
    """Prepares nodes based on input data and config.
    Parameters
    ----------
    dict_config : dict
        Configuration-file.
    dict_data : dictionary of measured loads and temperature.
    """
    print("Preparing common data...")
    date_start = dt.date.fromisoformat(
        dict_config["data"]["load_measurements"]["first_date_iso"])
    date_end = dt.date.fromisoformat(
        dict_config["data"]["load_measurements"]["last_date_iso"])

    ts_temperature_historical = utilities.get_first_value_of_dictionary(
        dict_data["temperature_measurements"])
    ts_temperature_historical = preprocessing.remove_nan_and_none_datapoints(
        ts_temperature_historical)
    dict_daily_normal_temperature = preprocessing.compute_daily_historical_normal(
        ts_temperature_historical)
    dict_temperature_n_day_average = preprocessing.create_n_day_average_dict(
        ts_temperature_historical,
        date_start, date_end,  n=3)

    print("Preparing all loads in network...")
    # Preprocessing and potential modelling of every load-point
    dict_loads = {}
    for str_node_ID in dict_data["load_measurements"]:
        print("--------------------")
        print("Preparing load-point", str_node_ID + "...")

        dict_node_ts = {}
        dict_node_ts["load_measurements"] = dict_data["load_measurements"][str_node_ID]
        dict_node_ts["normal_temperature"] = dict_daily_normal_temperature
        dict_node_ts["n-day_average_temperature"] = dict_temperature_n_day_average

        print("Preprocessing", str_node_ID + "...")
        dict_node_ts = preprocessing.preprocess_data(
            dict_config["preprocessing"], dict_node_ts)

        if dict_config["modelling"]["perform_modelling"]:
            print("Modelling based on dataset", str_node_ID + "...")
            dict_model = modelling.model_load(
                dict_config["modelling"], dict_node_ts)
            dict_loads[str_node_ID] = dict_model["load"]
        else:
            dict_loads[str_node_ID] = dict_node_ts["load"]

    print("--------------------")
    print("Successfully prepared all load-points")
    return dict_loads


def add_timeseries(ts_a, ts_b):
    """Returns the sum of data-values in two timeseries

    Parameters:
    ----------
    ts_a, ts_b : timeseries

    Returns:
    ----------
    ts_sum : timeseries
        Sum of input timeseries.

    Notes:
    ----------
    This function will cause skewing if both datasets contain similar amount of
    missing datapoints.

    The function will amend non-equally sized timeseries by searching for
    matching timestamps.

    """
    if ts_a == []:
        return ts_b
    if ts_b == []:
        return ts_a

    if len(ts_a) != len(ts_b):
        print("Warning: Mismatching length when adding timeseries!")

        if len(ts_a[:, 0]) < len(ts_b[:, 0]):
            ts_shortest, ts_longest = ts_a, ts_b
        else:
            ts_shortest, ts_longest = ts_b, ts_a
        int_first_index = utilities.first_matching_index(
                            ts_longest[:, 0], 
                            lambda dt: dt == ts_shortest[0, 0])
        ts_first_part_of_sum = ts_longest[:int_first_index, :]
        ts_second_part_of_sum = add_timeseries(
                                    ts_shortest, 
                                    ts_longest[int_first_index:, :])
        ts_sum = np.concatenate((ts_first_part_of_sum, 
                                ts_second_part_of_sum), 
                                axis=0)

    else:
        arr_time = ts_a[:, 0]
        arr_data = ts_a[:, 1] + ts_b[:, 1]
        ts_sum = np.transpose(np.array([arr_time, arr_data]))
    return ts_sum

def graphically_represent_load_point(lp_load):
    # Nicely present info of load point, i.e. list info such as voltage level,
    # customer type. Graph timeseries, etc.

    plotting.plot_timeseries([lp_load], ["ID: "], "Time", "Load", "Timeseries of customer: ")
    return