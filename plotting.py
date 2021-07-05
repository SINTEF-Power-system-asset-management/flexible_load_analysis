import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_timeseries(list_ts, list_labels, str_xlabel, str_ylabel, str_title):
    fig, ax = plt.subplots(figsize=(10, 6))
    for i in range(len(list_ts)):
        ts = list_ts[i]
        arr_time = ts[:,0]
        arr_data = ts[:,1]
        ax.plot(arr_time, arr_data, label=list_labels[i])

    ax.set_xlabel(str_xlabel)
    ax.set_ylabel(str_ylabel)
    ax.set_title(str_title)
    ax.grid(True)
    ax.legend(loc='upper left')
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=20))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d')) #dict_parameters["date_format"]
    plt.xticks(rotation=90)

    plt.show()
    return

def plot_histogram(arr, str_xlabel, str_ylabel, str_title):
    plt.hist(
        arr,
        bins=int(np.ceil(np.sqrt(len(arr)))))
    
    plt.xlabel(str_xlabel)
    plt.ylabel(str_ylabel)
    plt.title(str_title)
    plt.grid(True)
    plt.show()
    return


### Init and plot
### Plotting of datasets to be implemented:
# [x] Load measurements
# [x] Histogram of load measurements
# [x] Measured temperature (short time horizon)
# [x] Load before and after temperature-correction
# [] Variation curves by month/hour of day/etc
# [] Deterministic model for a week (model choice A) or for a week for each month (model chioce B)
# [] Temp-corr. load and deterministic model
# [] Relative error
# [] Histogram of relative error
# [] Stochastic load vs. measured load

def init_plotting(dict_parameters):
    plt.rcParams.update({"font.size": dict_parameters["font_size"]})
    return

def plot_selected(dict_config, dict_data_ts, dict_model):       # Bad name
    print("Do you want to skip plotting (No)/Yes?")
    str_input = str.lower(input())
    if str_input == 'y' or str_input == 'yes':
        print("Skipping plotting")
        return

    print("Plotting figures specified in config.toml...")
    dict_plotting_parameters = dict_config["plotting"]
    dict_plot_decider_bool = dict_plotting_parameters["plots_to_be_made"]
    init_plotting(dict_plotting_parameters)

    if dict_plot_decider_bool["load_measurements"]: plot_timeseries([dict_data_ts["load_measurements"]], ["Measured load"], "Time", "Load [kW]", "Load measurements")

    if dict_plot_decider_bool["load_measurements_histogram"]: plot_histogram(dict_data_ts["load_measurements"][:,1], "Load [kW]", "Occurences", "Load measurement histogram")

    if dict_plot_decider_bool["temperature_measurements"]: plot_timeseries([dict_data_ts["temperature_measurements"]], ["Measured temperature"], "Time", "Temperature [°C]", "Temperature measurements")

    if dict_plot_decider_bool["load_measurements_before_and_after_temperature_correction"]: plot_timeseries(
        [dict_data_ts["load_measurements"], dict_data_ts["load_temperature_corrected"]],
        ["Measured load", "Temperature-corrected load"],
        "Time",
        "Load [kW]",
        "Load measurements before and after temperature correction")

    print("Successfully completed all plots")
    return