"""Module for implementing analysis which may be performed.

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
import network
import load_points
import plotting
import utilities
import numpy as np

# Helper function

def input_until_expected_type_appears(type):
    print("Please input a", type)
    while True:
        inp = input()
        try:
            type_variable = type(inp)
            return type_variable
        except ValueError:
            print("Input failed, try again")


def interactively_traverse_nested_dictionary(dict_choices):

    print("\nAvailable files: ")
    print()
    utilities.print_dictionary_recursive(dict_choices)
    
    bool_successful_input = False
    while not bool_successful_input:
        print("\nInput key of data-source to follow")
        str_key = str(input())
        if str_key not in dict_choices:
            print("Could not find key, try again")
        else:
            bool_successful_input = True
    if type(dict_choices[str_key]) == dict:
        str_final_key, data = interactively_traverse_nested_dictionary(dict_choices[str_key])
    else:
        str_final_key = str_key
        data = dict_choices[str_key]
    return str_final_key, data


def interactively_insert_into_dictionary(dict_content, new_content, str_content_description):  # kan sikker kutte str_content_description
    print("The following keys are already stored:")
    for key in dict_content:
        print(key)

    bool_successfully_input = False
    while not bool_successfully_input:
        print("Input name to store", str_content_description, "under (leave blank to abort)")
        str_name = str(input())
        if not str_name:
            print("Aborting storage!")
            return dict_content
        elif str_name in dict_content:
            print("Name is already in use, try again")
        else:
            dict_content[str_name] = new_content
            bool_successfully_input = True
            print("Successfully stored", str_content_description)
    return dict_content


def interactively_write_to_file_in_directory(str_results_directory_path, result):
    print("Not yet implemented!")
    return


# Analysis

def max_load(ts_load):
    return np.max(ts_load[:,1])

def aggregate_load_of_node(str_load_ID, dict_loads_ts, g_network):
    """Finds timeseries of total load experienced by a node.

    Parameters:
    ----------
    str_load_ID : node-name
        Node which to aggregate load at.
    dict_loads_ts : nodes
        Container indexable by node-names of load-timeseries at that node.
    g_network : graph
        Directed graph of network-topology of loads.

    Returns:
    ----------
    ts_sum : timeseries
        Calculated aggregated load at str_load_ID.

    Notes:
    ----------
    Will calculate recursively, stopping at nodes which have no children which
    are then treated as customers.

    """
    if not str_load_ID in g_network:
        raise Exception("Error: Node missing from network")
    list_children = network.list_children_of_node(str_load_ID, g_network)

    ts_sum = []
    try:
        ts_sum = dict_loads_ts[str(str_load_ID)]
    except KeyError:
            print("Warning: Load-point", str_load_ID, "is missing timeseries!")
            ts_sum = []
    if list_children:    
        for n_child in list_children:
            ts_child = aggregate_load_of_node(n_child, dict_loads_ts, g_network)
            ts_sum = load_points.add_timeseries(ts_sum, ts_child)
    return ts_sum


# Interactive analysis

def interactive_max_load(dict_analysis_config, dict_results, dict_loads_ts):
    print("Beginning interactive max-load calculation")

    #1. Choose data-source and parameters interactively.
    print("Choose timeseries to calculate max load of:")
    str_ID, ts_load = interactively_traverse_nested_dictionary(
        {
            "customers" : dict_loads_ts,
            "previous_results" : dict_results
        }
    )

    #2. Perform analysis.
    fl_max_load = max_load(ts_load)

    #3. Present results graphically or numerically.
    print("Calculated the following max-load:", fl_max_load, "for load", str_ID)

    #4. Interactively store results to file and/or sub-results-dictionary for ability to
    #perform some other analysis on results later.
    dict_results = interactively_insert_into_dictionary(dict_results, fl_max_load, "max load")
    str_results_directory_path = dict_analysis_config["result_storage_path"]
    interactively_write_to_file_in_directory(str_results_directory_path, fl_max_load)

    return dict_results


def interactive_load_aggregation(dict_analysis_config, dict_results, dict_loads_ts, g_network):
    print("Beginning interactive load-aggregation")
    
    #1. Choose data-source and parameters interactively.
    bool_successfully_input_node_of_network = False
    while not bool_successfully_input_node_of_network:
        print("Nodes in network: ")
        print(network.list_nodes(g_network))
        print("What node should the aggregation be done from?")
        str_load_ID = input_until_expected_type_appears(str)
        if str_load_ID in g_network:
            bool_successfully_input_node_of_network = True
        else:
            print("Could not find", str_load_ID, "in network, try again!")
    
    #2. Perform analysis.
    ts_agg = aggregate_load_of_node(str_load_ID, dict_loads_ts, g_network)

    #3. Present results graphically or numerically.
    print("Got the following aggregated load at node", str_load_ID)
    plotting.plot_timeseries(
        [ts_agg], ["Aggregated load"], 
        "Time", "Load", "Aggregated load")

    #4. Interactively store results to file and/or sub-results-dictionary for ability to
    #perform some other analysis on results later.
    dict_results = interactively_insert_into_dictionary(dict_results, ts_agg, "aggregated load")
    str_results_directory_path = dict_analysis_config["result_storage_path"]
    interactively_write_to_file_in_directory(str_results_directory_path, ts_agg)

    return dict_results


def interactively_choose_analysis(dict_config, dict_results, dict_loads_ts, g_network):
    print("Beggining interactive analysis")
    dict_analysis_config = dict_config["analysis"]

    bool_continue = True
    while bool_continue:

        print(28 * "-", "ANALYSIS", 28 * "-")
        print("1: Max load calculation")
        print("2: Load-aggregation")
        print("3: Power-flow-analysis (not yet implemented)")
        print("9: Exit analysis")
        print(67 * "-")

        str_choice = input()

        if str_choice == '1':
            dict_results = interactive_max_load(dict_analysis_config, dict_results, dict_loads_ts)
        elif str_choice == '2':
            dict_results = interactive_load_aggregation(dict_analysis_config, dict_results, dict_loads_ts, g_network)
        elif str_choice == '3':
            print("Not yet implemented")
        elif str_choice == '9':
            print("Exiting interactive analysis!")
            bool_continue = False
        else:
            print("Input not recognized, try again!")

    return dict_results
