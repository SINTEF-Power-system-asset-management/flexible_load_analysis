"""Module for implementing storage and interaction of the nodes of the network.

Notes
----------
Load-points are defined as an ID, timeseries-pair of a specific load-point.

The point of isolating operations relating to load-points is such that the
chosen way of storing the load-points may be changed at will, without needing to
change code outside this module.

The unit of the load is implicitly kW (KiloWatt), but changing this will not affect calculations.

"""

import numpy as np

from . import timeseries as ts
from .. import utilities
from .. import plotting



def add_new_load(dict_loads_ts, str_new_load_ID, ts_new_load_data):
    dict_loads_ts[str_new_load_ID] = ts_new_load_data
    return dict_loads_ts


def remove_load(dict_loads_ts, str_load_ID):
    dict_loads_ts.pop(str_load_ID)
    return dict_loads_ts


def all_timestamps_present(dict_loads_ts):
    all_timestamps = np.empty((0,))
    for timeseries in dict_loads_ts.values():
        all_timestamps = np.unique(np.append(all_timestamps, ts.get_timestamp_array(timeseries)))
    return all_timestamps


def print_all_load_points(dict_loads_ts):
    for key in dict_loads_ts:
        print(key)
    return


def graphically_represent_load_point(lp_load):
    """Nicely show off data in single load-point.
    """

    plotting.plot_timeseries(
        [lp_load], ["ID: "], "Time", "Load", "Timeseries of customer: ")
    return

def input_until_node_in_load_points_appears(dict_loads_ts):
    bool_ID_in_network = False
    while not bool_ID_in_network:
        print("Please select a node")
        str_ID = utilities.input_until_expected_type_appears(str)
        if str_ID in dict_loads_ts:
            bool_ID_in_network = True
        else:
            print("Could not find", str_ID, "in list of load points!")
    return str_ID
