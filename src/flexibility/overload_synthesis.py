import copy
import numpy as np
import pandas as pd
import plotting
import analysis.methods.load_aggregation as load_aggregation
import flexibility.flexibility_need as flexibility_need
import flexibility.flexibility_analysis as flexibility_analysis
import objects.net_modification as net_modification
import objects.timeseries as ts

def add_N_random_loads(loads, network, agg_index, num_iterations, 
                                    plot_aggregate=True, plot_histogram=True, plot_clustering=True):
    str_agg_id = network["branch"]["F_BUS"][agg_index]
    fl_limit_kW = float(network["branch"]["RATE_A"][agg_index])*1000

    all_load_ids = [load_id for load_id in loads]
    l_loads_added = []

    for i in range(num_iterations + 1):
        if i != 0:
            print("Adding new load to network...")
            id_to_copy_from = np.random.choice(all_load_ids)
            ts_new_load_data = copy.deepcopy(loads[id_to_copy_from])
            net_modification.add_new_load_to_net(
                "5000" + str(i), ts_new_load_data, str_agg_id, loads, network)
            l_loads_added.append(id_to_copy_from)

        if i % 10 == 0:
            print(f"Loads added so far: {l_loads_added}")
            ts_agg = load_aggregation.aggregate_load_of_node(
                str_agg_id, loads, network)
            if plot_aggregate: plotting.plot_timeseries([ts_agg], [
                                     "Aggregated"], f"Aggregated load and limit after {i} addition(s)", fl_limit=fl_limit_kW)

            l_overloads = flexibility_analysis.find_overloads(ts_agg, fl_limit_kW)
            #l_overloads = flexibility_need.remove_unimportant_overloads(l_overloads)
            if l_overloads:
                flex_need = flexibility_need.FlexibilityNeed(l_overloads)
                if plot_histogram: plotting.plot_flexibility_histograms(flex_need)
                if plot_clustering: plotting.plot_flexibility_clustering(flex_need)

def remove_zeros(ts):
    df = pd.DataFrame(ts)
    df = df[(df != 0).all(1)]
    ts = df.to_numpy()
    return ts

def increase_single_load(loads, network, customer_index, aggregation_index, fl_increase, do_plotting=True):
    # Load to aggregate at
    str_agg_id = network["branch"]["F_BUS"][aggregation_index]
    # Customer to increase
    #str_customer_id = network["bus"]["BUS_I"][customer_index]
    # Line-limit at aggregation point
    fl_limit_kW = float(network["branch"]["RATE_A"][aggregation_index])*1000

    ts_agg_after = load_aggregation.aggregate_load_of_node(
                str_agg_id, loads, network)
    
    # Increasing load of ts_agg_before induce overloads
    ts_agg_after = ts.normalize_timeseries(ts_agg_after, (1.42*np.max(ts_agg_after[:,1])))
    ts_agg_after = remove_zeros(ts_agg_after)

    if do_plotting:
        plotting.plot_timeseries([ts_agg_after[0:26304,:]],
                                ["Aggregated load"],
                                f"Aggregated load and limit after increasing load",
                                fl_limit=fl_limit_kW)

    list_overloads = flexibility_analysis.find_overloads(ts_agg_after[0:26304,:], fl_limit_kW)
    if list_overloads:
        flex_need = flexibility_need.FlexibilityNeed(list_overloads)
        if do_plotting:
            plotting.plots_for_SEST(flex_need)
    else:
        flex_need = None
    return flex_need

