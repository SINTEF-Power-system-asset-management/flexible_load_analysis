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
import utilities as util


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
                if plot_histogram: plotting.plot_flexibility_histograms(flex_need)
                if plot_clustering: plotting.plot_flexibility_clustering(flex_need)



def increase_single_load_flex_analysis(loads, network, customer_index, aggregation_index, fl_increase, do_plotting=True):
    # Load to aggregate at
    str_agg_id = network["branch"]["F_BUS"][aggregation_index]
    # Customer to increase
    str_customer_id = network["bus"]["BUS_I"][customer_index]
    # Line-limit at aggregation point
    fl_limit_kW = float(network["branch"]["RATE_A"][aggregation_index])*1000

    ts_agg_before = load_aggregation.aggregate_load_of_node(
                str_agg_id, loads, network)

    # Increasing load of customer to induce overloads
    ts_customer = loads[str_customer_id]
    ts_customer = ts.normalize_timeseries(ts_customer, (fl_increase + np.max(ts_customer[:,1])/2))
    ts_customer = ts.offset_timeseries(ts_customer, fl_increase/2)
    loads[str_customer_id] = ts_customer

    ts_agg_after = load_aggregation.aggregate_load_of_node(
                str_agg_id, loads, network)
    if do_plotting:
        plotting.plot_timeseries([ts_agg_before],
                                ["Aggregated"],
                                f"Aggregated load and limit before increasing load",
                                fl_limit=fl_limit_kW)
        plotting.plot_timeseries([ts_agg_after],
                                ["Aggregated"],
                                f"Aggregated load and limit after increasing load",
                                fl_limit=fl_limit_kW)

    list_overloads = flexibility_need.find_overloads(ts_agg_after, fl_limit_kW)
    if list_overloads:
        flex_need = flexibility_need.FlexibilityNeed(list_overloads)
        if do_plotting:
            plotting.plot_flexibility_histograms(flex_need)
            plotting.plot_flexibility_clustering(flex_need)
    return flex_need
    

def overload_temperature_correlation(ts_temperature_historical, flex_need):
    temps = {}
    for temp_measurement in ts_temperature_historical:
        temps[temp_measurement[0].date()] = temp_measurement[1]
    
    temps = np.array([temps[o.dt_start.date()] for o in flex_need.l_overloads])

    plotting.plot_timeseries([ts_temperature_historical], [""], [""], str_ylabel="Temperature [C]")

    arr_spikes = np.array([o.fl_spike for o in flex_need.l_overloads])

    plt.scatter(temps, arr_spikes)
    plt.xlabel("Temperature [deg C]")
    plt.ylabel("Spike [kW]")
    plt.show()

    print(np.corrcoef(temps, arr_spikes))



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


""" Fungerer ikke
def plot_stacked_area_of_children(node, loads, g_network):
    children = network.customers_below(node, loads, g_network)
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
    
    add_random_loads_flex_analysis(dict_loads_ts, dict_network, 1, 50, plot_aggregate=True, plot_histogram=True)
    # Pr. now, choice to increase load nr. 18 is chosen arbritarily
    flex_need = increase_single_load_flex_analysis(dict_loads_ts, dict_network, 18, 1, 1200)

    # Temperature-correlation
    ts_temperature_historical = util.get_first_value_of_dictionary(dict_data["temperature_measurements"])
    overload_temperature_correlation(ts_temperature_historical, flex_need)
