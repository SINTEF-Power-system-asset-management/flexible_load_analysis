import json

def load_config():
    fp_config = open('config.json', 'r')
    dict_config = json.load(fp_config)
    return dict_config 

def init():
    dict_config = load_config()
    print("Loaded the following config.json: \n", dict_config)
    print("Do you want to override any parameters (No)/Yes?")
    str_input = str.lower(input())
    if str_input == 'y' or str_input == 'yes':
        raise(Exception("Not configured yet"))

    
    return


init()