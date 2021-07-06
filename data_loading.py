import datetime as dt
import pandas as pd
import numpy as np
import os.path



def load_time_and_data_from_excel(str_path_excel, int_sheet, int_time_column, int_data_column, vertical_data=True):
    try:
        df_excel_sheet = pd.read_excel(str_path_excel, int_sheet)
    except FileNotFoundError:
        print("File not found, check path in config.toml")
    arr_excel_sheet = np.array(df_excel_sheet)
    if not vertical_data:
        arr_excel_sheet = np.transpose(arr_excel_sheet)
    return arr_excel_sheet[:,int_time_column], arr_excel_sheet[:,int_data_column]

def load_time_and_data_from_txt(str_path_txt, str_separator, int_time_column, int_data_column, vertical_data=True):
    with open(str_path_txt, 'r') as fp:
        arr_contents = fp.readlines()
    for i in range(len(arr_contents)):
        arr_contents[i] = str.split(str.strip(arr_contents[i]), str_separator)
    arr_contents = np.array(arr_contents)
    if not vertical_data:
        arr_contents = np.transpose(arr_contents)
    arr_contents = arr_contents[1:19753,:]   # Assumes the first row isn't data, hard-coded last datapoint for testing purposes
    arr_time = arr_contents[:,int_time_column]
    arr_data = arr_contents[:,int_data_column]
    return arr_time, arr_data


# str_first_date_iso not necessary when time format contains dates
def convert_general_time_array_to_datetime_array(arr_time_general, list_time_format, str_first_date_iso=""):
    arr_time_dt = [None] * len(arr_time_general)
    for i in range(len(arr_time_general)):
        if isinstance(arr_time_general[i], (int, np.float64)):    # This seems gross, maybe own configuration for non-string timestamps?
            if 'H' in list_time_format:
                arr_time_dt[i] = dt.datetime.fromisoformat(str_first_date_iso) + dt.timedelta(hours=arr_time_general[i])
        else:
            if isinstance(list_time_format, list):
                for str_format in list_time_format:
                    try:
                        arr_time_dt[i] = dt.datetime.strptime(str(arr_time_general[i]), str_format)
                        bool_success = True
                        break
                    except:
                        bool_success = False
                        continue
                if not bool_success: raise Exception("Unable to apply any of the given date-formats")
            else:
                try:
                    arr_time_dt[i] = dt.datetime.strptime(str(arr_time_general[i]), list_time_format)
                except:
                    pass

    # Or perhaps do some pipeline-y thing with arr_time_dt[i] += ... for bit of info given

        """ Always perform this action? Can you imagine time format not on HH:MM:SS and doesn't contain d?
        if not 'd' in str_time_format:  # when the timestamps are relative some given start-date
            if str_first_date_iso == "" : raise Exception("Missing first date info")
            arr_time_dt[i] = arr_time_dt[i] #+ dt.timedelta()#take the date from str_first_date_iso and time from arr_time_dt[i] to form new datetime-obj
        """

    return arr_time_dt

def convert_data_to_float(arr_data):
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
    return np.transpose(np.array([arr_time_dt, arr_data]))



def load_data_and_create_timeseries(dict_data_config):
    str_data_path = dict_data_config["path"]
    str_data_date_format = dict_data_config["date_format"]
    str_data_first_date_iso = dict_data_config["first_date_iso"]

    _str_data_filename, str_data_filetype = os.path.splitext(str_data_path)

    if str_data_filetype == ".xlsx" or str_data_filetype == ".xls":
        int_sheet = dict_data_config["sheet"]
        int_time_column = dict_data_config["time_column"]
        int_data_column = dict_data_config["data_column"]
        bool_vertical_data = dict_data_config["vertical_data"]

        arr_time, arr_data = load_time_and_data_from_excel(str_data_path, int_sheet, int_time_column, int_data_column, bool_vertical_data)
    
    elif str_data_filetype == ".txt":
        str_separator = dict_data_config["separator"]
        int_time_column = dict_data_config["time_column"]
        int_data_column = dict_data_config["data_column"]
        bool_vertical_data = dict_data_config["vertical_data"]
        
        arr_time, arr_data = load_time_and_data_from_txt(str_data_path, str_separator, int_time_column, int_data_column, bool_vertical_data)

    elif str_data_filetype == ".csv":
        raise Exception("Not yet implemented")
    
    # elif str_data_filetype == ".example"
    #   Code for additional formats

    arr_time_dt = convert_general_time_array_to_datetime_array(arr_time, str_data_date_format, str_data_first_date_iso)
    arr_data = convert_data_to_float(arr_data)

    ts_data = create_standard_time_series(arr_time_dt, arr_data)

    return ts_data