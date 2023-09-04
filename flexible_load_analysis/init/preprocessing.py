import datetime as dt
import copy

import numpy as np

from ..modelling import modelling
from .. import utilities

"""Module for performing various timeseries preprocessing steps.
The module functionality is designed to be pipeline-able, in that
a choice of preprocessing methods may be run back to back.
"""


# Helper functions

def datetime_to_yearless_iso_string(dt):
    """Converts datetime-object to string of date without year on iso format.
    """
    return dt.isoformat()[5:10]


def compute_daily_historical_normal(ts_daily_data_historical):
    """Computes daily average value over historical timeseries.

    Parameters
    ----------
    ts_daily_data_historical : timeseries
        Historical daily data to compute daily normal over. 

    Returns
    ----------
    dict_daily_average : dict
        Dictionary of daily historical averages. Keys are yearless dates on
        iso format. 

    Notes
    ----------
    Function assumes timeseries is at most of daily frequency.

    The function does not guarantee the output dictionary is chronologically 
    ordered.
    Example: Datasets which begin at non-leapyears will have "02-29" as the 
    last entry in the output dictionary.
    """
    dict_running_sum_and_count = {}
    for i in range(len(ts_daily_data_historical)):
        arr_cur_data = ts_daily_data_historical[i, :]
        str_date_yearless = datetime_to_yearless_iso_string(arr_cur_data[0])
        flt_cur_sum = dict_running_sum_and_count.get(
            str_date_yearless, [0, 0])[0]
        int_cur_count = dict_running_sum_and_count.get(
            str_date_yearless, [0, 0])[1]
        list_new_sum_and_count = [flt_cur_sum + arr_cur_data[1],
                                  int_cur_count + 1]
        dict_running_sum_and_count[str_date_yearless] = list_new_sum_and_count

    dict_daily_average = {}
    for key in dict_running_sum_and_count:
        dict_daily_average[key] = dict_running_sum_and_count[key][0] / \
            dict_running_sum_and_count[key][1]
    return dict_daily_average


def create_n_day_average_dict(ts_basis, date_start, date_end,  n):
    """Computes backwards n-day average at every point of input timeseries.

    Parameters
    -----------
    ts_basis : timeseries
        Timeseries to calculate average over daily datapoints.
    dt_start : datetime
        First date to calculate from.
    dt_end : datetime
        Last date to calculate to (inclusive)
    n : int
        Amount of days to take backwards average over.

    Returns
    -----------
    dict_averages : dict
        n-day backwards averages, keyed by date.

    Notes
    ----------
    Contents of return will always be a chronologically sorted dict as long as
    ts_basis is sorted.
    """
    int_starting_index = 0
    while int_starting_index < len(ts_basis):
        if ts_basis[int_starting_index][0].date() == date_start:
            break
        else:
            int_starting_index += 1

    dict_averages = {}
    while int_starting_index < len(ts_basis):
        fl_running_sum = 0
        i = 0
        while i < n:
            fl_running_sum += ts_basis[int_starting_index - i][1]
            i += 1

        dt_cur_date = ts_basis[int_starting_index][0].date()
        dict_averages[dt_cur_date] = fl_running_sum / n

        if dt_cur_date == date_end:
            return dict_averages
        else:
            int_starting_index += 1
    raise(Exception("Start or end date missing from basis-timeseries"))



# Preprocessing steps
# Supported preprocessing steps must take a timeseries as first argument,
# a dictionary for optional storing of preprocessing performed and thirdly
# *args and **kwargs.
# Only return is the processed timeseries

# TODO: Create separate modules for each preprocessing step
# TODO: Create enforcement of interface

