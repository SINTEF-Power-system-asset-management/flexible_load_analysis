import numpy as np
import datetime as dt


def remove_nan_and_none_datapoints(ts_data):
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
    ts_data = ts_data[list_good_indeces]
    return ts_data


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
    raise(Exception("End date missing from basis-timeseries"))


def correct_load_for_temperature_deviations(
        ts_load, 
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
    for i in range(len(ts_load)):
        arr_datapoint_i = ts_load[i]
        dt_time_i = arr_datapoint_i[0]
        fl_load_i = arr_datapoint_i[1]
        # Removed, but should in theory be performed according to Tønne
        # if 11 <= dt_time_i.month or dt_time_i.month <= 4:
        if True:
            Tn = dict_daily_normal_temperature[datetime_to_yearless_iso_string(
                dt_time_i)]
            Ti = dict_temperature_n_day_average[dt_time_i.date()]
            fl_load_corrected_i = fl_load_i + fl_load_i*k*x*(Tn - Ti)
        else:
            fl_load_corrected_i = fl_load_i

        ts_load_corrected[i][0] = dt_time_i
        ts_load_corrected[i][1] = fl_load_corrected_i

    return ts_load_corrected


def preprocess_data(dict_preprocessing_config, dict_data_ts):
    """Performs preprocessing on given data based on configuration.

    Parameters
    ----------
    dict_preprocessing_config : dict
        Dictionary of which preprocessing steps to perform.
    dict_data_ts : dict(timeseries)
        Timeseries to preprocess or to use for preprocessing purposes.

    Returns
    ----------
    dict_data_ts : dict(timeseries)
        Input-dictionary with backloaded preprocessed data and biproducts.

    Notes
    ----------
    Main functionality of this module.
    """
    print("Preprocessing data...")

    list_preprocessing_log = []

    if dict_preprocessing_config["remove_NaN_and_None"]:
        dict_data_ts["load_measurements"] = remove_nan_and_none_datapoints(dict_data_ts["load_measurements"])
        list_preprocessing_log.append("remove_nan_and_none")

    if dict_preprocessing_config["correct_for_temperature"]:
        ts_load = dict_data_ts["load_measurements"]
        dict_daily_normal_temperature = dict_data_ts["normal_temperature"]
        dict_temperature_3_day_average = dict_data_ts["n-day_average_temperature"]
        k = dict_preprocessing_config["k_temperature_coefficient"]
        x = dict_preprocessing_config["x_temperature_sensitivity"]

        dict_data_ts["load_temperature_corrected"] = correct_load_for_temperature_deviations(
            ts_load, 
            dict_daily_normal_temperature,
            dict_temperature_3_day_average,
            k, x)
        list_preprocessing_log.append("correct_for_temperature")

    # Format allows for simple pipelining of additional preprocessing steps.
    # if dict_preprocessing_config["example"]:
    #   dict_data_ts["field"] = example_preprocessing_step(dict_preprocessing_config, dict_data_ts["other_field"])
    # if dict_preprocessing_config["another"]:
    #   dict_data_ts["other_field"] = another_preprocessing_step(dict_preprocessing_config, dict_data_ts["yet_another_field"])

    if "correct_for_temperature" in list_preprocessing_log:
        dict_data_ts["load"] = dict_data_ts["load_temperature_corrected"]
    else:
        dict_data_ts["load"] = dict_data_ts["load_measurements"]

    print("Successfully completed all preprocessing steps")
    return dict_data_ts
