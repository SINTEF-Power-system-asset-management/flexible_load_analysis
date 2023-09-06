import copy

import numpy as np

from .. import plotting
from ..analysis.methods import load_aggregation
from ..objects import net_modification, timeseries as ts, network
from . import flexibility_need, flexibility_analysis


def add_N_random_loads(loads, dict_network, agg_index, num_iterations, 
                                    plot_aggregate=True, plot_histogram=True, plot_clustering=True):
    str_agg_id = dict_network["branch"]["F_BUS"][agg_index]
    fl_limit_kW = float(dict_network["branch"]["RATE_A"][agg_index])*1000
    reference_bus_ID = network.get_reference_bus_ID(dict_network)

    all_load_ids = [load_id for load_id in loads]
    l_loads_added = []

    for i in range(num_iterations + 1):
        if i != 0:
            print("Adding new load to dict_network...")
            id_to_copy_from = np.random.choice(all_load_ids)
            ts_new_load_data = copy.deepcopy(loads[id_to_copy_from])
            net_modification.add_new_load_to_net(
                "5000" + str(i), ts_new_load_data, str_agg_id, loads, dict_network)
            l_loads_added.append(id_to_copy_from)

        if i % 10 == 0:
            print(f"Loads added so far: {l_loads_added}")
            ts_agg = load_aggregation.aggregate_load_of_node(
                str_agg_id, loads, dict_network, reference_bus_ID)
            if plot_aggregate: plotting.plot_timeseries([ts_agg], [
                                     "Aggregated"], f"Aggregated load and limit after {i} addition(s)", fl_limit=fl_limit_kW)

            l_overloads = flexibility_analysis.find_overloads(ts_agg, fl_limit_kW)
            #l_overloads = flexibility_need.remove_unimportant_overloads(l_overloads)
            if l_overloads:
                flex_need = flexibility_need.FlexibilityNeed(l_overloads)
                if plot_histogram: plotting.plot_flexibility_histograms(flex_need)
                if plot_clustering: plotting.plot_flexibility_clustering(flex_need)



def increase_single_load(loads, dict_network, customer_index, aggregation_index, fl_increase, do_plotting=True):
    # Load to aggregate at
    str_agg_id = dict_network["branch"]["F_BUS"][aggregation_index]
    # Customer to increase
    str_customer_id = dict_network["bus"]["BUS_I"][customer_index]
    # Line-limit at aggregation point
    fl_limit_kW = float(dict_network["branch"]["RATE_A"][aggregation_index])*1000
    reference_bus_ID = network.get_reference_bus_ID(dict_network)

    ts_agg_before = load_aggregation.aggregate_load_of_node(
                str_agg_id, loads, dict_network, reference_bus_ID)

    # Increasing load of customer to induce overloads
    ts_customer = loads[str_customer_id]
    ts_customer = ts.normalize_timeseries(ts_customer, (fl_increase + np.max(ts_customer[:,1])/2))
    ts_customer = ts.offset_timeseries(ts_customer, fl_increase/2)
    loads[str_customer_id] = ts_customer

    ts_agg_after = load_aggregation.aggregate_load_of_node(
                str_agg_id, loads, dict_network, reference_bus_ID)
    if do_plotting:
        plotting.plot_timeseries([ts_agg_before],
                                ["Aggregated"],
                                f"Aggregated load and limit before increasing load",
                                fl_limit=fl_limit_kW)
        plotting.plot_timeseries([ts_agg_after],
                                ["Aggregated"],
                                f"Aggregated load and limit after increasing load",
                                fl_limit=fl_limit_kW)

    list_overloads = flexibility_analysis.find_overloads(ts_agg_after, fl_limit_kW)
    if list_overloads:
        flex_need = flexibility_need.FlexibilityNeed(list_overloads)
        if do_plotting:
            plotting.plot_flexibility_histograms(flex_need)
            plotting.plot_flexibility_clustering(flex_need)
    else:
        flex_need = None
    return flex_need

