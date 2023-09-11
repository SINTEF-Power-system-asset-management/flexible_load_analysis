import copy

import numpy as np

from . import network
from . import load_points
from  . import timeseries as ts
from ..modelling import modelling
from .. import utilities


def add_new_load_to_net(str_new_load_ID, ts_new_load_data, str_parent_node_ID, dict_loads_ts, g_network):
    """Adds a node to both the network and node-container.
    """
    dict_loads_ts = load_points.add_new_load(dict_loads_ts, str_new_load_ID, ts_new_load_data)
    g_network = network.add_node(g_network, str_new_load_ID, str_parent_node_ID)
    return dict_loads_ts, g_network


def remove_node_from_net(dict_loads_ts, g_network, str_load_ID):
    """Removes a node from both the network and node-container.
    """
    dict_loads_ts = load_points.remove_load(dict_loads_ts, str_load_ID)
    g_network = network.remove_node(g_network, str_load_ID)
    return dict_loads_ts, g_network


def interactively_inspect_loads(dict_loads_ts):
    bool_continue_inspecting = True
    while bool_continue_inspecting:

        print("Available load-points to inspect")
        load_points.print_all_load_points(dict_loads_ts)

        
        print("Input ID of node you want to inspect")
        str_ID = load_points.input_until_node_in_load_points_appears(dict_loads_ts)
        load_points.graphically_represent_load_point(dict_loads_ts[str_ID])

        print("Continue inspection?")
        str_choice = utilities.input_until_acceptable_response(["y", "n"])
        bool_continue_inspecting = (str_choice == "y")
        
    return


def interactively_copy_existing_load(dict_loads_ts):
    print("Available load-points to copy from:")
    load_points.print_all_load_points(dict_loads_ts)

    print("Input ID of node you want to copy")
    str_ID = load_points.input_until_node_in_load_points_appears(dict_loads_ts)
    ts_new_load_data = copy.deepcopy(dict_loads_ts[str_ID])

    return ts_new_load_data


def interactively_model_based_on_existing_load(dict_loads_ts, dict_modelling_config):
    print("Available load-points to model based on: ")
    load_points.print_all_load_points(dict_loads_ts)

    print("Input ID of node you want to model based on")
    str_ID = load_points.input_until_node_in_load_points_appears(dict_loads_ts)
    ts_modelling_baseline = copy.deepcopy(dict_loads_ts[str_ID])

    
    ts_model = modelling.model_single_load(dict_modelling_config, ts_modelling_baseline)
    return ts_model


def interactively_add_new_loads_to_net(dict_config, dict_loads_ts, g_network):

    bool_continue_adding_loads = True
    while bool_continue_adding_loads:

        bool_successfully_generated_load = False
        while not bool_successfully_generated_load:
            print("Select how to generate the new load")
            print(30 * "-", "MENU", 30 * "-")
            print("1: Copy of existing load")
            print("2: Model based on existing load")
            print("3: Model based on max power (not yet implemented)")
            print("4: Model based on load-categorization (not yet implemented)")
            print("9: Abort")
            print(67 * "-")

            str_choice = input()

            if str_choice == '1':
                ts_new_load_data = interactively_copy_existing_load(dict_loads_ts)
            elif str_choice == '2':
                ts_new_load_data = interactively_model_based_on_existing_load(
                    dict_loads_ts, dict_config["modelling"])
            elif str_choice == '3':
                #ts_new_load_data = interactively_model_based_on_max_power(dict_loads_ts)
                print("Warning: Not yet implemented! Returning dummy-load")
                ts_new_load_data = np.array([[1, 200], [2, 300], [3, 400]])
            elif str_choice == '4':
                #ts_new_load_data = interactively_model_based_on_categorization(dict_loads_ts)
                print("Warning: Not yet implemented! Returning dummy-load")
                ts_new_load_data = np.array([[1, 200], [2, 300], [3, 400]])
            elif str_choice == '9':
                print("Aborting adding new loads to network!")
                return dict_loads_ts, g_network
            else:
                print("Input not recognized, try again!")
                continue

            # Scaling
            fl_old_max_load = np.max(ts_new_load_data[:, 1])
            print("The generated new load has max-load:", fl_old_max_load)
            print(
                "Input wanted new max-load as to scale the generated load (leave blank for no scaling)")
            fl_new_max_load = input()
            try:
                if fl_new_max_load:
                    fl_new_max_load = float(fl_new_max_load)
                    fl_scaling_factor = fl_new_max_load/fl_old_max_load
                    ts_new_load_data = ts.scale_timeseries(
                        ts_new_load_data, fl_scaling_factor)
            except TypeError:
                print("Unrecognized input, skipping scaling.")


            # Graphically represent new load
            print("New load generated: ")
            load_points.graphically_represent_load_point(ts_new_load_data)
            
            print("Is the generated load correct? ")
            str_choice = utilities.input_until_acceptable_response(["y", "n"])
            bool_successfully_generated_load = (str_choice == "y")

            if not bool_successfully_generated_load:
                print("Try generating load again or abort?")
                str_choice = utilities.input_until_acceptable_response(["g", "a"])
                if (str_choice == "g"):
                    print("Restarting load-generation")
                    bool_successfully_generated_load = False
                else:
                    print("Aborting adding of new load to network!")
                    return dict_loads_ts, g_network
                
    
        print("Successfully generated new load data!")

        print("Add the new load to the network")
        print("Set the name of the new load-point:")
        str_new_load_ID = input()

        bool_happy_with_load_placement = False
        while not bool_happy_with_load_placement:
            print("Network as of right now:")
            network.plot_network(g_network)
            print("Nodes in network:")
            list_nodes_in_network = network.list_nodes(g_network)
            print(list_nodes_in_network)

            print("Input name of parent node of", str_new_load_ID)
            str_parent_ID = network.input_until_node_in_network_appears(g_network)
            
            # Check if not trafo/not compatible node, then
            # add newload to new network
            dict_loads_ts, g_network = add_new_load_to_net(
                str_new_load_ID, ts_new_load_data, 
                str_parent_ID, dict_loads_ts, g_network)

            print("The new network will look as follows:")
            network.plot_network(g_network)

            print("Happy with the placement?")
            str_choice = utilities.input_until_acceptable_response(["y", "n"])
            if str_choice == "y":
                bool_happy_with_load_placement = True

            elif str_choice == 'n':
                dict_loads_ts, g_network = remove_node_from_net(
                    dict_loads_ts, g_network, str_new_load_ID)

                print("Retry placing load again or abort?")
                str_choice = utilities.input_until_acceptable_response(["r", "a"])
                if str_choice == "r":
                    bool_happy_with_load_placement = False
                else:
                    print("Aborting adding of new load to network!")
                    return dict_loads_ts, g_network

        print("Do you want to stop adding loads to network?")
        str_choice = utilities.input_until_acceptable_response(["y", "n"])
        bool_continue_adding_loads = (str_choice == "y")

    print("Finished adding loads to network!")
    return dict_loads_ts, g_network


