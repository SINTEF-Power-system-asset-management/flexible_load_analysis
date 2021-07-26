import os
import datetime as dt
import pandas as pd
import numpy as np
import toml


def load_config(str_config_path):
    """Loads config.toml.

    Returns
    ----------
    dict_config : dict
        Dictionary containing loaded configuration-file.

    Notes
    ----------
    Requires toml as dependency.
    """
    dict_config = toml.load(str_config_path)
    return dict_config


def load_time_and_data_from_excel(
        str_path_excel,
        int_sheet,
        int_time_column,
        int_data_column,
        vertical_data=True):
    """Loads time and data-fields from excel-sheet

    Parameters
    ----------
    str_path_excel : str
        Relative path of excel-file to be loaded.
    int_sheet : int
        Sheet-number of excel-file. Zero-indexed.
    int_time_column, int_data_column : int
        Column (row) the relevant information occupies. Zero-indexed.
    vertical_data, bool, default=True
        Whether the time/data-values occupy rows downwards ("vertical") or not.

    Returns
    ----------
    arr_time : np.array
        Array of time-values.
    arr_data : np.array
        Array of data-values.

    Raises
    ----------
    FileNotFoundError
        If pandas can't find str_path_excel.

    Notes
    ----------
    Requires pandas as dependency.

    Assumes the first row (column) is used for labeling and therefore does not
    load this row (column).

    The returned arrays are coordinated in the sense that the ith element of
    each array correspond to the same row in the loaded excel-sheet.
    """
    try:
        df_excel_sheet = pd.read_excel(str_path_excel, int_sheet)
    except FileNotFoundError:
        print("File not found, check path in config.toml")
        raise FileNotFoundError
    arr_excel_sheet = np.array(df_excel_sheet)
    if not vertical_data:
        arr_excel_sheet = np.transpose(arr_excel_sheet)
    arr_time = arr_excel_sheet[:, int_time_column]
    arr_data = arr_excel_sheet[:, int_data_column]
    return arr_time, arr_data


def load_time_and_data_from_txt(
        str_path_txt,
        str_separator,
        int_time_column,
        int_data_column,
        vertical_data=True):
    """Loads time and data-fields from structured txt-file

    Parameters
    ----------
    str_path_txt : str
        Relative path of txt-file to be loaded.
    str_separator : str
        Character or string separating each column.
    int_time_column, int_data_column : int
        Column (row) the relevant information occupies. Zero-indexed.
    vertical_data, bool, default=True
        Whether the time/data-values occupy rows downwards ("vertical") or not.

    Returns
    ----------
    arr_time : np.array
        Array of time-values.
    arr_data : np.array
        Array of data-values.

    Notes
    ----------
    A structured txt-file will resemble a spreadsheet where str_separator
    delimits columns and newline delimits rows.

    Assumes the first row (column) is used for labeling and therefore does not
    load this row (column).

    The returned arrays are coordinated in the sense that the ith element of
    each array correspond to the same row in the loaded txt-file.
    """
    with open(str_path_txt, 'r') as fp:
        arr_contents = fp.readlines()
    for i in range(len(arr_contents)):
        arr_contents[i] = str.split(str.strip(arr_contents[i]), str_separator)
    arr_contents = np.array(arr_contents)
    if not vertical_data:
        arr_contents = np.transpose(arr_contents)
    arr_contents = arr_contents[1:,:]
    arr_time = arr_contents[:, int_time_column]
    arr_data = arr_contents[:, int_data_column]
    return arr_time, arr_data


def convert_general_time_array_to_datetime_array(
        arr_time_general,
        list_time_format,
        str_first_date_iso=""):
    """Converts array of any time-format to python datetime.

    Parameters
    ----------
    arr_time_general : np.arrary
        Array of timestamps on any format.
    list_time_format : list(string)
        List of possible formats the timestamps are on.
    str_first_date_iso, str, default=""
        Date of first timestamp, iso format.

    Returns
    ----------
    arr_time_dt : np.array(datetime)
        Array of timestamps on datetime-format.
    """
    arr_time_dt = [None] * len(arr_time_general)
    for i in range(len(arr_time_general)):
        if 'H' in list_time_format:
            arr_time_dt[i] = (dt.datetime.fromisoformat(str_first_date_iso)
                              + dt.timedelta(hours=int(arr_time_general[i])))
        else:
            if isinstance(list_time_format, list):
                for str_format in list_time_format:
                    try:
                        arr_time_dt[i] = dt.datetime.strptime(
                            str(arr_time_general[i]), str_format)
                        bool_success = True
                        break
                    except:
                        bool_success = False
                        continue
                if not bool_success:
                    raise Exception(
                        "Unable to apply any of the given date-formats")
            else:
                try:
                    arr_time_dt[i] = dt.datetime.strptime(
                        str(arr_time_general[i]), list_time_format)
                except:
                    pass
    return arr_time_dt


