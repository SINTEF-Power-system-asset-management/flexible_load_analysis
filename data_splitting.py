import os.path


def split_txt_by_ID(str_path_txt, str_separator, int_column_IDs):
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

    Notes
    ----------
    Function creates a directory in the same folder as str_path_txt where all
    split files are put.
    """
    with open(str_path_txt, 'r') as fp:
        arr_contents = fp.readlines()

    dict_uniques = {}
    str_header = arr_contents[0]
    for i in range(1, len(arr_contents)):
        arr_cur_line = str.split(str.strip(arr_contents[i]), str_separator)
        ID = arr_cur_line[int_column_IDs]
        arr_lines_so_far = dict_uniques.get(ID, [str_header])
        arr_lines_so_far.append(str_separator.join(arr_cur_line) + '\n')
        dict_uniques[ID] = arr_lines_so_far

    str_input_filename, _str_data_filetype = os.path.splitext(str_path_txt)
    str_folder = str_input_filename + "_split\\"
    if not os.path.exists(str_folder):
        os.mkdir(str_folder)
    for key in dict_uniques:
        str_new_path = str_folder + str(key) + ".txt"
        if not os.path.exists(str_new_path):
            with open(str_new_path, 'w') as fp:
                fp.writelines(dict_uniques[key])
        else:
            raise Exception("At least one duplicate file! Delete all old files before continuing.")
