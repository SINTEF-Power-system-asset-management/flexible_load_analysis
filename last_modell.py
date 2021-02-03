import numpy as np 
from numpy import random
from matplotlib import pyplot as plt 
import pandas as pd 

from hjelpefunksjoner import * 

### Denne fila inneholder følgende: 

# En funksjon (modeller_last) som utfører lastmodelleringen basert på Tønne sin algoritme. 

def modeller_last(last, startdag, plot = True, print_div = True): 
    """ Funksjon for modellering av last 
    Steg 1: Temperaturkorriger last 
    Steg 2: Fremkall variasjonskurver 
    Steg 3: Beregn profil for estimert maks-effekt
    Steg 4: Beregn relativt avvik 
    Steg 5: Modeller last ut fra estimert maks og relativt avvik
    Steg 6: Evauler stokatisk modell 
    Args: 
        last [numpy array, 8760 verdier]: målt/faktisk forbruk, effektserie med timesoppløsning 
        plot (default: True): sannhetsvariabel for plot
        print_div (default: True): sannhetsvariabel for printing 
    Return: 
        mod_last: modellert last
    """

    ############
    ## Steg 1 ##
    ############

    ### Temperaturkorriger last 

    gammel_last = last 
    Tønne_temp = 1
    if Tønne_temp: # Tønne metodikk - døgntemp, 3 siste mot normal for temp-korrigering
        last = temp_korriger_last(last, plot_bool = plot) 
    else: 
        last = temp_korriger_last(last, døgn_temp=False, plot_bool = plot) 


    ############
    ## Steg 2 ##
    ############  

    ### Generer variasjonskurver for måned, hverdag, helg
     
    # Fremkall variasjonskurver 
    max_mnd = find_monthly_max(last)
    ukedag_var = finn_var(last, startdag)
    helg_var = finn_var(last, startdag, ukedag = False)

    # Normaliser variasjonskurvene 
    max_P = max(last)
    max_mnd = max_mnd/max_P
    ukedag_var = ukedag_var/max_P
    helg_var = helg_var/max_P

    if plot: 
        # plot last før og etter temperatur-korrigering 
        plot_temp_last(gammel_last, last)

        # plot variasjonskurver 
        plot_mnd_var_kurve(max_mnd)
        plot_dag_var_kurve(ukedag_var, helg_var)

    ############
    ## Steg 3 ##
    ############

    ### Beregn estimert maks  

    est_maks = estimer_maks_profil(max_mnd, ukedag_var, helg_var, max_P, startdag)

    ############
    ## Steg 4 ##
    ############

    ### Beregn relativt avvik ("avvik") 

    last = np.array(last)
    est_maks = np.array(est_maks)
    avvik = (last - est_maks)/est_maks # relativt avvik

    if plot: 
        # Plot målt (temp-korrigert), estimert maks og relativt avvik
        plot_pre_mod(last, est_maks, avvik)

        # plot relativt avvik 
        plot_rel_avvik(avvik, startdag)

    # (valgfri) Finn sannsynlighetsfordeling for relative avvik 

    ############
    ## Steg 5 ##
    ############

    ### Modeller last

    mod_last = np.zeros(shape=(8760,))
    for t in range(8760): 
        mod_last[t] = est_maks[t]*(1 + np.random.choice(avvik))

    ############
    ## Steg 6 ##
    ############

    ### Evaluer modell 

    # Avvik mellom modellert last og faktisk last 
    tot_avvik = mod_last - last 

    eva_arr = np.zeros(shape=(8760,))
    neg_avvik = 0
    for t in range(8760): 
        if tot_avvik[t] < 0 :
            neg_avvik += 1 
        eva_arr[t] = (mod_last[t] - last[t])/est_maks[t]

    if plot: 
        # plot modellert last for en gitt tid 
        plot_post_mod(last, mod_last, tid = 1000)

        # plot evaluering av modell 
        plot_mod_evaluering(eva_arr)

    # Print diverse parametre 
    if print_div:
        print("Makseffekt for estimert maks: ", max(est_maks), " kW.")
        print("Makseffekt for målt last: ", max(last), " kW.")
        print("Makseffekt for modellert last: ", max(mod_last), " kW.")
        print("Evaluering av stokastisk modell: ", sum(np.positive(eva_arr)), " %.")
        print("Grad av avviket som er negativt: ", neg_avvik/87.6, " %.")
        print("Liten grad av negativt avvik tilsier at modelleringen typisk gir en for høy verdi.")
    
    return max(mod_last)

