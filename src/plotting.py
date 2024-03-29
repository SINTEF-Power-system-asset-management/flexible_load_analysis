"""Module for plotting figures selected in config.

Run plot_selected to plot these figures.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from calendar import month_abbr
import utilities as util
from flexibility.flexibility_need import metric_annotation


def plot_timeseries(list_ts, list_labels, str_title, str_xlabel="Date", str_ylabel="Load [kW]", fl_limit=None):
    fig, ax = plt.subplots(figsize=(10, 6))
    for i in range(len(list_ts)):
        ts = list_ts[i]
        arr_time = ts[:, 0]
        arr_data = ts[:, 1]
        ax.plot(arr_time, arr_data, label=list_labels[i])
    if fl_limit:
        ax.plot([arr_time[0], arr_time[-1]], [fl_limit, fl_limit], "--", color="g", label="Limit")

    ax.set_xlabel(str_xlabel)
    ax.set_ylabel(str_ylabel)
    ax.set_title(str_title)
    ax.grid(True)
    ax.legend(loc='upper left')
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=30))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=90)
    plt.tight_layout()
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


def plot_variation_curves(dict_variation_values, str_variation_value_alternative):
    if str.lower(str_variation_value_alternative) == 'a':
        arr_monthly_variation = dict_variation_values["monthly"]
        arr_hourly_variation_workday = dict_variation_values["workday_hourly"]
        arr_hourly_variation_weekend = dict_variation_values["weekend_hourly"]

        _, ax1 = plt.subplots(figsize=(10, 6))
        arr_months = [month_abbr[i] for i in range(1, 13)]
        ax1.plot(arr_months, arr_monthly_variation, label="Load variation")
        ax1.set_xlabel("Month")
        ax1.set_ylabel("Variation from normal")
        ax1.set_title("Monthly load variation")
        ax1.grid(True)
        ax1.legend(loc='upper left')

        _, ax2 = plt.subplots(figsize=(10, 6))
        arr_hours = [i for i in range(1, 25)]
        ax2.plot(arr_hours, arr_hourly_variation_workday, label="Workday")
        ax2.plot(arr_hours, arr_hourly_variation_weekend, label="Weekend")
        ax2.set_xlabel("Hour")
        ax2.set_ylabel("Variation from normal")
        ax2.set_title("Hourly load variation, workday vs. weekend")
        ax2.grid(True)
        ax2.legend(loc='upper left')

        plt.show()

    elif str.lower(str_variation_value_alternative) == 'b':
        arr_monthly_hourly_variation_workday = dict_variation_values["workday_monthly"]
        arr_monthly_hourly_variation_weekend = dict_variation_values["weekend_monthly"]

        fig, (ax0, ax1) = plt.subplots(nrows=2)

        im0 = ax0.pcolormesh(arr_monthly_hourly_variation_workday)
        fig.colorbar(im0, ax=ax0)
        ax0.set_xlabel("Hour")
        ax0.set_ylabel("Month")
        ax0.set_title("Hourly load variation workdays")

        im1 = ax1.pcolormesh(arr_monthly_hourly_variation_weekend)
        fig.colorbar(im1, ax=ax1)
        ax1.set_xlabel("Hour")
        ax1.set_ylabel("Month")
        ax1.set_title("Hourly load variation weekends")

        plt.show()
    else:
        raise Exception("Unsupported variation value alternative")
    return


def plot_deterministic_load(ts_deterministic_model, str_variation_value_alternative):
    """Plots the deterministic model for a week when variation value alternative
    A is chosen, or a week for each month if B is chosen.

    Warning
    ----------
    Doesn't work as intended.
    """
    if str.lower(str_variation_value_alternative) == 'a':
        # Finding the first datapoint on a monday
        int_first_monday_index = util.first_matching_index(
            ts_deterministic_model[:, 0], lambda dt: dt.weekday() == 0)

        # Finding the second monday
        dt_first = ts_deterministic_model[int_first_monday_index, 0]
        int_second_monday_index = util.first_matching_index(
            ts_deterministic_model[:, 0], lambda dt: dt.weekday() == 0 and dt.date() != dt_first.date())

        fig, ax = plt.subplots(figsize=(10, 6))
        ts = ts_deterministic_model[int_first_monday_index:(
            int_second_monday_index-1), :]
        arr_time = ts[:, 0]
        arr_data = ts[:, 1]
        ax.plot(arr_time, arr_data, label="Deterministic model")

        ax.set_xlabel("Time")
        ax.set_ylabel("Load [kW]")
        ax.set_title("Deterministic model for one week")
        ax.grid(True)
        ax.legend(loc='upper left')
        ax.xaxis.set_major_locator(mdates.DayLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=90)

        plt.show()

    elif str.lower(str_variation_value_alternative) == 'b':
        fig, ax = plt.subplots(figsize=(10, 6))

        int_first_monday_index = util.first_matching_index(
            ts_deterministic_model[:, 0], lambda dt: dt.weekday() == 0)
        dt_first_monday = ts_deterministic_model[int_first_monday_index, 0]
        int_second_monday_index = util.first_matching_index(
            ts_deterministic_model[:, 0], lambda dt: dt.weekday() == 0 and dt.date() != dt_first_monday.date())

        ts = ts_deterministic_model[int_first_monday_index:(
            int_second_monday_index-1), :]
        arr_time = ts[:, 0]
        arr_days = [dt.strftime("%A %H:%M:%S") for dt in arr_time]
        arr_data = ts[:, 1]
        ax.plot(arr_days, arr_data, label=dt_first_monday.strftime("%B"))

        int_previous_monday_index = int_first_monday_index
        dt_previous_monday = dt_first_monday
        int_months_plotted = 1
        while int_months_plotted < 12:
            int_first_monday_of_month_index = util.first_matching_index(
                ts_deterministic_model[int_previous_monday_index:, 0], lambda dt: dt.weekday() == 0 and dt.month != dt_previous_monday.month)
            dt_first_monday = ts_deterministic_model[int_first_monday_of_month_index, 0]
            int_second_monday_index = util.first_matching_index(
                ts_deterministic_model[int_previous_monday_index:, 0], lambda dt: dt.weekday() == 0 and dt.date() != dt_first_monday.date())

            ts = ts_deterministic_model[int_previous_monday_index+int_first_monday_of_month_index:(
                int_previous_monday_index+int_second_monday_index-1), :]
            arr_time = ts[:, 0]
            arr_days = [dt.strftime("%A %H:%M:%S") for dt in arr_time]
            arr_data = ts[:, 1]
            ax.plot(arr_days, arr_data, label=dt_first_monday.strftime("%B"))

            int_previous_monday_index = int_first_monday_of_month_index + int_previous_monday_index
            dt_previous_monday = dt_first_monday
            int_months_plotted += 1

        ax.set_xlabel("Time")
        ax.set_ylabel("Load [kW]")
        ax.set_title("Deterministic model for one week of each month")
        ax.grid(True)
        ax.legend(loc='upper left')
        ax.xaxis.set_major_locator(mdates.DayLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=90)

        plt.show()
    else:
        raise Exception("Unsupported variation value alternative")
    return

### Init and plot


def init_plotting(dict_parameters):
    plt.rcParams.update({"font.size": dict_parameters["font_size"]})
    return


def plot_selection(dict_config, dict_data_ts, dict_model):
    print("Do you want to skip plotting (No)/Yes?")
    str_input = str.lower(input())
    if str_input == 'y' or str_input == 'yes':
        print("Skipping plotting")
        return

    dict_plotting_parameters = dict_config["plotting"]
    dict_plot_decider_bool = dict_plotting_parameters["plots_to_be_made"]
    init_plotting(dict_plotting_parameters)

    print("Plotting figures specified in config.toml...")
    if dict_plot_decider_bool["load_measurements"]:
        plot_timeseries([dict_data_ts["load_measurements"]], [
                        "Measured load"], "Time", "Load [kW]", "Load measurements")
    if dict_plot_decider_bool["load_measurements_histogram"]:
        plot_histogram(dict_data_ts["load_measurements"][:, 1],
                       "Load [kW]", "Occurences", "Load measurement histogram")
    if dict_plot_decider_bool["temperature_measurements"]:
        plot_timeseries(
            [dict_data_ts["temperature_measurements"]], 
            ["Measured temperature"], 
            "Time", 
            "Temperature [°C]", 
            "Temperature measurements")
    if dict_plot_decider_bool["load_measurements_before_and_after_temperature_correction"]:
        plot_timeseries(
            [dict_data_ts["load_measurements"], dict_data_ts["load_temperature_corrected"]],
            ["Measured load", "Temperature-corrected load"],
            "Time",
            "Load [kW]",
            "Load measurements before and after temperature correction")

    if dict_config["modelling"]["chosen_model"] == "toenne":
        str_variation_value_alternative = dict_config["modelling"]["toenne"]["variation_values_alternative"]

        if dict_plot_decider_bool["variation_curves"]:
            plot_variation_curves(
                dict_model["biproducts"]["variation_values"],
                str_variation_value_alternative)
        # Doesn't work
        if dict_plot_decider_bool["deterministic_model"]:
            plot_deterministic_load(
                dict_model["biproducts"]["deterministic_model"], 
                str_variation_value_alternative)
        if dict_plot_decider_bool["load_measurements_and_deterministic_model"]:
            plot_timeseries(
                [dict_data_ts["load_temperature_corrected"], dict_model["biproducts"]["deterministic_model"]],
                ["Temperature-corrected load", "Deterministic model"],
                "Time",
                "Load [kW]",
                "Measured load vs. deterministic load model"
            )
        if dict_plot_decider_bool["relative_error"]:
            plot_timeseries(
                [dict_model["biproducts"]["error_timeseries"]], 
                ["Relative model error"], 
                "Time", 
                "Error", 
                "Relative model error (measurements vs determinisitc model)")
        if dict_plot_decider_bool["relative_error_histogram"]:
            plot_histogram(dict_model["biproducts"]["error_timeseries"][:, 1],
                           "Error", "Occurences", "Relative model error histogram")
        if dict_plot_decider_bool["load_measurements_and_stochastic_model"]:
            plot_timeseries(
                [dict_data_ts["load_temperature_corrected"], dict_model["load"]],
                ["Measured load", "Stochastic model"],
                "Time",
                "Load [kW]",
                "Temperature-corrected load measurements vs stochastic model (single run)"
            )
    print("Successfully completed all plots")
    return


# Plot flexibility

def plot_flexibility_histograms(flex_need):
    arrs = flex_need.extract_arrays()

    l_metrics = [metric for metric in arrs]
    num_sides = int(np.ceil(np.sqrt(len(l_metrics))))

    fix,axs = plt.subplots(num_sides,num_sides,sharey=True,constrained_layout=True)

    stop = False
    for i in range(num_sides):
        for j in range(num_sides):
            index = i * num_sides + j
            if index >= len(l_metrics): 
                stop = True
                break
            metric = l_metrics[index]
            axs[i, j].hist(arrs[metric], bins='auto')
            axs[i, j].set_xlabel(metric_annotation(metric))
            axs[i, j].set_ylabel("Counts")

            if metric == "recovery":
                days_to_ignore = 10
                num_ignored = np.count_nonzero(arrs[metric] > days_to_ignore*24)
                if num_ignored > 0:
                    right_lim = np.max(arrs[metric][arrs[metric] <= days_to_ignore*24])
                    axs[i, j].set_xlim(left=-1,right=right_lim)
                    print(f"Warning: {num_ignored} data-points not displayed because recovery-time succeeded {days_to_ignore} days")

    plt.show()

def plot_flexibility_clustering(flex_need):
    arrs = flex_need.extract_arrays()

    l_metric_combos = util.all_unordered_pairs([metric for metric in arrs])
    num_sides = int(np.ceil(np.sqrt(len(l_metric_combos))))

    fix,axs = plt.subplots(num_sides,num_sides,constrained_layout=True)

    stop = False
    for i in range(num_sides):
        for j in range(num_sides):
            index = i * num_sides + j
            if index >= len(l_metric_combos): 
                stop = True
                break
            (first, last) = l_metric_combos[index]
            axs[i, j].scatter(arrs[first], arrs[last])
            axs[i, j].set_xlabel(metric_annotation(first))
            axs[i, j].set_ylabel(metric_annotation(last))

            if first == "recovery" or last == "recovery":
                metric = first if first == "recovery" else last
                
                days_to_ignore = 10
                num_ignored = np.count_nonzero(arrs[metric] > days_to_ignore*24)
                if num_ignored > 0:
                    upper_lim = np.max(arrs[metric][arrs[metric] <= days_to_ignore*24])

                    if metric == first:
                        axs[i, j].set_xlim(left=-1,right=upper_lim)
                    else: 
                        axs[i, j].set_ylim(bottom=-1,top=upper_lim)
                    
                    print(f"Warning: {num_ignored} data-points not displayed because recovery-time succeeded {days_to_ignore} days")
            

        if stop: break
            
    plt.show()
    """
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.scatter(arrs["energy"], arrs["ramping"], arrs["energy"])
    ax.set_xlabel('Duration [h]')
    ax.set_ylabel('Ramp [kW/h]')
    ax.set_zlabel('Energy [kWh]')
    """
    
    plt.show()



def plot_load_duration_curve(ldc, fl_limit=None):
    fig, ax = plt.subplots(figsize=(10, 6))
    arr_time = ldc[:, 0]
    arr_data = ldc[:, 1]
    ax.plot(arr_time, arr_data, label="Load duration curve")
    if fl_limit:
        ax.plot([arr_time[0], arr_time[-1]], [fl_limit, fl_limit], "--", color="g", label="Limit")

    ax.set_xlabel("Number")
    ax.set_ylabel("Load [MW]")
    ax.set_title("Load duration curve")
    ax.grid(True)
    ax.legend(loc='upper right')

    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()