def print_dictionary_recursive(dictionary, depth = 0):
    for key in dictionary:
        print(depth*"\t", key, end=': ')
        value = dictionary[key]
        if isinstance(value, dict): 
            print()
            print_dictionary_recursive(value, depth + 1)
        else: print(value)
    return

def first_matching_index(indexable, fn_boolean):
    for i in range(len(indexable)):
        if fn_boolean(indexable[i]): return i
    return None