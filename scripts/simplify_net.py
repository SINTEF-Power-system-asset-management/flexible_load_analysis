import matplotlib.pyplot as plt

from flexible_load_analysis.data_initialization import data_loading, preprocessing
from flexible_load_analysis.objects import net_simplification
from flexible_load_analysis.objects.network import plot_network



configs = [
    r"in_data/test_data/single_radial/config.toml",
    r"in_data/test_data/two_radials/config.toml"
]
voltage_levels = [66, 66]

reference_buses = [None, "B1"]

save_modified_to_file = False
out_dir = r".\simplified_data"


for STR_CONFIG_PATH, voltage_level_kV, reference_bus in zip(configs, voltage_levels, reference_buses):

    dict_config, dict_data, dict_network = data_loading.initialize_config_and_data(
        STR_CONFIG_PATH)

    dict_loads_ts, dict_preprocessing_log = preprocessing.preprocess_all_loads(dict_config, dict_data)

    fig, all_axes = plt.subplots(2,1)
    axs = all_axes.flat
    
    plot_network(dict_network, draw_figure=False, ax=axs[0])
    axs[0].set_title("Before simplification")

    dict_loads_ts, dict_network = net_simplification.simplify_net(dict_loads_ts, dict_network, unifying_voltage_kV=voltage_level_kV, reference_bus=reference_bus, keep_highest_impedance_loadline=True)
    
    plot_network(dict_network, draw_figure=False, ax=axs[1])
    axs[1].set_title("After simplification")
    plt.show()
