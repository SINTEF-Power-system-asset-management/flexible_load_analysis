import numpy as np
from numpy import random
from matplotlib import pyplot as plt
import pandas as pd

from hjelpefunksjoner import *
from last_modell import *
from test_data import last_max_mnd, last_ukedag_var, last_helg_var

plt.rcParams.update({"font.size": 28})  # skriftstørrelse på plot

plot_bool = 1  # plotte last og avvik underveis?
x_simu = 0     # dersom man ønsker å modellere lasten en gang, sett x_simu til 0.
# dersom man ønsker x antall modelleringer av samme last, sett x_simu til 1 og angi antall simuleringer (simu_antall)

############################
#### Last inn last-data ####
############################

# Generere tilfeldig last (test):
test = 0

if test:
    # Last inn testdata
    last = generer_test_data(last_max_mnd, last_ukedag_var, last_helg_var, 50, 0)
    last_startdag = 0
    antall_år = 1
else:
    # Last inn kunde
    anlegg_nr = 5
    last, last_startdag, antall_år = last_inn_data(anlegg_nr)

print("Målt maks-effekt er", max(last), "kW.")

# Input til last-modellen under må være en np-array som inneholder en effektserie over et år for en gitt last / kunde
# Koden over må endres / tilpasses det man har av tilgjengelig data / dataformat slik at man får en last med et slik format

#########################
#### Lastmodellering ####
#########################

if x_simu:  # Kjør x antall simuleringer (x bestemmes av "simu_antall" i linja under)

    simu_antall = 1000
    maks_eff = np.zeros(shape=(simu_antall,))
    eva_verdi = np.zeros(shape=(simu_antall,))
    for sim in range(simu_antall):
        maks_eff[sim], eva_verdi[sim] = modeller_last(
            last, startdag=last_startdag, år=antall_år, plot=plot_bool,
        )

    plot_maks_effekt(maks_eff, simu_antall)
    print(
        "Gjennomsnittlig verdi for evaluering av stokastisk modell:",
        sum(eva_verdi) / simu_antall,
    )
    print("Maks modellert verdi:", max(maks_eff))

else:  # kjør en simulering

    maks_eff, eva_verdi = modeller_last(
        last, startdag=last_startdag, år=antall_år, plot=plot_bool
    )
    print("Modellert maks-effekt er", maks_eff, "kW.")
    print("Stokastisk evaluering gir:", eva_verdi)
