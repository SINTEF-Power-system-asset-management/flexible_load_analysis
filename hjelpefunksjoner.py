import sys
import numpy as np
import math
from matplotlib import pyplot as plt
import pandas as pd
from numpy import random

### Denne fila inneholder følgende:

# Første del: hjelpefunksjoner i hoved_fil
# Andre del: hjelpefunksjoner i last_modell
# Tredje del: plot-funksjoner i last_modell

####################################
### Hjelpefunksjoner i hoved_fil ###
####################################


def generer_test_data(max_mnd, ukedag_var, helg_var, max_P, startdag=0):
    """ Generer en tilfeldig last.
    Args: 
        max_mnd: variasjonskurve sesong (normalisert)
        ukedag_var: variasjonskurve ukedag (normalisert)
        helg_var: variasjonskurve helg (normalisert)
        max_P: årlig maks-effekt 
    Returns: 
        profil: tilfeldig generert last-profil for et år 
    """
    profil = np.zeros(shape=(8760,))
    for t in range(8760):
        ind = get_index_mnd_max(t)
        tilf_avvik = np.random.uniform(0.9, 1.1)
        if sjekk_hverdag(t, startdag):
            profil[t] = max_mnd[ind] * ukedag_var[int(t % 24)] * max_P * tilf_avvik
        else:
            profil[t] = max_mnd[ind] * helg_var[int(t % 24)] * max_P * tilf_avvik

    return profil


def last_inn_data(anlegg_nr):
    """ Plot-funksjon for maks-effekter. Distribusjon av  
    Args: 
        fordeling: maks-effekter for x antall lastmodelleringer
    Returns: 
        last: effektserie for last
        startdag: hvilken dag last-serien starter på, 0 for mandag, 1 for tirsdag osv 
    """
    path = r"C:\Users\eirikh\Lastmodellering\Stokastisk_lastmodellering\Norgesnett data\H5699_data.xlsx"
    if anlegg_nr == 1:
        df = pd.read_excel(path, "Anlegg_1")
    elif anlegg_nr == 2:
        df = pd.read_excel(path, "Anlegg_2")
    elif anlegg_nr == 3:
        df = pd.read_excel(path, "Anlegg_3")
    elif anlegg_nr == 4:
        df = pd.read_excel(path, "Anlegg_4")
    elif anlegg_nr == 5:
        df = pd.read_excel(path, "Anlegg_5")
    else:
        df = None
    temp = np.array(df)
    temp_t = np.transpose(temp)
    last = temp_t[2]  # Effekt-serie last, et år
    år =  int(math.floor(len(last) / 8760))
    last = last[0 : 8760 * år]
    startdag = 0  # startdag 2018: mandag
    return last, startdag, år


def plot_maks_effekt(fordeling, simu_antall):
    """ Plot-funksjon for maks-effekter. Distribusjon av  
    Args: 
        fordeling: maks-effekter for x antall lastmodelleringer 
    """
    maks_eff = np.sort(fordeling)
    percentil = [90, 95, 99]
    frac = [percentil[0] / 100, percentil[1] / 100, percentil[2] / 100]
    P_lim = [0, 0, 0]
    for i in range(3):
        P_lim[i] = maks_eff[int(frac[i] * simu_antall)]
        print(
            "Med",
            percentil[i],
            "%",
            "sannsynlighet er maks-effekt høyst",
            P_lim[i],
            "kW.",
        )

    bins = int(len(fordeling))
    ylabel_hist = "Empirisk fordeling [antall]"
    ylabel_kum = "Kumulativ fordeling [%]"
    xlabel = "Maks-effekt [kW]"
    tittel = "Fordeling av maks-effekter"
    label_kumulativ = "Kumulativ fordeling"

    plt.figure(figsize=(15, 8))
    ax = plt.axes()
    plt.ylabel(ylabel_hist)
    values, base, _ = plt.hist(
        fordeling, bins=bins, alpha=0.5, color="green", range=None
    )
    ax_bis = ax.twinx()
    values = np.append(values, 0)
    ax_bis.plot(
        base,
        np.cumsum(values) / np.cumsum(values)[-1],
        color="darkorange",
        marker="o",
        linestyle="-",
        markersize=1,
        label=label_kumulativ,
    )
    plt.xlabel(xlabel)
    plt.ylabel(ylabel_kum)
    plt.title(tittel)
    for i in range(3):
        plt.axvline(
            x=P_lim[i],
            color="k",
            label="{} % sannsynlighet".format(percentil[i]),
            linestyle="--",
        )
    ax_bis.legend(loc="upper left")
    plt.grid(True)
    plt.show()


