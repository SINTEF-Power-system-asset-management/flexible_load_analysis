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
