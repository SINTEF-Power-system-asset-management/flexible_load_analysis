import matplotlib.pyplot as plt
import numpy as np
import analysis.methods.load_aggregation as load_aggregation
import plotting
from flexibility.flexibility_need import OverloadEvent

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

def find_overloads(ts_data, fl_power_limit):
    l_overloads = []
    b_in_overload_event = False
    for i in range(len(ts_data)):
        b_line_overloaded = (ts_data[i, 1] >= fl_power_limit)
        if b_line_overloaded and not b_in_overload_event:
            b_in_overload_event = True
            i_start = i
        elif not b_line_overloaded and b_in_overload_event:
            i_end = i
            l_overloads.append(OverloadEvent(ts_data[i_start:i_end+1,:], fl_power_limit))
            b_in_overload_event = False
        else:
            continue
    return l_overloads

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