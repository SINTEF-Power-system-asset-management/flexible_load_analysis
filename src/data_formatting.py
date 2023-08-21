"""Module for converting data-files to compliant format.
Modify path-parameters at the 
"""
import os.path
import pandas as pd
import numpy as np


def split_txt_by_ID_and_encode(str_path_txt, str_separator, int_column_IDs, dict_ID_encoding):
    """Splits rows of txt into multiple files based on ID-field.

    Parameters
    ----------
    str_path_txt : str
        Path of the file to split.
    str_separator : str
        String/char separating each column of the txt.
    int_column_IDs : int
        Column number of file to group rows by. Rows with the same "ID"-value
        are stored together in a new file with ID as the name. Zero-indexed.
    dict_ID_encoding : dict
        Pair of old_ID and new_ID, for anonymizing customer-data.

    Notes
    ----------
    Function creates a directory in the same folder as str_path_txt where all
    split files are put.
    """
    with open(str_path_txt, 'r') as fp:
        arr_contents = fp.readlines()

    dict_uniques = {}
    str_header = arr_contents[0]
    list_skipped = []
    for i in range(1, len(arr_contents)):
        arr_cur_line = str.split(str.strip(arr_contents[i]), str_separator)
        old_ID = arr_cur_line[int_column_IDs]
        if old_ID in dict_ID_encoding:
            new_ID = dict_ID_encoding[arr_cur_line[int_column_IDs]]
            arr_cur_line[int_column_IDs] = new_ID
            arr_lines_so_far = dict_uniques.get(new_ID, [str_header])
            arr_lines_so_far.append(str_separator.join(arr_cur_line) + '\n')
            dict_uniques[new_ID] = arr_lines_so_far
        else:
            if not (old_ID in list_skipped): list_skipped.append(old_ID)
    print("Skipped the following customers missing from encoding:")
    #for id in list_skipped: print(id)
    print(list_skipped)


    str_input_filename, _str_data_filetype = os.path.splitext(str_path_txt)
    str_folder = str_input_filename + "_split_and_encoded\\"
    if not os.path.exists(str_folder):
        os.mkdir(str_folder)
    for key in dict_uniques:
        str_new_path = str_folder + str(key) + ".txt"
        if not os.path.exists(str_new_path):
            with open(str_new_path, 'w') as fp:
                fp.writelines(dict_uniques[key])
        else:
            print(
                "WARNING! Duplicate split load-file! Delete all old files before continuing.")
    return


def encode_directory_contents(str_dir_path, dict_encoding):
    """Encodes all apperances of ID's in directory of txt-like files.

    Parameters:
    ----------
    str_dir_path : str
        Path of directory to encode.
    dict_encoding : dict
        Dictionary of old_ID, new_ID-encoding.

    Notes
    ----------
    Works with .txt, .csv-files stored in str_dir_path.

    """
    str_new_dir_path = str_dir_path[:-1] + \
        "_encoded\\"  # To remove \ from old path
    if not os.path.exists(str_new_dir_path):
        os.mkdir(str_new_dir_path)

    for str_file_path in os.listdir(str_dir_path):
        with open(str_dir_path + str_file_path, 'r') as fp:
            arr_contents = fp.readlines()
        for i in range(len(arr_contents)):
            for old_ID in dict_encoding:
                new_ID = dict_encoding[old_ID]
                arr_contents[i] = arr_contents[i].replace(old_ID + ";", new_ID + ";")

        str_new_file_path = str_new_dir_path + str_file_path
        if not os.path.exists(str_new_file_path):
            with open(str_new_file_path, 'w') as fp:
                fp.writelines(arr_contents)
        else:
            print(
                "WARNING! Duplicate network-file! Delete all old files before continuing.")

    return


def automatic_encoding(str_network_dir_path):
    # Automatic naming as "R(adial)xS(voltage)yT(number)"
    df_bus = pd.read_csv(str_network_dir_path + "bus.csv", sep=";", dtype=str)

    df_bus['zone_and_voltage'] = df_bus.apply(lambda x: f"R{x.BUS_AREA}S{x.BASE_KV}", axis=1)
    df_bus['instances'] = df_bus.groupby('zone_and_voltage').cumcount()+1
    df_bus["IDs"] = df_bus.apply(lambda x: f"{x.zone_and_voltage}T{x.instances}", axis=1)

    dict_encoding = dict(zip(df_bus.BUS_I, df_bus.IDs))

    return dict_encoding


def format_data_files(dict_data_unsplit, dict_network, str_path_encoding=None, auto_encode=True):
    if auto_encode and not (str_path_encoding is None):
        print("Warning, performing autoencoding while providing explicit encoding ignores the latter!")
    print("Loading encoding...")
    if auto_encode:
        dict_encoding = automatic_encoding(dict_network["path"])
        print("Generated the following encoding automatically:")
        print(dict_encoding)
    else:
        df_encoding = pd.read_excel(str_path_encoding, 0)
        arr_old_ID = np.array(df_encoding["old_ID"])
        arr_new_ID = np.array(df_encoding["new_ID"])
        dict_encoding = {}
        for i in range(len(arr_old_ID)):
            dict_encoding[str(arr_old_ID[i])] = str(arr_new_ID[i])
    
    print("Splitting data-file...")
    str_path = dict_data_unsplit["path"]
    str_separator = dict_data_unsplit["separator"]
    int_ID_column = dict_data_unsplit["ID_column"]
    split_txt_by_ID_and_encode(str_path, str_separator, int_ID_column, dict_encoding)

    print("Encoding network-data...")
    str_path = dict_network["path"]
    str_separator = dict_network["separator"]
    encode_directory_contents(str_path, dict_encoding)

    print("Successfully performed all data-operations")
    return


if __name__=="__main__":
    # Change these fields when running this script.
    # Delete the directories "example_network_encoded" and
    # "example_load_data_split" before running this script, or else it will do
    # nothing.
    dict_data_unsplit = {
        "path": "in_data/example_data/example_load_data.txt",
        "separator": ";",
        "ID_column": 0
    }
    dict_network = {
        "path": "in_data/example_data/example_network/",
        "separator": ";"
    }
    str_path_encoding = "in_data/example_data/example_encoding.xlsx"

    # Do not change this.
    format_data_files(
        dict_data_unsplit,
        dict_network,
        str_path_encoding=str_path_encoding,
        auto_encode=True
    )
