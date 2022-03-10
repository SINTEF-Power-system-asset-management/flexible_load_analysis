import init
import load_points
from flexibility import flexibility_need
from analyses import load_aggregation
import net_modification
import timeseries as ts
import plotting
import copy
import numpy as np


def add_random_loads_flex_analysis(loads, network, agg_index, num_iterations, 
                                    plot_aggregate=True, plot_overload=True):
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
                if plot_overload: flexibility_need.plot_flexibility_characteristics(flex_need)


if __name__ == "__main__":

    np.random.seed(0)

    STR_CONFIG_PATH = "ora_data/config_ORA.toml"
    dict_config, dict_data, dict_network = init.initialize_config_and_data(
        STR_CONFIG_PATH)

    # Data-structure
    dict_loads_ts = load_points.prepare_all_loads(dict_config, dict_data)

    #add_random_loads_flex_analysis(dict_loads_ts, dict_network, 1, 100)
