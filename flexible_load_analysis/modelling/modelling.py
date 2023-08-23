from .models import toenne


def model_load(dict_modelling_config, dict_data_ts):
    """Shell function for selecting model.

    Parameters
    ----------
    dict_modelling_config : dict
        Dictionary of chosen model and parameters.

    Returns
    ----------
    dict_model : dict
        Dictionary of finished model as well as biproducts from modelling.
    """
    print("Loading the chosen model and parameters...")

    str_chosen_model = dict_modelling_config["chosen_model"]
    dict_parameters = dict_modelling_config[str_chosen_model]
    if str_chosen_model == "toenne":
        dict_model = toenne.create_toenne_load_model(
            dict_data_ts, dict_parameters)
    elif str_chosen_model == "example":
        raise Exception("Not yet implemented")

    print("Successfully performed load-modelling")
    return dict_model