def remove_nan_and_none_datapoints(ts_data, dict_preprocessing_log, fill_isolated_method=None):
    """Removes datapoints containing NaN or None.

    Parameters
    ----------
    dict_data_ts : dict(timeseries)
        Dictionary of all timeseries to remove NaN and None from.

    Returns
    ----------
    dict_data_ts : dict(timeseries)
        Dictionary of all timeseries without NaN and None-values.
    """
    print("Removing NaN and None datapoints...")
    
    list_good_indeces = []
    for dp in ts_data:
        dp = list(dp)
        if (not None in dp) and (dp == dp):
            list_good_indeces.append(True)
        else:
            list_good_indeces.append(False)
    if fill_isolated_method is None or fill_isolated_method == "":
        ts_data = ts_data[list_good_indeces]
    else:
        # Any data-filling technique other than none requires knowledge of isolated Nans
        num_datapoint = len(list_good_indeces)
        isolated_missing_points_idxs = []
        for i in range(num_datapoint):
            i_is_bad_datapoint = (list_good_indeces[i] == False)
            i_neighbours_good_datapoints = True
            # Only check neighbouring datapoints if not at ends of timeseries
            if i != 0: i_neighbours_good_datapoints = i_neighbours_good_datapoints and (list_good_indeces[i - 1] == True)
            if i != num_datapoint - 1: i_neighbours_good_datapoints = i_neighbours_good_datapoints and (list_good_indeces[i + 1] == True)
            if i_is_bad_datapoint and i_neighbours_good_datapoints: isolated_missing_points_idxs.append(i)

        if fill_isolated_method=="lin_interp":
            raise(NotImplementedError)
        elif fill_isolated_method=="quadratic_interp":
            raise(NotImplementedError)
        else:
            raise(NotImplementedError)

    dict_preprocessing_log["remove_NaN_and_None"] = {"good_indices" : list_good_indeces}
    return ts_data


def remove_negative_values(ts_data):
    raise(NotImplementedError)
    dict_preprocessing_log["remove_negative_values"] = {"result1" : variable}
    return ts_data


def fill_missing_data(ts_data):
    """Finds missing timestamps given some expected resolution and fills using selected method.
    """
    # Should really import some method from timeseries, for cleanliness
    raise(NotImplementedError)
    dict_preprocessing_log["fill_missing_data"] = {"result1" : variable}
    return ts_data


def correct_load_for_temperature_deviations(
        ts_load, dict_preprocessing_log,
        dict_daily_normal_temperature,
        dict_temperature_n_day_average,
        k, x):
    """Performs temperature-correction of load-timeseries based on historical
    temperature measurements.

    Follows method as described in Planboka 
    (https://www.sintef.no/prosjekter/1993/planleggingsbok-for-kraftnett/).

    Parameters
    -----------
    dict_data_ts : dict(timeseries)
        Dictionary containing at least the timeseries of load, temperature-
        measurements for the same period and historical temperature-measurements.
    k, x : float
        Parameters in temperature-correction, temperautre-coefficient and
        temperature-sensetivity.

    Returns
    -----------
    dict_data_ts : dict(timeseries)
        Input-dictionary backloaded with temperature-corrected load and 
        calculated daily historical normal temperature.
    """
    print("Performing temperature-correction of load-data...")
    # Correction step
    ts_load_corrected = np.zeros_like(ts_load)
    skipped_timestamps = []
    for i in range(len(ts_load)):
        arr_datapoint_i = ts_load[i]
        dt_time_i = arr_datapoint_i[0]
        fl_load_i = arr_datapoint_i[1]
        # Removed, but should in theory be performed according to Tønne
        # if 11 <= dt_time_i.month or dt_time_i.month <= 4:
        if True:
            try:
                Tn = dict_daily_normal_temperature[datetime_to_yearless_iso_string(
                    dt_time_i)]
                Ti = dict_temperature_n_day_average[dt_time_i.date()]
                fl_load_corrected_i = fl_load_i + fl_load_i*k*x*(Tn - Ti)
            except KeyError:
                print(f"Temperature for {dt_time_i} missing, skipping correction")
                fl_load_corrected_i = fl_load_i
                skipped_timestamps.append(dt_time_i)
        else:
            fl_load_corrected_i = fl_load_i

        ts_load_corrected[i][0] = dt_time_i
        ts_load_corrected[i][1] = fl_load_corrected_i

    dict_preprocessing_log["correct_for_temperature"] = {"skipped_timestamps" : skipped_timestamps}
    return ts_load_corrected




