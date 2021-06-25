import numpy as np

def remove_nan_and_none_datapoints(dict_data_ts):
    print("Removing NaN and None datapoints...")
    for data_source in dict_data_ts:
        ts_data = dict_data_ts[data_source]
        list_good_indeces = list(map(lambda dp: (not None in dp) and (dp == dp), ts_data))
        ts_data = ts_data[list_good_indeces]
        """
        ts_data = np.array(filter(lambda dp: not None in dp, ts_data))
        ts_data = np.array(filter(lambda dp: dp == dp, ts_data))
        """
        dict_data_ts[data_source] = ts_data
    return dict_data_ts

def datetime_to_yearless_iso_string(dt):
    return dt.isoformat()[5:10]

def compute_daily_historical_normal(ts_daily_data_historical):
    # Group each data point with other data-points on the same time-slot in an appropriate resolution.
    # Average the groups of data-points for each time-slot
    # Create new timeseries with (time-slot, data-point) for all time-slots.
    
    # This desperately needs optimization

    # Assumes daily data measurements
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

    print(dict_daily_average)
    return dict_daily_average

def correct_load_for_temperature_deviations(dict_config, dict_data_ts):
    print("Performing temperature-correction of load-data...")
    ts_load = dict_data_ts["load_measurements"] # These names are hard-code-y, perhaps rather search for type: load or type: temp?
    ts_temperature = dict_data_ts["temperature_measurements"]
    ts_temperature_historical = dict_data_ts["temperature_measurements_historical"]

    dict_daily_normal_temperature = compute_daily_historical_normal(ts_temperature_historical)

    return dict_data_ts



def preprocess_data(dict_config, dict_data_ts):
    print("Preprocessing data...")

    if dict_config["preprocessing"]["remove_NaN_and_None"]: dict_data_ts = remove_nan_and_none_datapoints(dict_data_ts)
    
    if dict_config["preprocessing"]["correct_for_temperature"]: dict_data_ts = correct_load_for_temperature_deviations(dict_config, dict_data_ts)

    # Format allows for simple pipelining of multiple preprocessing steps if needed.
    #if dict_config["preprocessing"]["example"]: dict_data_ts = example_preprocessing_step(dict_config, dict_data_ts)
    #if dict_config["preprocessing"]["another"]: dict_data_ts = another_preprocessing_step(dict_config, dict_data_ts)

    print("Successfully completed all preprocessing steps")
    return dict_data_ts