######################################
### Hjelpefunksjoner i last_modell ###
######################################


def temp_korriger_last(last, år=1, døgn_temp=True, plot_bool=False):
    """ Temperaturkorriger last
    Args: 
        last: effektserie for last  
        døgn_temp: True hvis det er midl. døgntemperatur. False hvis det er annen oppløsning (time f.eks) 
    Returns: 
        last_korr: temperaturkorrigert last 
    """
    normal_temperatur = normal_temperatur_døgn(
        år
    )  # gjennomsnittlig døgntemperatur basert på siste 20 år
    if døgn_temp:
        df_temp = pd.read_excel(
            "temperatur_data\\Temperatur_Strømtangen_fyr_2018-2020.xlsx"
        )
        temperatur_array = np.array(df_temp)
        temperatur = np.zeros(shape=(365 * år, 1))
        for dag in range(365 * år):
            temperatur[dag] = temperatur_array[dag][3]
    else:
        print("not in use")
        df_temp = pd.read_excel(
            "temperatur_data\\Timesverdier temperatur 2019 Færder.xlsx"
        )
        temperatur_array = np.array(df_temp)
        temperatur = np.zeros(shape=(8760, 1))
        for dag in range(365):
            for t in range(24):
                temperatur[t + 24 * dag] = temperatur_array[t + 24 * dag][3]
    if plot_bool:
        plot_temperatur(temperatur, normal_temperatur, år)
    # temperatur-avhengig faktor (avhengig av kundegruppe, husholdning, industri, skole osv.):
    k = 0.1
    # temperatursensitivitet forbruk (konstant for alle kundegrupper):
    x = 0.05

    last_korr = np.zeros(shape=(len(last),))

    if døgn_temp:
        for dag in np.arange(0, 2):
            for t in range(24):
                last_korr[t + 24 * dag] = last[t + 24 * dag]

        for dag in np.arange(2, 365 * år):
            avg_last_3_days = (
                temperatur[dag] + temperatur[dag - 1] + temperatur[dag - 2]
            ) / 3
            delta_T = normal_temperatur[dag] - avg_last_3_days
            for t in range(24):
                last_korr[t + 24 * dag] = last[t + 24 * dag] * (1 + k * x * (delta_T))

    else:
        print("not in use")
        # Eksempel på alternativ. Korrigerer basert på avstand fra timesverdi til gjennomsnittlig døgnverdi.
        for t in np.arange(0, 8760):
            delta_T = temperatur[t] - normal_temperatur[math.floor(t / 24)]
            last_korr[t] = last[t] * (1 + k * x * delta_T)

    return last_korr


def normal_temperatur_døgn(antall_år_last):
    """ Beregning av normal døgn temperatur basert på historiske data
    Args: 
        år: antall år lasten går over
    Returns: 
        normal_temperatur: normal (dvs gjennomsnittlig) temperatur for hver dag
    """
    df_temp = pd.read_excel(
        "temperatur_data\\Temperatur_Strømtangen_fyr_2000-2019.xlsx"
    )
    temperatur_array_historisk = np.array(df_temp)
    temperatur_array_historisk_transponert = np.transpose(temperatur_array_historisk)
    antall_år = math.floor(len(temperatur_array_historisk_transponert[3]) / 365)

    normal_temperatur = np.zeros(shape=(365 * antall_år_last, 1))
    for dag in range(365):
        sum_temp_dag = 0
        for år in range(antall_år):
            sum_temp_dag += temperatur_array_historisk[dag + 365 * år][3]
        normal_temperatur[dag] = sum_temp_dag / antall_år
    for år in range(1, antall_år_last):
        normal_temperatur[år * 365 : (år + 1) * 365] = normal_temperatur[0:365]

    return normal_temperatur


