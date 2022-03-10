import numpy as np

# Dictionary utility

def print_dictionary_recursive(dictionary, depth=0):
    """Prints a dictionary of nested dictionaries on a nice format.

    Parameters
    ----------
    dictionary : dict
        Dictionary to be printed
    depth : int, default=0
        Recursion depth.
    """
    for key in dictionary:
        print(depth*"\t", key, end=': ')
        value = dictionary[key]
        if isinstance(value, dict):
            print()
            print_dictionary_recursive(value, depth + 1)
        else:
            if isinstance(value, np.ndarray):
                print("Numpy-array of length", len(value))
            else:
                print(value)
    return


def first_matching_index(indexable, fn_boolean):
    """Finds index of first element which fulfills boolean function

    Parameters
    ----------
    indexable : indexable container
        Container to be searched.
    fn_boolean : func
        Truthy function for element to fulfil.

    Returns
    -----------
    i : int
        Index of indexable of first item fulfilling search criteria.
    None
        If no element fulfils criteria.
    """
    for i in range(len(indexable)):
        if fn_boolean(indexable[i]):
            return i
    return None


def get_first_value_of_dictionary(dict_inp):
    """Returns first value of dictionary.
    """
    if len(dict_inp) == 1:
        for key in dict_inp:
            return dict_inp[key]
    else:
        return None


# Interactive dictionary handling

def interactively_traverse_nested_dictionary(dict_choices):
    """Traverse nested string-keyed dictionary

    Parameters:
    ----------
    dict_choices : dict
        Dictionary to traverse

    Returns:
    ----------
    str_final_key : str
        Final input key
    data : 
        Content at final input key

    Notes:
    ----------
    Dictionary is traversed like a file-system, where each nested dictionary may
    be interpreted as a sub-folder.
    """
    print("\nAvailable files: ")
    print()
    print_dictionary_recursive(dict_choices)

    bool_successful_input = False
    while not bool_successful_input:
        print("\nInput key of data-source to follow")
        str_key = str(input())
        if str_key not in dict_choices:
            print("Could not find key, try again")
        else:
            bool_successful_input = True
    if type(dict_choices[str_key]) == dict:
        str_final_key, data = interactively_traverse_nested_dictionary(
            dict_choices[str_key])
    else:
        str_final_key = str_key
        data = dict_choices[str_key]
    return str_final_key, data


def interactively_insert_into_dictionary(dict_content, new_content, str_content_description="content"):
    """Input content to dictionary interactively

    Parameters:
    ----------
    dict_content : dict
        Dictionary to insert content into
    new_content : 
        Content to insert
    str_content_description : str (optional)
        Description of content, to be used in display

    Returns:
    ----------
    dict_content : dict
        Dictionary after insertion

    Notes:
    ----------
    Leaving input blank aborts storing of new content.
    """
    print("The following keys are already stored:")
    for key in dict_content:
        print(key)

    bool_successfully_input = False
    while not bool_successfully_input:
        print("Input name to store", str_content_description,
              "under (leave blank to abort)")
        str_name = str(input())
        if not str_name:
            print("Aborting storage!")
            return dict_content
        elif str_name in dict_content:
            print("Name is already in use, try again")
        else:
            dict_content[str_name] = new_content
            bool_successfully_input = True
            print("Successfully stored", str_content_description)
    return dict_content


def interactively_write_to_file_in_directory(str_results_directory_path, result):
    print("Beginning to store results locally at machine...")
    print("WARNING: Not yet implemented!")
    return


# UI

def input_until_expected_type_appears(type):
    print("Please input a", type)
    while True:
        inp = input()
        try:
            type_variable = type(inp)
            return type_variable
        except ValueError:
            print("Input failed, try again")


def input_until_acceptable_response(list_acceptable_responses):
    """Acceptable responses must be of same type
    """
    acceptable_type = type(list_acceptable_responses[0])
    bool_acceptable_response = False
    while not bool_acceptable_response:
        print("Acceptable responses:", list_acceptable_responses)
        str_response = input_until_expected_type_appears(acceptable_type)
        if str_response in list_acceptable_responses:
            bool_acceptable_response = True
        else:
            print("Response not accepted, please retry!")

    return str_response


# Datetime

def duration_to_hours(dt_dur):
    return dt_dur.seconds / 3600 + dt_dur.days * 24

def datetime_to_season(dt):
    # 1 = winter
    # 2 = spring
    # 3 = summer
    # 4 = autumn

    month = dt.month
    season = month%12 // 3 + 1 
    return season