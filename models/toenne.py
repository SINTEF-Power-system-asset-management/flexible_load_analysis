import numpy as np
from numpy.lib.shape_base import _kron_dispatcher

# Module for implementing Tønne's load modeling method. 
# Requires input measured load to be compensated for temperature.

def generate_deterministic_model(ts_measured_load, str_max_or_average_variation, str_variation_value_alternative):
    # Implements both step 2 and 3 og Tønne.

    # Initialization of empty data containers
    if str.lower(str_variation_value_alternative) == "a":
            dict_variation_values = {
                "monthly": [[] for _ in range(12)],
                "workday_hourly": [[] for _ in range(24)],
                "weekend_hourly": [[] for _ in range(24)]
            }
    elif str.lower(str_variation_value_alternative) == "b":
        dict_variation_values = {
            "workday_monthly" : [ [ [] for _ in range(24) ] for _ in range(12)],
            "weekend_monthly" : [ [ [] for _ in range(24) ] for _ in range(12)]
        }
    else:
        raise Exception("Unsupported variation value alternative")    


    # Step 2a, categorize
    for i in range(len(ts_measured_load)):
        dt_time_i = ts_measured_load[i, 0]
        fl_load_i = ts_measured_load[i, 1]
        int_month_i = dt_time_i.month
        int_hour_i = dt_time_i.hour
        bool_date_is_workday = (dt_time_i.weekday() < 5)

        # This may seem magical, requires good documentation
        if str.lower(str_variation_value_alternative) == "a":
            dict_variation_values["monthly"][int_month_i - 1].append(fl_load_i)
            if bool_date_is_workday:
                dict_variation_values["workday_hourly"][int_hour_i].append(fl_load_i)
            else:
                dict_variation_values["weekend_hourly"][int_hour_i].append(fl_load_i)
        
        elif str.lower(str_variation_value_alternative) == "b":
            if bool_date_is_workday:
                dict_variation_values["workday_monthly"][int_month_i - 1][int_hour_i].append(fl_load_i)
            else:
                dict_variation_values["weekend_monthly"][int_month_i - 1][int_hour_i].append(fl_load_i)

        else:
            raise Exception("Unsupported variation value alternative")


    # Step 2b, calculate variation
    if str.lower(str_max_or_average_variation) == "max":
        fn_variation_baseline = np.average
    elif str.lower(str_max_or_average_variation) == "average":
        fn_variation_baseline = np.max
    else:
        raise Exception("Unsupported method for calculating variation")

    fl_normalization_baseline = fn_variation_baseline(ts_measured_load[:,1])

    if str.lower(str_variation_value_alternative) == "a":
        for category in dict_variation_values:
            dict_variation_values[category] = list(map(lambda arr: fn_variation_baseline(arr) / fl_normalization_baseline, dict_variation_values[category]))
    elif str.lower(str_variation_value_alternative) == "b":
        for category in dict_variation_values:
            for month in range(12):
                dict_variation_values[category][month] = list(map(lambda arr: fn_variation_baseline(arr) / fl_normalization_baseline, dict_variation_values[category][month]))
    else:
        raise Exception("Unsupported variation value alternative")    


    # Step 3, generate deterministic model
    ts_load_deterministic_model = []
    for i in range(len(ts_measured_load)):
        dt_time_i = ts_measured_load[i, 0]
        int_month_i = dt_time_i.month
        int_hour_i = dt_time_i.hour
        bool_date_is_workday = (dt_time_i.weekday() < 5)

        fl_modelled_load_i = fl_normalization_baseline
        if str.lower(str_variation_value_alternative) == "a":
            fl_modelled_load_i *= dict_variation_values["monthly"][int_month_i - 1]
            if bool_date_is_workday:
                fl_modelled_load_i *= dict_variation_values["workday_hourly"][int_hour_i]
            else:
                fl_modelled_load_i *= dict_variation_values["weekend_hourly"][int_hour_i]

        elif str.lower(str_variation_value_alternative) == "b":
            if bool_date_is_workday:
                fl_modelled_load_i *= dict_variation_values["workday_monthly"][int_month_i - 1][int_hour_i]
            else:
                fl_modelled_load_i *= dict_variation_values["weekend_monthly"][int_month_i - 1][int_hour_i]
        else:
            raise Exception("Unsupported variation value alternative")
        
        ts_load_deterministic_model.append([dt_time_i, fl_modelled_load_i])

    return np.array(ts_load_deterministic_model), dict_variation_values


def create_toenne_load_model(dict_data_ts, dict_parameters):
    print("Performing Tønne-modelling...")

    # Step 1 of Tønne is inherent in the load already being 
    ts_measured_load = dict_data_ts["load"]
    str_max_or_average_variation = dict_parameters["max_or_average_variation_calculation"]
    str_variation_value_alternative = dict_parameters["variation_values_alternative"]

    # Step 2 and 3 of Tønne
    ts_load_deterministic_model, dict_variation_values = generate_deterministic_model(ts_measured_load, str_max_or_average_variation, str_variation_value_alternative)

    # Step 4 of Tønne
    # Todo: felles/individuelt avvik
    ts_relative_model_error = []
    for i in range(len(ts_measured_load)):
        dt_time_i = ts_measured_load[i, 0]
        fl_actual_load_i = ts_measured_load[i, 1]
        fl_modelled_load_i = ts_load_deterministic_model[i, 1]
        fl_relative_error_i = (fl_actual_load_i - fl_modelled_load_i) / fl_modelled_load_i
        ts_relative_model_error.append([dt_time_i, fl_relative_error_i])
    ts_relative_model_error = np.array(ts_relative_model_error)

    # Step 5 of Tønne
    # Todo

    dict_model = {}
    dict_model["load"] = ts_load_stochastic_model  # Model timeseries
    dict_model["biproducts"] = {}    # Dictionary of biproducts from modelling
    return dict_model