def find_monthly_max(P_profile, antall_år):
    """ Finn månedlig maks
    Args: 
        P_profile: effektserie for x antall år  
        antall_år: verdien av x
    Returns: 
        max_mnd: maks-effekt per måned  
    """
    max_mnd = np.zeros(shape=(12, 1))
    for år in range(antall_år):
        for t in range(8760):
            if t < 746:  # januar
                if P_profile[t + år * 8760] > max_mnd[0]:
                    max_mnd[0] = P_profile[t + år * 8760]
            elif t < 1418 and t > 745:  # febraur
                if P_profile[t + år * 8760] > max_mnd[1]:
                    max_mnd[1] = P_profile[t + år * 8760]
            elif t < 2161 and t > 1417:  # mars
                if P_profile[t + år * 8760] > max_mnd[2]:
                    max_mnd[2] = P_profile[t + år * 8760]
            elif t < 2881 and t > 2160:  # april
                if P_profile[t + år * 8760] > max_mnd[3]:
                    max_mnd[3] = P_profile[t + år * 8760]
            elif t < 3625 and t > 2880:  # mai
                if P_profile[t + år * 8760] > max_mnd[4]:
                    max_mnd[4] = P_profile[t + år * 8760]
            elif t < 4345 and t > 3624:  # juni
                if P_profile[t + år * 8760] > max_mnd[5]:
                    max_mnd[5] = P_profile[t + år * 8760]
            elif t < 5089 and t > 4344:  # juli
                if P_profile[t + år * 8760] > max_mnd[6]:
                    max_mnd[6] = P_profile[t + år * 8760]
            elif t < 5833 and t > 5088:  # august
                if P_profile[t + år * 8760] > max_mnd[7]:
                    max_mnd[7] = P_profile[t + år * 8760]
            elif t < 6553 and t > 5832:  # september
                if P_profile[t + år * 8760] > max_mnd[8]:
                    max_mnd[8] = P_profile[t + år * 8760]
            elif t < 7298 and t > 6552:  # oktober
                if P_profile[t + år * 8760] > max_mnd[9]:
                    max_mnd[9] = P_profile[t + år * 8760]
            elif t < 8018 and t > 7297:  # november
                if P_profile[t + år * 8760] > max_mnd[10]:
                    max_mnd[10] = P_profile[t + år * 8760]
            elif t < 8760 and t > 8017:  # desember
                if P_profile[t + år * 8760] > max_mnd[11]:
                    max_mnd[11] = P_profile[t + år * 8760]
    return max_mnd


def finn_var(P_profile, startdag=0, ukedag=True):
    """ Generer variasjonskruve for ukedag/helg. 
    Args: 
        P_profile: effektserie for et år  
        ukedag: defualt True, må settes til False dersom det er helg 
    Returns: 
        output: maks-effekt per ukedag/helg   
    """
    output = np.zeros(shape=(24, 1))
    for t in range(len(P_profile)):
        if ukedag:
            if sjekk_hverdag(t, startdag):
                if P_profile[t] > output[int(t % 24)]:
                    output[int(t % 24)] = P_profile[t]
        else:
            if not sjekk_hverdag(t, startdag):
                if P_profile[t] > output[int(t % 24)]:
                    output[int(t % 24)] = P_profile[t]
    return output


def sjekk_hverdag(t, startdag=0):
    """ Sjekk om det er hverdag eller hleg
    Args: 
        t: time 
        startdag: hvilken dag starter året på (mandag = 0, tirsdag = 1, osv)
    Returns: 
        hverdag: True hvis det er hverdag 
    """
    # input tid t
    # Antar her 2019, dvs at 1.jan er en tirsdag
    hverdag = False
    uke_off_set = 24 * startdag
    if t < uke_off_set:
        uke = t / (24 * 7)
    else:
        uke = (t + uke_off_set) / (24 * 7)
    treshold = math.floor(uke) + 5 / 7
    if uke < treshold:
        hverdag = True
    return hverdag


def estimer_maks_profil(max_mnd, ukedag_var, helg_var, max_P, antall_år=1, startdag=0):
    """ Estimer årlig maks-profil. 
    Args: 
        max_mnd: variasjonskurve sesong (normalisert)
        ukedag_var: variasjonskurve ukedag (normalisert)
        helg_var: variasjonskurve helg (normalisert)
        max_P: årlig maks-effekt 
        antall_år: antall år med lastdata
        startdag: hvilken dag 1.jan er
    Returns: 
        profil: maks-effekt hver time for et år 
    """
    maks_profil = np.zeros(shape=(8760 * antall_år,))
    for t in range(len(maks_profil)):
        år = int(math.floor(t / 8760))
        ind = get_index_mnd_max(t, år)
        if sjekk_hverdag(t, startdag):
            maks_profil[t] = max_mnd[ind] * ukedag_var[int(t % 24)] * max_P
        else:
            maks_profil[t] = max_mnd[ind] * helg_var[int(t % 24)] * max_P
    return maks_profil


