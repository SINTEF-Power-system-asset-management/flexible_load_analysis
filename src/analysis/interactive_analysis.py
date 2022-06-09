"""Module for interactively choose, perform - and store results from - a set
of accessible analyses.

Notes
----------
The container dict_results is carried throughout the interactive analysis as
a way to temporarily store results which may be used as a data-source for further
analysis in the future.

The functions for interactively performing analysis should be structured as follows:
1. Choose data-source and parameters interactively.
2. Perform analysis.
3. Present results graphically or numerically.
4. Interactively store results to file and/or sub-results-dictionary for ability to
perform some other analysis on results later.
"""
import objects.network as network
import plotting
import utilities
from analysis.methods import max_load, load_aggregation, load_duration_curve


# Interactive analysis

def interactive_max_load(dict_analysis_config, dict_results, dict_loads_ts):
    """Interactively calculate max load of timeseries
    """
    print("Beginning interactive max-load calculation")

    # 1. Choose data-source and parameters interactively.
    print("Choose timeseries to calculate max load of:")
    str_ID, ts_load = utilities.interactively_traverse_nested_dictionary(
        {
            "customers": dict_loads_ts,
            "results": dict_results
        }
    )

    # 2. Perform analysis.
    fl_max_load = max_load.find_max_load(ts_load)

    # 3. Present results graphically or numerically.
    print("Calculated the following max-load:",
          fl_max_load, "for load", str_ID)

    # 4. Interactively store results to file and/or sub-results-dictionary for ability to
    # perform some other analysis on results later.
    dict_results = utilities.interactively_insert_into_dictionary(
        dict_results, fl_max_load, "max load")
    str_results_directory_path = dict_analysis_config["result_storage_path"]
    utilities.interactively_write_to_file_in_directory(
        str_results_directory_path, fl_max_load)

    return dict_results


def interactive_load_aggregation(dict_analysis_config, dict_results, dict_loads_ts, g_network):
    """Interactively perform load-aggregation
    """
    print("Beginning interactive load-aggregation")

    # 1. Choose data-source and parameters interactively.
    print("Nodes in network: ")
    print(network.list_nodes(g_network))
    print("What node should the aggregation be done from?")
    str_load_ID = network.input_until_node_in_network_appears(g_network)
    print("What node should be the reference node?")
    str_ref_ID = network.input_until_node_in_network_appears(g_network)

    # 2. Perform analysis.
    ts_agg = load_aggregation.aggregate_load_of_node(
        str_load_ID, dict_loads_ts, g_network, str_ref_ID)

    # 3. Present results graphically or numerically.
    print("Got the following aggregated load at node", str_load_ID)
    plotting.plot_timeseries(
        [ts_agg], ["Aggregated load"],
        "Time", "Load", "Aggregated load")

    # 4. Interactively store results to file and/or sub-results-dictionary for ability to
    # perform some other analysis on results later.
    dict_results = utilities.interactively_insert_into_dictionary(
        dict_results, ts_agg, "aggregated load")
    str_results_directory_path = dict_analysis_config["result_storage_path"]
    utilities.interactively_write_to_file_in_directory(
        str_results_directory_path, ts_agg)

    return dict_results


def interactive_load_duration_curve(dict_analysis_config, dict_results, dict_loads_ts):
    """Interactively create load-duration-curves
    """
    print("Beginning interactive creation of load-duration")

    # 1. Choose data-source and parameters interactively.
    print("Choose timeseries to create load-duration curve of:")
    str_ID, ts_load = utilities.interactively_traverse_nested_dictionary(
        {
            "customers": dict_loads_ts,
            "results": dict_results
        }
    )
    print("Input limit of relevant line load is connected to (input 0 to skip):")
    inp = utilities.input_until_expected_type_appears(float)
    fl_limit = inp if inp else None

    # 2. Perform analysis.
    ldc = load_duration_curve.create_load_duration_curve(ts_load)

    # 3. Present results graphically or numerically.
    plotting.plot_load_duration_curve(ldc, fl_limit=fl_limit)

    # 4. Interactively store results to file and/or sub-results-dictionary for ability to
    # perform some other analysis on results later.
    dict_results = utilities.interactively_insert_into_dictionary(
        dict_results, ldc, "load duration curve")
    str_results_directory_path = dict_analysis_config["result_storage_path"]
    utilities.interactively_write_to_file_in_directory(
        str_results_directory_path, ldc)

    return dict_results


def interactively_inspect_previous_results(dict_results):
    """Interactively inspect results
    """
    print("Beginning inspection of results")

    bool_continue = True
    while bool_continue:
        key, result = utilities.interactively_traverse_nested_dictionary(
            dict_results)
        print(key, ":", result)

        print("Continue inspecting previous results?")
        str_choice = utilities.input_until_acceptable_response(["y", "n"])
        if str_choice == "n":
            bool_continue = False

    return


# Top level function

def interactively_choose_analysis(dict_config, dict_results, dict_loads_ts, g_network):
    print("Beggining interactive analysis")
    dict_analysis_config = dict_config["analysis"]

    bool_continue = True
    while bool_continue:

        print(28 * "-", "ANALYSIS", 28 * "-")
        print("1: Max load calculation")
        print("2: Load-aggregation")
        print("3: Power-flow-analysis (not yet implemented)")
        print("4: Load-duration curve")
        print("8: Inspect previous results")
        print("9: Exit analysis")
        print(67 * "-")

        str_choice = input()

        if str_choice == '1':
            dict_results = interactive_max_load(
                dict_analysis_config, dict_results, dict_loads_ts)
        elif str_choice == '2':
            dict_results = interactive_load_aggregation(
                dict_analysis_config, dict_results, dict_loads_ts, g_network)
        elif str_choice == '3':
            print("Not yet implemented")
        elif str_choice == '4':
            dict_results = interactive_load_duration_curve(
                dict_analysis_config, dict_results, dict_loads_ts
            )
        elif str_choice == '8':
            interactively_inspect_previous_results(dict_results)
        elif str_choice == '9':
            print("Exiting interactive analysis!")
            bool_continue = False
        else:
            print("Input not recognized, try again!")

    return dict_results
