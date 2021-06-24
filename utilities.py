def print_dictionary_recursive(dictionary, depth = 0):
    for key in dictionary:
        print(depth*"\t", key, end=': ')
        value = dictionary[key]
        if type(value) == dict: 
            print()
            print_dictionary_recursive(value, depth + 1)
        else: print(value)
    return