import numpy as np

def create_load_duration_curve(ts):
    """Returns indexed set of loads, sorted by highest = 0.
    """
    load_sorted = np.sort(ts[:,1])
    load_sorted = np.flipud(load_sorted)
    idxs = np.arange(0, load_sorted.shape[0])
    return np.vstack((idxs, load_sorted)).T
