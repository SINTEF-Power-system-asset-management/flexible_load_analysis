import time


def UI(n_loads, g_network):

    list_choice_log = []
    bool_continue = True

    while bool_continue:
        print("Recieved the following customers: ")
        for key in n_loads:
            print(key)
        print("Recieved the following network: ")
        print(g_network)
        print(30 * "-" , "MENU" , 30 * "-")
        print("1: Examine loads")    # plot data (timeseries) of chosen customer
        print("2: Add new load")
        print("3: Modify load")
        print("4: Modify network")
        print("9: Exit modification")
        print(67 * "-")

        str_choice = input()
        list_choice_log.append(str_choice)

        if str_choice == '1':
            inspect_desired_loads_until_exit_signal()
        elif str_choice == '2':
            add_new_load_to_network()
        elif str_choice == '3':
            modify_load_in_net_work()
        elif str_choice == '4':
            modify_network()
        elif str_choice == '9':
            print("Exiting grid_modification!")
            bool_continue = False
        else:
            print("Input not recognized, try again!")
        
        time.sleep(2)
    return n_loads, g_network
    

UI([1,2],3)