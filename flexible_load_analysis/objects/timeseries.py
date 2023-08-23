import numpy as np

from .. import utilities

def create_standard_time_series(arr_time_dt, arr_data):
    """Returns timeseries on standardized format

    Parameters
    ----------
    arr_time_dt : np.array
        Array of timestamps.
    arr_data : np.arrary
        Array of data associated to the timestamps.

    Returns
    ----------
    timeseries = np.array([datetime, float])
        Timeseries-array.

    Notes
    ----------
    "Standardized" here means that the timeseries is formatted vertically, 
    such that array[i] accesses the ith datapoint.
    """
    return np.transpose(np.array([arr_time_dt, arr_data]))


def add_timeseries(ts_a, ts_b):
    """Returns the sum of data-values in two timeseries

    Parameters:
    ----------
    ts_a, ts_b : timeseries

    Returns:
    ----------
    ts_sum : timeseries
        Sum of input timeseries.

    Notes:
    ----------
    This function will cause skewing if both datasets contain similar amount of
    missing datapoints.

    The function will amend non-equally sized timeseries by searching for
    matching timestamps.

    """
    if not ts_a.size > 0:
        return ts_b
    if not ts_b.size > 0:
        return ts_a

    if len(ts_a) != len(ts_b):
        print("Warning: Mismatching length when adding timeseries!")

        if len(ts_a[:, 0]) < len(ts_b[:, 0]):
            ts_shortest, ts_longest = ts_a, ts_b
        else:
            ts_shortest, ts_longest = ts_b, ts_a
        int_first_index = utilities.first_matching_index(
            ts_longest[:, 0],
            lambda dt: dt == ts_shortest[0, 0])
        ts_first_part_of_sum = ts_longest[:int_first_index, :]
        ts_second_part_of_sum = add_timeseries(
            ts_shortest,
            ts_longest[int_first_index:, :])
        ts_sum = np.concatenate((ts_first_part_of_sum,
                                ts_second_part_of_sum),
                                axis=0)

    else:
        arr_time = ts_a[:, 0]
        arr_data = ts_a[:, 1] + ts_b[:, 1]
        ts_sum = np.transpose(np.array([arr_time, arr_data]))
    return ts_sum


def offset_timeseries(ts, fl):
    """Offsets all datapoints in a timeseries by some number.
    """
    ts[:, 1] += fl
    return ts


def scale_timeseries(ts, fl):
    """Scales all datapoints in a timeseries by some number.
    """
    ts[:,1] *= fl
    return ts


def normalize_timeseries(ts, new_max=1):
    old_max = np.max(ts[:,1])
    scale = new_max/old_max
    ts = scale_timeseries(ts, scale)
    return ts