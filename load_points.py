"""Module for implementing storage and interaction of the nodes of the network.

Notes
----------
Load-points are defined as an ID, timeseries-pair of a specific load-point.

The point of isolating operations relating to load-points is such that the
chosen way of storing the load-points may be changed at will, without needing to
change code outside this module.

"""
import datetime as dt
import preprocessing
import modelling
import utilities
import plotting


def prepare_all_loads(dict_config, dict_data):
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
    dict_loads_ts = {}
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
            dict_loads_ts[str_node_ID] = dict_model["load"]
        else:
            dict_loads_ts[str_node_ID] = dict_node_ts["load"]

    print("--------------------")
    print("Successfully prepared all load-points")
    return dict_loads_ts


def add_new_load(dict_loads_ts, str_new_load_ID, ts_new_load_data):
    dict_loads_ts[str_new_load_ID] = ts_new_load_data
    return dict_loads_ts


def remove_load(dict_loads_ts, str_load_ID):
    dict_loads_ts.pop(str_load_ID)
    return dict_loads_ts


def print_all_load_points(dict_loads_ts):
    for key in dict_loads_ts:
        print(key)
    return


def graphically_represent_load_point(lp_load):
    """Nicely show off data in single load-point.
    """

    plotting.plot_timeseries(
        [lp_load], ["ID: "], "Time", "Load", "Timeseries of customer: ")
    return
