import numpy as np
import datetime as dt

def remove_nan_and_none_datapoints(dict_data_ts):
    print("Removing NaN and None datapoints...")
    for data_source in dict_data_ts:
        ts_data = dict_data_ts[data_source]
        list_good_indeces = []
        for dp in ts_data:
            dp = list(dp)
            if (not None in dp) and (dp == dp):
                list_good_indeces.append(True)
            else:
                list_good_indeces.append(False)
        ts_data = ts_data[list_good_indeces]
        dict_data_ts[data_source] = ts_data
    return dict_data_ts



def datetime_to_yearless_iso_string(dt):
    return dt.isoformat()[5:10]

def compute_daily_historical_normal(ts_daily_data_historical):
    # Assumes daily data measurements
    # Warning: Does not guarantee the output dictionary is chronologically ordered.
    # Example: Datasets which begin at non-leapyears will have "02-29" as the last entry in the output dictionary.
    dict_running_sum_and_count = {}
    for i in range(len(ts_daily_data_historical)):
        arr_cur_data = ts_daily_data_historical[i,:]
        str_date_yearless = datetime_to_yearless_iso_string(arr_cur_data[0])
        flt_cur_sum = dict_running_sum_and_count.get(str_date_yearless, [0, 0])[0]
        int_cur_count = dict_running_sum_and_count.get(str_date_yearless, [0, 0])[1]
        list_new_sum_and_count = [flt_cur_sum + arr_cur_data[1], int_cur_count + 1]
        dict_running_sum_and_count[str_date_yearless] = list_new_sum_and_count
    
    dict_daily_average = {}
    for key in dict_running_sum_and_count:
        dict_daily_average[key] = dict_running_sum_and_count[key][0] / dict_running_sum_and_count[key][1]
    return dict_daily_average

def compute_n_day_average_starting_from(dt_start_day, ts_daily_data, n):
    int_index = 0
    while int_index < len(ts_daily_data):
        if ts_daily_data[int_index][0].day == dt_start_day.day and ts_daily_data[int_index][0].month == dt_start_day.month:
            break
        else:
            int_index += 1

    fl_running_sum = 0
    i = 0
    while i < n:
        fl_running_sum += ts_daily_data[int_index - i][1]
        i += 1
    return fl_running_sum / n

def correct_load_for_temperature_deviations(dict_config, dict_data_ts):
    print("Performing temperature-correction of load-data...")

    # Parameters
    ts_load = dict_data_ts["load_measurements"]
    ts_temperature = dict_data_ts["temperature_measurements"]
    ts_temperature_historical = dict_data_ts["temperature_measurements_historical"]
    k = dict_config["preprocessing"]["k_temperature_coefficient"]
    x = dict_config["preprocessing"]["x_temperature_sensitivity"]
    dict_daily_normal_temperature = compute_daily_historical_normal(ts_temperature_historical)

    # Correction step
    ts_load_corrected = np.zeros_like(ts_load)
    for i in range(len(ts_load)):
        arr_datapoint_i = ts_load[i]
        dt_time_i = arr_datapoint_i[0]
        fl_load_i = arr_datapoint_i[1]
        #if 11 <= dt_time_i.month or dt_time_i.month <= 4:      # Removed, but should in theory be performed according to Tønne
        if True:
            Tn = dict_daily_normal_temperature[datetime_to_yearless_iso_string(dt_time_i)]
            Ti = compute_n_day_average_starting_from(dt_time_i, ts_temperature, n=3)
            fl_load_corrected_i = fl_load_i + fl_load_i*k*x*(Tn - Ti)
        else:
            fl_load_corrected_i = fl_load_i
        
        ts_load_corrected[i][0] = dt_time_i
        ts_load_corrected[i][1] = fl_load_corrected_i

    # Backloading new data
    dict_data_ts["temperature_daily_normal"] = dict_daily_normal_temperature
    dict_data_ts["load_temperature_corrected"] = ts_load_corrected
    return dict_data_ts



def preprocess_data(dict_config, dict_data_ts):
    print("Preprocessing data...")

    list_preprocessing_log = []

    if dict_config["preprocessing"]["remove_NaN_and_None"]: 
        dict_data_ts = remove_nan_and_none_datapoints(dict_data_ts)
        list_preprocessing_log.append("remove_nan_and_none")
    
    if dict_config["preprocessing"]["correct_for_temperature"]: 
        dict_data_ts = correct_load_for_temperature_deviations(dict_config, dict_data_ts)
        list_preprocessing_log.append("correct_for_temperature")

    # Format allows for simple pipelining of multiple preprocessing steps if needed.
    #if dict_config["preprocessing"]["example"]: dict_data_ts = example_preprocessing_step(dict_config, dict_data_ts)
    #if dict_config["preprocessing"]["another"]: dict_data_ts = another_preprocessing_step(dict_config, dict_data_ts)

    if "correct_for_temperature" in list_preprocessing_log:
        dict_data_ts["load"] = dict_data_ts["load_temperature_corrected"]
    else:
        dict_data_ts["load"] = dict_data_ts["load_measurements"]

    print("Successfully completed all preprocessing steps")
    return dict_data_ts