def get_index_mnd_max(t, år=0):
    """ Returner hvilken måned det er basert på hvilken time det er.
    Args: 
        t: time 
        år: hvilket år
    Returns: 
        indeks: hvilken måned t er i
    """
    if t - 8760 * år < 746:  # januar
        return 0
    elif t - 8760 * år < 1418 and t - 8760 * år > 745:  # febraur
        return 1
    elif t - 8760 * år < 2161 and t - 8760 * år > 1417:  # mars
        return 2
    elif t - 8760 * år < 2881 and t - 8760 * år > 2160:  # april
        return 3
    elif t - 8760 * år < 3625 and t - 8760 * år > 2880:  # mai
        return 4
    elif t - 8760 * år < 4345 and t - 8760 * år > 3624:  # juni
        return 5
    elif t - 8760 * år < 5089 and t - 8760 * år > 4344:  # juli
        return 6
    elif t - 8760 * år < 5833 and t - 8760 * år > 5088:  # august
        return 7
    elif t - 8760 * år < 6553 and t - 8760 * år > 5832:  # september
        return 8
    elif t - 8760 * år < 7298 and t - 8760 * år > 6552:  # oktober
        return 9
    elif t - 8760 * år < 8018 and t - 8760 * år > 7297:  # november
        return 10
    elif t - 8760 * år > 8017:  # desember
        return 11
    else:
        print("Something went wrong...")


def sorter_avvik(alle_avvik, startdag=0):
    """ Sorterer avvik mellom helg og hverdag i histogram 
    Args: 
        alle_avvik: avvik for hvert tidssteg
        startdag (default: 0): startdag i tidsserie (mandag=0, tirsdag=1, osv)
    Returns: 
        ind: indeks fra -1 til 1 med steglengde 0.05 
        avvik_helg: hyppighetsfordeling for avvik i helg
        avvik_hverdag: hyppighetsfordeling for avvik i hverdag
    """
    avvik_helg = np.zeros(shape=(20, 1))
    avvik_hverdag = np.zeros(shape=(20, 1))
    index = 0
    ind = [
        -1.00,
        -0.90,
        -0.80,
        -0.70,
        -0.60,
        -0.50,
        -0.40,
        -0.30,
        -0.20,
        -0.10,
        -0.0,
        0.10,
        0.20,
        0.30,
        0.40,
        0.50,
        0.60,
        0.70,
        0.80,
        0.90,
    ]
    for t in range(len(alle_avvik)):
        for i in range(len(ind)):
            if alle_avvik[t] > ind[i]:
                index = i
        if sjekk_hverdag(t, startdag):
            avvik_hverdag[index] += 1
        else:
            avvik_helg[index] += 1
    return ind, avvik_helg, avvik_hverdag


#######################################
#### Plot-funksjoner i last_modell ####
#######################################


def plot_temperatur(temperatur, normal_temperatur, år):
    """ Plot av temperatur og normaltemperatur 
    Args: 
        temperatur: temperatur
        normal_temperatur: normaltemperatur 
    """
    plot_temp = np.zeros(shape=(2, 365 * år))
    plot_temp[0] = np.transpose(temperatur)
    plot_temp[1] = np.transpose(normal_temperatur)
    plt.plot(np.transpose(plot_temp))
    plt.ylabel("Temperatur [C]")
    plt.xlabel("Dag")
    plt.legend(["Temperatur 2018-2020", "Normaltemperatur (2000-2020)"])
    plt.title("Temperatur og normaltemperatur - Strømtangen")
    plt.show()


def plot_temp_last(gammel_last, last):
    """ Plot last før og etter temperaturkorrigering  
    Args: 
        gammel_last: last før temperaturkorrigering 
        last: last etter temperaturkorrigering 
    """
    plot_last = np.zeros(shape=(2, 1440))
    plot_last[0] = np.transpose(gammel_last[0:1440])
    plot_last[1] = np.transpose(last[0:1440])
    plt.plot(np.transpose(plot_last))
    plt.legend(["Før temperaturkorrigering", "Etter temperaturkorrigering"])
    plt.title("Last")
    plt.show()