def convert_general_data_array_to_float_array(arr_data):
    """Converts array of selected data-formats to floats.

    Parameters
    ----------
    arr_data : np.arrary
        Array of ints, floats or strings representing numerical values.

    Returns
    ----------
    arr_data_float : np.array(float)

    Notes
    ----------
    Also compensates for use of ',' instead of '.' as decimal separator.

    """
    arr_data_float = [None] * len(arr_data)
    for i in range(len(arr_data)):
        data_i = arr_data[i]
        if isinstance(data_i, float):
            arr_data_float[i] = data_i
        elif isinstance(data_i, str):
            if ',' in data_i:
                arr_data_float[i] = float(str.replace(data_i, ',', '.'))
            else:
                arr_data_float[i] = float(data_i)
        else:
            arr_data_float[i] = data_i
    return arr_data_float


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


def load_data_and_create_timeseries(dict_data_config):
    """Loads data based on structured dictionary and creates timeseries.

    Parameters
    ----------
    dict_data_config : dict
        Structured dictionary containing at least the path of the data, 
        how the timestamps are formatted and the date of the first timestamp.

    Returns
    ----------
    ts_data : timeseries = np.array([datetime, float])
        Timeseries of loaded data.

    Notes
    ----------
    Main functionality of this module.
    """
    str_data_path = dict_data_config["path"]
    str_data_date_format = dict_data_config["date_format"]
    str_data_first_date_iso = dict_data_config["first_date_iso"]

    list_paths_to_be_loaded = []
    if os.path.isdir(str_data_path):
        for str_file_path in os.listdir(str_data_path):
            list_paths_to_be_loaded.append(str_data_path + str_file_path)
    else:
        list_paths_to_be_loaded.append(str_data_path)

    dict_loaded_ts = {}
    for str_path in list_paths_to_be_loaded:
        print("Loading", str_path + "...")
        _str_data_filename, str_data_filetype = os.path.splitext(str_path)

        if str_data_filetype == ".xlsx" or str_data_filetype == ".xls":
            int_sheet = dict_data_config["sheet"]
            int_time_column = dict_data_config["time_column"]
            int_data_column = dict_data_config["data_column"]
            bool_vertical_data = dict_data_config["vertical_data"]

            arr_time, arr_data = load_time_and_data_from_excel(
                str_path, int_sheet,
                int_time_column, int_data_column, bool_vertical_data)

        elif str_data_filetype == ".txt":
            str_separator = dict_data_config["separator"]
            int_time_column = dict_data_config["time_column"]
            int_data_column = dict_data_config["data_column"]
            bool_vertical_data = dict_data_config["vertical_data"]

            arr_time, arr_data = load_time_and_data_from_txt(
                str_path, str_separator,
                int_time_column, int_data_column, bool_vertical_data)

        elif str_data_filetype == ".csv":
            raise Exception("Not yet implemented")

        # elif str_data_filetype == ".example"
        #   Code for additional formats

        arr_time_dt = convert_general_time_array_to_datetime_array(
            arr_time, str_data_date_format, str_data_first_date_iso)
        arr_data = convert_general_data_array_to_float_array(arr_data)

        ts_data = create_standard_time_series(arr_time_dt, arr_data)

        if os.path.isdir(str_data_path):
            str_key_name, _temp = os.path.splitext(
                str_path.replace(str_data_path, ""))
        else:
            str_key_name = str_data_path
        dict_loaded_ts[str_key_name] = ts_data

    return dict_loaded_ts


def load_network_from_directory(dict_network_config):
    """Loads directory of MATPOWER-formatted csb-files to dictionary.

    Parameters
    ----------
    dict_network_config : dict
        Dictionary of file-configuration, including path.

    Returns
    ----------
    dict_network : dict
        Dictionary of network-information required to build graph-representation.
    """
    str_dir_path = dict_network_config["path"]
    str_separator = dict_network_config["separator"]

    list_paths_to_be_loaded = []
    for str_file_path in os.listdir(str_dir_path):
        list_paths_to_be_loaded.append(str_dir_path + str_file_path)

    dict_network = {}
    for str_path in list_paths_to_be_loaded:
        print("Loading", str_path + "...")

        df_network_info = pd.read_csv(str_path, sep=str_separator)
        dict_network_info = {}
        for col in df_network_info:
            dict_network_info[col] = np.array(df_network_info[col])

        str_data_filename, _str_data_filetype = os.path.splitext(str_path)
        str_key_name = str_data_filename.replace(str_dir_path, "")
        dict_network[str_key_name] = dict_network_info

    return dict_network
