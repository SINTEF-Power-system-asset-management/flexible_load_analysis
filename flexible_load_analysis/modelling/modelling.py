from .models import toenne
from ..utilities import get_first_value_of_dictionary

def model_all_loads(dict_modelling_config, dict_loads_ts):
    str_chosen_model = dict_modelling_config["chosen_model"]
    dict_parameters = dict_modelling_config[str_chosen_model]

    match str_chosen_model:
        case "toenne":
            modelling_func = toenne.create_toenne_load_model
        case "example1":
            modelling_func = print

    dict_modelled_ts = {}
    dict_modelling_log = {}
    for str_node_ID in dict_loads_ts:
        print(f"Modelling node {str_node_ID} ...")
        load_measurement_ts = dict_loads_ts[str_node_ID]
        dict_modelling_log[str_node_ID] = {}
        modelled_ts = modelling_func(load_measurement_ts, dict_modelling_log[str_node_ID], **dict_parameters)
        dict_modelled_ts[str_node_ID] = modelled_ts
    
    print("Successfully performed all load-modelling")
    return dict_modelled_ts, dict_modelling_log


def model_single_load(dict_modelling_config, load_ts):
    
    dict_modelled_ts, _ = model_all_loads(dict_modelling_config, {"Data" : load_ts})

    return get_first_value_of_dictionary(dict_modelled_ts)
