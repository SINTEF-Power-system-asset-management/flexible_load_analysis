import numpy as np
from numpy import random
from matplotlib import pyplot as plt
import pandas as pd

from hjelpefunksjoner import *
from last_modell import *
from test_data import last_max_mnd, last_ukedag_var, last_helg_var

plt.rcParams.update({"font.size": 28})  # skriftstørrelse på plot

plot_bool = 1  # plotte last og avvik underveis?
antall_simuleringer = 1  # dersom man ønsker å modellere lasten en gang

# Variasjonskurve-alternativ: A eller B
alt = "A"
# Avviksinndeling: "felles" eller "individuell"
avvik_fordeling = "felles"

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

maks_eff = np.zeros(shape=(antall_simuleringer,))
eva_verdi = np.zeros(shape=(antall_simuleringer,))

for simulering in range(antall_simuleringer):
    maks_eff[simulering], eva_verdi[simulering] = modeller_last(
        last,
        startdag=last_startdag,
        år=antall_år,
        alt=alt,
        fordeling_avvik=avvik_fordeling,
        plot=plot_bool,
    )

if antall_simuleringer > 1:
    plot_maks_effekt(maks_eff, antall_simuleringer)
    print(
        "Gjennomsnittlig verdi for evaluering av stokastisk modell:",
        sum(eva_verdi) / antall_simuleringer,
    )
    print("Maks modellert verdi:", max(maks_eff))
else:
    print("Modellert maks-effekt er", maks_eff[0], "kW.")
    print("Stokastisk evaluering gir:", eva_verdi[0])
