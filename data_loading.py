import datetime as dt
import pandas as pd
import numpy as np



def load_time_and_data_from_excel(str_path_excel, str_sheet, int_time_column, int_data_column): # columns 0 and 1
    # Try read_excel, throw if bad str.
    df_excel_sheet = pd.read_excel(str_path_excel, str_sheet)
    arr_excel_sheet = np.array(df_excel_sheet)
    return arr_excel_sheet[:,int_time_column], arr_excel_sheet[:,int_data_column]



def convert_hour_array_to_datetime_array(arr_time_hours):
    arr_time_dt = np.zeros_like(arr_time_hours)
    for i in range(len(arr_time_hours)):
        arr_time_dt[i] = dt.datetime.fromtimestamp(arr_time_hours[i] * 3600)
    return arr_time_dt

arr_time_hrs, arr_data = load_time_and_data_from_excel('sample_load_data.xlsx', 0, 0, 1)
print(type(arr_time_hrs[0]))