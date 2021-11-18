import numpy as np

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


