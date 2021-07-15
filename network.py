import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

"""Module takes in dictionary of matpower-formattet dictionaries of info
on the network. The project uses networkx as it's graph representation.
This module also presents functions for operating on the network, so that the 
network-representation may be changed without changing outside operating on the network.
"""

# module-name is perfect and represents an accurate level of abstraction,
# therefore the nodes need to be renamed to 

# repeat of fnc from data_loading. consider moving 
# "load_data_and_create_timeseries" to init for better cohesion in data_loading
# and thereby allowing data_loading to be imported into this module.

def convert_network_dictionary_to_graph(dict_network):
    nx_network = nx.Graph()
    nx_network.add_nodes_from(dict_network["bus"]["bus_i"])
    nx_network.add_edges_from(
            np.stack((
                dict_network["branch"]["fbus"], 
                dict_network["branch"]["tbus"]), 
                axis=1))
    plt.subplot(111)
    nx.draw(nx_network, with_labels=True, font_weight='bold')
    plt.show()
    return nx_network