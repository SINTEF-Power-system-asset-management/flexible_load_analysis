import analyses
import init
import load_points
from flexibility import flexibility_need
from analyses import load_aggregation
import net_modification
import timeseries as ts
import plotting
import copy
import numpy as np
import network
import matplotlib.pyplot as plt


def add_random_loads_flex_analysis(loads, network, agg_index, num_iterations, 
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

            l_overloads = flexibility_need.find_overloads(ts_agg, fl_limit_kW)
            #l_overloads = flexibility_need.remove_unimportant_overloads(l_overloads)
            if l_overloads:
                flex_need = flexibility_need.FlexibilityNeed(l_overloads)
                if plot_histogram: flexibility_need.plot_flexibility_histograms(flex_need)
                if plot_clustering: flexibility_need.plot_flexibility_clustering(flex_need)


def increase_single_load_flex_analysis(loads, network, customer_index, aggregation_index, fl_increase):
    str_agg_id = network["branch"]["F_BUS"][aggregation_index]
    fl_limit_kW = float(network["branch"]["RATE_A"][aggregation_index])*1000

    ts_agg = load_aggregation.aggregate_load_of_node(
                str_agg_id, loads, network)
    plotting.plot_timeseries([ts_agg], [
                                     "Aggregated"], f"Aggregated load and limit before increasing load", fl_limit=fl_limit_kW)

    str_customer_id = network["bus"]["BUS_I"][customer_index]
    ts_customer = loads[str_customer_id]
    ts_customer = ts.offset_timeseries(ts_customer, fl_increase)
    loads[str_customer_id] = ts_customer

    ts_agg = load_aggregation.aggregate_load_of_node(
                str_agg_id, loads, network)

    plotting.plot_timeseries([ts_agg], [
                                     "Aggregated"], f"Aggregated load and limit after increasing load", fl_limit=fl_limit_kW)

    l_overloads = flexibility_need.find_overloads(ts_agg, fl_limit_kW)
    if l_overloads:
        flex_need = flexibility_need.FlexibilityNeed(l_overloads)
        flexibility_need.plot_flexibility_histograms(flex_need)
        flexibility_need.plot_flexibility_clustering(flex_need)




def find_branch_closest_to_overload(loads, network):
    maxs = []
    for i in range(len(network["branch"]["F_BUS"])):
        print(i)
        fbus = network["branch"]["F_BUS"][i]
        rate_A = float(network["branch"]["RATE_A"][i])*1000
        
        ts_agg = load_aggregation.aggregate_load_of_node(
                fbus, loads, network)
        if ts_agg != np.array([]): 
            fl_max = float(np.max(ts_agg[:,1]))
            maxs.append((i, rate_A - fl_max, fbus, rate_A))
    return sorted(maxs,key=lambda x: x[1], reverse=False)[0]

def customers_below(node, loads, g_network):
    if node in loads:
        return [node]
    else:
        res = []
        children = network.list_children_of_node(node, g_network)
        for id in children:
            res += customers_below(id, loads, g_network)
        return res


""" Fungerer ikke
def plot_stacked_area_of_children(node, loads, g_network):
    children = customers_below(node, loads, g_network)
    children_loads = []
    for id in children:
        if id in loads:
            children_loads.append(loads[id][:,1])
    
    plt.stackplot(*children_loads)

    plt.show()
"""


if __name__ == "__main__":

    np.random.seed(0)

    STR_CONFIG_PATH = "ora_data/config_ORA.toml"
    dict_config, dict_data, dict_network = init.initialize_config_and_data(
        STR_CONFIG_PATH)

    # Data-structure
    dict_loads_ts = load_points.prepare_all_loads(dict_config, dict_data)
    
    # add_random_loads_flex_analysis(dict_loads_ts, dict_network, 1, 50, plot_aggregate=True, plot_histogram=True)
    increase_single_load_flex_analysis(dict_loads_ts, dict_network, 18, 1, 1500)
    


    