def plot_mnd_var_kurve(max_mnd):
    """ Plot variasjonskurve for sesong 
    Args: 
        max_mnd: maks-effekt for hver måned 
    """
    plt.plot(max_mnd)
    plt.title("Variasjonskurve år")
    plt.show()


def plot_dag_var_kurve(ukedag_var, helg_var):
    """ Plot variasjonskurve for hverdag og helg 
    Args: 
        ukedag_var: maks-effekt for hver time på hverdager 
        helg_var: maks-effekt for hver time i helger  
    """
    plot_arr = np.zeros(shape=(2, 24))
    plot_arr[0] = np.transpose(ukedag_var)
    plot_arr[1] = np.transpose(helg_var)
    plt.plot(np.transpose(plot_arr))
    plt.title("Variasjonskurver uke")
    plt.legend(["Hverdag", "Helg"])
    plt.show()


def plot_estimert_maks(est_maks, startdag):
    """ Plot en uke med estimert maks
    Args: 
        est_maks: estimert maks-effekt 
    """
    start_tid = (7 - startdag) * 24
    plt.plot(est_maks[start_tid : start_tid + 7 * 24])
    plt.ylabel("Effekt [kW]")
    plt.title("Estimert maks - ukesprofil")
    plt.show()


def plot_pre_mod(last, est_maks, rel_avvik, antall_år = 1):
    """ Plot effektserier før modellering (pre)
    Args: 
        last: effekt-serie for last
        est_maks: effekt-serie for estimert maks basert på variasjonskurver 
        rel_avvik: relativt avvik mellom last og est_maks 
    """
    plot_arr = np.zeros(shape=(2, 8760*antall_år))  # len(last)))#8760*år))
    plot_arr[0] = last[0:8760*antall_år]
    plot_arr[1] = est_maks[0:8760*antall_år]
    #plot_arr[2] = rel_avvik[0:8760*antall_år]

    plt.plot(np.transpose(plot_arr), linewidth=0.5)
    #plt.legend(["Målt", "Maks multi. variasjonskurver", "Rel. avvik"])
    plt.title("Effektserier før modellering: Målt, estimert maks og relativt avvik")
    plt.show()


def plot_rel_avvik(rel_avvik):
    """ Plot effektserier før modellering (pre)
    Args:  
        rel_avvik: relativt avvik mellom last og est_maks 
    """
    plt.plot(np.transpose(rel_avvik), linewidth=0.5)
    plt.title("Relativt avvik")
    plt.show()


def plot_rel_avvik_hist(avvik, startdag=0):
    """ Plot relativt avvik - som histogram med skille mellom helg og hverdag
    Args: 
        startdag (default: 0): startdag i tidsserie (mandag=0, tirsdag=1, osv)
        avvik: relativt avvik mellom last og est_maks 
    """
    x, avvik_helg, avvik_hverdag = sorter_avvik(avvik, startdag)
    avvik_hverdag = np.transpose(avvik_hverdag)[0]
    avvik_helg = np.transpose(avvik_helg)[0]
    pos = np.arange(20)
    p1 = plt.bar(pos, avvik_hverdag, width=0.75)
    p2 = plt.bar(pos, avvik_helg, width=0.75, bottom=avvik_hverdag)
    plt.xticks(pos, x)
    plt.legend((p1[0], p2[0]), ("Hverdag", "Helg"))
    plt.title("Stokastisk avvik - histogram")
    plt.show()


def plot_post_mod(last, mod_last, tid=8760):
    """ Plot effektserier etter modellering (post)
    Args: 
        last: effekt-serie for last
        mod_last: effekt-serie for modellert last
        tid (default: 8760): for antall timer figuren skal vise 
    """
    plot_mod = np.zeros(shape=(2, tid))
    plot_mod[0] = last[0:tid]
    plot_mod[1] = mod_last[0:tid]

    # Plot med to akser
    plt.plot(np.transpose(plot_mod), linewidth=0.5)
    plt.ylabel("Effekt [kW]")
    plt.legend(["Målt", "Modellert"])
    plt.title("Effektserier: Målt og modellert last")
    plt.show()


def plot_mod_evaluering(eva_arr):
    """  Plot evaluering av modell 
    Args: 
        eva_arr: vektor med evalueringsverdier av stokastisk modell 
    """
    # Plot evaluering av modell
    plt.plot(eva_arr, linewidth=0.5)
    plt.title("Evaluering av stokastisk modell")
    plt.show()
