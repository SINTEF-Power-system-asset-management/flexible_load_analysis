import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import analysis

str_bus_ID = "c"

dict_loads_ts = {
    "a" : np.array([[1, 12.3], [2, 13.3], [3, 14.3]]),
    "b" : np.array([[1, 40.3], [2, 30.3], [3, 20.3]])
}

g_network = nx.DiGraph()
g_network.add_nodes_from(["a", "b", "c"])
g_network.add_edge("c", "b")
g_network.add_edge("c", "a")


plt.subplot(111)
nx.draw(g_network, with_labels=True, font_weight='bold')
plt.show()

print(analysis.aggregation_factors(str_bus_ID, dict_loads_ts, g_network))