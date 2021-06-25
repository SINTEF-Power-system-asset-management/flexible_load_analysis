import datetime as dt
import pandas as pd
import numpy as np
import os.path



def load_time_and_data_from_excel(str_path_excel, str_sheet, int_time_column, int_data_column, vertical_data=True):
    df_excel_sheet = pd.read_excel(str_path_excel, str_sheet)
    arr_excel_sheet = np.array(df_excel_sheet)
    if not vertical_data:
        arr_excel_sheet = np.transpose(arr_excel_sheet)
    return arr_excel_sheet[:,int_time_column], arr_excel_sheet[:,int_data_column]

"""
def load_time_and_data_from_csv(str_path_csv, parameters):

    return arr_time, arr_data
"""

# str_first_date_iso not necessary when time format contains dates
def convert_general_time_array_to_datetime_array(arr_time_general, str_time_format, str_first_date_iso=""):
    arr_time_dt = [None] * len(arr_time_general)
    for i in range(len(arr_time_general)):
        if type(arr_time_general[i]) != str:    # This seems gross, maybe own configuration for non-string timestamps?
            if 'H' in str_time_format:
                arr_time_dt[i] = dt.datetime.fromisoformat(str_first_date_iso) + dt.timedelta(hours=arr_time_general[i])
        else:
            arr_time_dt[i] = dt.datetime.strptime(str(arr_time_general[i]), str_time_format)

    # Or perhaps do some pipeline-y thing with arr_time_dt[i] += ... for bit of info given

        """ Always perform this action? Can you imagine time format not on HH:MM:SS and doesn't contain d?
        if not 'd' in str_time_format:  # when the timestamps are relative some given start-date
            if str_first_date_iso == "" : raise Exception("Missing first date info")
            arr_time_dt[i] = arr_time_dt[i] #+ dt.timedelta()#take the date from str_first_date_iso and time from arr_time_dt[i] to form new datetime-obj
        """

    return arr_time_dt



def create_standard_time_series(arr_time_dt, arr_data):
    return np.transpose(np.array([arr_time_dt, arr_data]))



def load_data_and_create_timeseries(dict_data_config):
    str_data_path = dict_data_config["path"]
    str_data_date_format = dict_data_config["date_format"]
    str_data_first_date_iso = dict_data_config["first_date_iso"]

    _str_data_filename, str_data_filetype = os.path.splitext(str_data_path)

    if str_data_filetype == ".xlsx" or str_data_filetype == ".xls":
        str_sheet = dict_data_config["sheet"]
        str_time_column = dict_data_config["time_column"]
        str_data_column = dict_data_config["data_column"]
        bool_vertical_data = dict_data_config["vertical_data"]

        arr_time, arr_data = load_time_and_data_from_excel(str_data_path, str_sheet, str_time_column, str_data_column, bool_vertical_data)
    
    elif str_data_filetype == ".csv":
        raise Exception("Not yet implemented")
    # elif str_data_filetype == ".example"
    #   Code for additional formats

    arr_time_dt = convert_general_time_array_to_datetime_array(arr_time, str_data_date_format, str_data_first_date_iso)

    ts_data = create_standard_time_series(arr_time_dt, arr_data)

    return ts_data