# Preprocessing pipeline

def preprocess_all_loads(dict_config, dict_data):
    """Prepares nodes based on input data and config.
    Parameters
    ----------
    dict_config : dict
        Configuration-file.
    dict_data : dictionary of measured loads and temperature.
    """

    dict_preprocessing_config = dict_config["preprocessing"]

    preprocessing_funcs = []
    preprocessing_parameters = []
    
    # Remove NaN and None values from load-timeseries
    perform_remove_nan_and_none = dict_preprocessing_config.get("remove_NaN_and_None", False)
    if perform_remove_nan_and_none:
        fill_method = dict_preprocessing_config.get("NaN_and_None_removal", {}).get("fill_method", None)
        preprocessing_funcs.append(remove_nan_and_none_datapoints)
        preprocessing_parameters.append([fill_method])

    # Temperature correction
    perform_temperature_correction = dict_preprocessing_config.get("perform_temperature_correction", False)
    if perform_temperature_correction:
        date_start = dt.date.fromisoformat(
        dict_config["data"]["load_measurements"]["first_date_iso"])
        date_end = dt.date.fromisoformat(
        dict_config["data"]["load_measurements"]["last_date_iso"])

        ts_temperature_historical = utilities.get_first_value_of_dictionary(
            dict_data["temperature_measurements"])
        ts_temperature_historical = remove_nan_and_none_datapoints(
            ts_temperature_historical, {})
        dict_daily_normal_temperature = compute_daily_historical_normal(
            ts_temperature_historical)
        dict_temperature_n_day_average = create_n_day_average_dict(
            ts_temperature_historical,
            date_start, date_end,  n=3)
        
        k = dict_config["preprocessing"]["correct_for_temperature"]["k_temperature_coefficient"]
        x = dict_config["preprocessing"]["correct_for_temperature"]["x_temperature_sensitivity"]
        
        preprocessing_funcs.append(correct_load_for_temperature_deviations)
        preprocessing_parameters.append([dict_daily_normal_temperature, dict_temperature_n_day_average, k, x])

    # Example
    perform_example_step = dict_preprocessing_config.get("perform_example_step", False)
    if perform_example_step:
        fill_method = dict_preprocessing_config.get("NaN_and_None_removal", {}).get("fill_method", None)
        preprocessing_funcs.append(remove_nan_and_none_datapoints)
        preprocessing_parameters.append([fill_method])



    # Actually perform preprocessing.
    preprocessing_log = {}
    dict_loads_ts = {}

    print("Preprocessing all loads in network...")
    for str_node_ID in dict_data["load_measurements"]:
        print(f"Preparing load-point {str_node_ID}...")
        load_ts = copy.deepcopy(dict_data["load_measurements"][str_node_ID])
        preprocessing_log[str_node_ID] = {}

        for func, params in zip(preprocessing_funcs, preprocessing_parameters):
            load_ts = func(load_ts, preprocessing_log[str_node_ID], *params)
        
        dict_loads_ts[str_node_ID] = load_ts
    
    print("--------------------")
    print("Successfully prepared all load-points")
    return dict_loads_ts, preprocessing_log



    """
    # TODO: Model_all_loads func og slutte å kreve at man sender inn dict hvorav én av keys-a er load. Heller sende load_ts (ett stk!!) og evt ekstra params som valgfri
    if dict_config["modelling"]["perform_modelling"]:
        print("Modelling based on dataset", str_node_ID + "...")
        dict_model = modelling.model_load(
            dict_config["modelling"], dict_node_ts)
        dict_loads_ts[str_node_ID] = dict_model["load"]
    """