def interactively_increase_loads_in_net(dict_loads_ts):
    # May add option between increasing load by addition or scaling.

    bool_continue_increasing_loads = True
    while bool_continue_increasing_loads:

        bool_correct_new_load = False
        while not bool_correct_new_load:
            
            print("Available ID's to increase: ")
            load_points.print_all_load_points(dict_loads_ts)

            print("Input ID of node you want to increase")
            str_ID = load_points.input_until_node_in_load_points_appears(dict_loads_ts)

            print(str_ID, "as of now")
            load_points.graphically_represent_load_point(dict_loads_ts[str_ID])

            print("Input how much you want to increase", str_ID, "by")
            fl_increase = utilities.input_until_expected_type_appears(float)

            ts_new_load = ts.offset_timeseries(
                dict_loads_ts[str_ID], fl_increase)

            print(str_ID, "after increase")
            load_points.graphically_represent_load_point(ts_new_load)

            print("Happy with the new load? ")
            str_choice = utilities.input_until_acceptable_response(["y", "n"])
            bool_correct_new_load = (str_choice == "y")

            if not bool_correct_new_load:
                ts_new_load = ts.offset_timeseries(
                    dict_loads_ts[str_ID], -fl_increase)
                
                print("Retry increasing load or abort?")
                str_choice = utilities.input_until_acceptable_response(["r", "a"])
                if str_choice == "r":
                    bool_correct_new_load = False
                else:
                    print("Aborting adding of new load to network!")
                    return dict_loads_ts

        print("Do you want to stop increasing loads in the network?")
        str_choice = utilities.input_until_acceptable_response(["y", "n"])
        bool_continue_increasing_loads = (str_choice == "n")

    print("Finished increasing loads!")
    return dict_loads_ts


def interactively_modify_net(dict_config, dict_loads_ts, g_network):
    """Text-menu interface for interactively modifying the network at runtime.

    Notes:
    ----------
    All network-data is per now implemented such that assignment is done by
    reference. New instances therefore must be copied explicitly.
    """
    print("Beginning interactive modification of network!")

    list_choice_log = []
    bool_continue = True

    while bool_continue:
        print("Recieved the following loads: ")
        load_points.print_all_load_points(dict_loads_ts)
        print("Recieved the following network: ")
        network.plot_network(g_network)

        print(24 * "-", "NET-MODIFICATION", 24 * "-")
        # plot data (timeseries) of chosen customer
        print("1: Examine loads")
        print("2: Add new load")
        print("3: Increase load")
        print("4: Modify topology (not yet implemented)")
        print("9: Exit modification")
        print(67 * "-")

        str_choice = input()
        list_choice_log.append(str_choice)

        if str_choice == '1':
            interactively_inspect_loads(dict_loads_ts)
        elif str_choice == '2':
            interactively_add_new_loads_to_net(
                dict_config, dict_loads_ts, g_network)
        elif str_choice == '3':
            interactively_increase_loads_in_net(dict_loads_ts)
        elif str_choice == '4':
            # modify_network_topology()  # list branches, remove, add, etc.
            print("Not yet implemented!")
        elif str_choice == '9':
            print("Exiting grid_modification!")
            bool_continue = False
        else:
            print("Input not recognized, try again!")

    return dict_loads_ts, g_network
