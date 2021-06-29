from models import toenne

def model_load(dict_config, dict_data_ts):
    print("Loading the chosen model and parameters...")

    str_chosen_model = dict_config["modelling"]["chosen_model"]
    dict_parameters = dict_config["modelling"][str_chosen_model]
    if str_chosen_model == "toenne":
        dict_model = toenne.create_toenne_load_model(dict_data_ts, dict_parameters)
    elif str_chosen_model == "example":
        raise Exception("Not yet implemented")

    print("Successfully performed load-modelling")
    return dict_model