import numpy as np
import scipy.optimize as opt

from ...objects import radial_network_traversal
from . import load_aggregation


def velander_model(x, k1, k2):
    return k1 * x + k2 * np.sqrt(x)


def find_velander_coefficients(
    d_loads,
    d_network,
    agg_node,
    min_subset_size=10,
    max_subset_size=20,
    num_samples=20,
    return_uncertainty=False,
):
    """This function uses successive subset sampling and curve fitting to estimate Velander coefficents for the supplied grid.

    Args:
        d_loads (dict): Dictionary containing all load timeseries
        d_network (dict): Matpower-formatted dictionary of network.
        agg_node (str): Which node in the network the aggregation should
        min_subset_size (int, optional): Smallest randomly generated sample size. Defaults to 10.
        max_subset_size (int, optional): Largest randomly generated sample size. Defaults to 20.
        num_samples (int, optional): Number of samples generated. Defaults to 20.

    Returns:
        (float,float): calculated Velander coefficients k1 and k2

    Notes:
        For each iteration, a random number of load points are sampled, aggregated, and their peak load- and energy demand are
        calculated and collected as a single datapoint. The process is repeated until enough datapoints are generated.
    """
    contributing_nodes = radial_network_traversal.all_loads_below(
        agg_node, d_network, d_loads, reference_node=agg_node
    )

    max_subset_size = min(max_subset_size, len(contributing_nodes)) - 1

    peak_load_observations = np.empty(num_samples)
    energy_demand_observations = np.empty(num_samples)

    for i in range(num_samples):
        size = np.random.randint(min_subset_size, max_subset_size)
        sample_nodes = np.random.choice(contributing_nodes, size)

        arr_load = load_aggregation.aggregate_load_of_node(
            agg_node,
            {key: d_loads[key] for key in sample_nodes},
            d_network,
            print_contributing=False,
            reference_node=agg_node
        )
        peak_load_observations[i] = np.max(arr_load[:, 1])
        energy_demand_observations[i] = np.sum(arr_load[:, 1])
    popt, pcov = opt.curve_fit(velander_model, energy_demand_observations, peak_load_observations)

    # Since Pmax <= E <= N*Pmax, then Velander assumes
    # k1 E + k2 E^(1/2) <= E <= N*(k1 E + k2 E^(1/2))
    # implies
    # k1 E <= E <= N*(k1 E + k2 E)
    # k1 <= 1 <= N(k1 + k2)
    # assert popt[0] <= 1
    # assert 1 <= arr_load.shape[0]*(sum(popt))

    if return_uncertainty:
        return popt, np.sqrt(np.diag(pcov))

    return popt
