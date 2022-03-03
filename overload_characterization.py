import init
import load_points
from flexibility import flexibility_need
from analyses import load_aggregation
import net_modification
import timeseries as ts
import plotting
import copy
import numpy as np

np.random.seed(0)

STR_CONFIG_PATH = "ora_data/config_ORA.toml"
dict_config, dict_data, dict_network = init.initialize_config_and_data(
    STR_CONFIG_PATH)

# Data-structure
dict_loads_ts = load_points.prepare_all_loads(dict_config, dict_data)


i_agg_ind = 1
str_agg_id = dict_network["branch"]["F_BUS"][i_agg_ind]
all_load_ids = [load_id for load_id in dict_loads_ts]
l_loads_added = []

for i in range(101):
    if i != 0:
        print("Adding new load to network...")
        id_to_copy_from = np.random.choice(all_load_ids) #"40016"
        ts_new_load_data = copy.deepcopy(dict_loads_ts[id_to_copy_from])
        """ Removed to instead add 10s of loads and aggregate statistics
        fl_old_max_load = np.max(ts_new_load_data[:, 1])
        fl_new_max_load = 1000
        fl_scaling_factor = fl_new_max_load/fl_old_max_load
        ts_new_load_data = ts.scale_timeseries(ts_new_load_data, fl_scaling_factor)
        """
        net_modification.add_new_load_to_net("5000" + str(i), ts_new_load_data, str_agg_id, dict_loads_ts, dict_network)
        l_loads_added.append(id_to_copy_from)

    if i % 10 == 0:
        fl_lim_kW = float(dict_network["branch"]["RATE_A"][i_agg_ind])*1000
        ts_agg = load_aggregation.aggregate_load_of_node(str_agg_id, dict_loads_ts, dict_network)
        l_overloads = flexibility_need.find_overloads(ts_agg, fl_lim_kW)
        #l_overloads = flexibility_need.remove_unimportant_overloads(l_overloads)
        if l_overloads: flex_need = flexibility_need.FlexibilityNeed(l_overloads)
        
        print(l_loads_added)
        plotting.plot_timeseries([ts_agg], ["Aggregated"], f"Aggregated load and limit after {i} addition(s)",fl_limit=fl_lim_kW)
        if l_overloads: flexibility_need.plot_flexibility_characteristics(flex_need)
