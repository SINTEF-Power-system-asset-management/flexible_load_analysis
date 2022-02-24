import init
import load_points
from flexibility import flexibility_need
from analyses import load_aggregation
import net_modification

STR_CONFIG_PATH = "ora_data/config_ORA.toml"
dict_config, dict_data, dict_network = init.initialize_config_and_data(
    STR_CONFIG_PATH)

# Data-structure
dict_loads_ts = load_points.prepare_all_loads(dict_config, dict_data)


i_agg_ind = 1
str_agg_id = dict_network["branch"]["F_BUS"][i_agg_ind]
for i in range(10):
    fl_lim = float(dict_network["branch"]["RATE_A"][i_agg_ind])
    ts_agg = load_aggregation.aggregate_load_of_node(str_agg_id, dict_loads_ts, dict_network)
    l_overloads = flexibility_need.find_overloads(ts_agg, fl_lim)
    #print("----------Before filtering----------")
    #[print(i) for i in l_overloads]
    l_overloads = flexibility_need.remove_unimportant_overloads(l_overloads)
    #print("----------After filtering----------")
    #[print(i) for i in l_overloads]
    #input()
    flexibility_need.overload_distribution(l_overloads)

    # TODO: Generate new load here and insert, run analysis again.
    net_modification.add_new_load_to_net("5000" + str(i), [[],[]], str_agg_id, dict_loads_ts, dict_network)