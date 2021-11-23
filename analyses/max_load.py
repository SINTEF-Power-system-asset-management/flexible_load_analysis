import numpy as np

def find_max_load(ts_load):
    return np.max(ts_load[:, 1])