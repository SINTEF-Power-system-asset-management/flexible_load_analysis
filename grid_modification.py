import time


def interactively_add_new_loads_to_network(n_loads, g_network):

    bool_continue_adding_loads = True
    while bool_continue_adding_loads:
        
        bool_successfully_generated_load = False
        while not bool_successfully_generated_load:
            print("Select how to generate the new load")
            print(30 * "-" , "MENU" , 30 * "-")
            print("1: Copy of existing load")
            print("2: Model based on existing load")
            print("3: Model based on max power")
            print("4: Model based on load-categorization")

            print(67 * "-")

            str_choice = input()

            if str_choice == '1':
                #n_new_load = interactively_copy_existing_load(n_loads)
                n_new_load = 1
            elif str_choice == '2':
                #n_new_load = interactively_model_based_on_existing_load(n_loads)
                n_new_load = 2
            elif str_choice == '3':
                #n_new_load = interactively_model_based_on_max_power(n_loads)
                n_new_load = 3
            elif str_choice == '4':
                #n_new_load = interactively_model_based_on_categorization(n_loads)
                n_new_load = 4
            else:
                print("Input not recognized, try again!")
                continue
        
            # graphically represent n_new_load
            print(n_new_load)
            bool_retry_input = True
            while bool_retry_input:
                print("Is the generated load correct? yes/no")
                str_choice = str.lower(input())
                if str_choice == "yes" or str_choice == 'y':
                    bool_successfully_generated_load = True
                    bool_retry_input = False
                elif str_choice == "no" or str_choice == 'n':
                    bool_successfully_generated_load = False
                    bool_retry_input = False
                else:
                    print("Unrecognizd input, try again")
                    bool_retry_input = True

            if not bool_successfully_generated_load:
                bool_retry_input = True
                while bool_retry_input:
                    print("Try generating load again or abort? g/a")
                    str_choice = str.lower(input())
                    if str_choice == 'g':
                        bool_successfully_generated_load = False
                        bool_retry_input = False
                    elif str_choice == 'a':
                        print("Aborting adding of new load to network!")
                        bool_retry_input = False
                        return n_loads, g_network
                    else:
                        print("Unrecognizd input, try again")
                        bool_retry_input = True

            print("Restarting load-generation")

        print("Successfully generated new load!")

        print("Add the new load to the network")
        # function interactively_add_load_to_network
        # print network
        # print("Select parent node of new load")
        # Check if not trafo, then 
        # g_new_network = g_network
        # add newload to newnetwork
        # Graph newnetwork
        # Are you happy?
        # if yes: g_network = g_new_network
        # if not: try again or abort?

        time.sleep(2)
        
        print("Do you want to stop adding loads to netork (No)/Yes?")
        str_choice = str.lower(input())
        if str_choice == "yes" or 'y':
            bool_continue_adding_loads = False

    print("Finished adding loads to network!")
    return n_loads, g_network



interactively_add_new_loads_to_network([1,2,3], 7)