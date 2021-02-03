## Readme
Dette er en "readme"-fil for en implementert lastmodelleringsalgoritme utført av SINTEF Energi AS i forbindelse med CINELDI WP1. 

## Python versjoner
Koden er bygget opp ved hjelp av Python 3.85. Koden skal fungere med andre versjoner av Python 3.  

Nødvendig pakker som må være installert for kjøring av kode: 
a) numpy
b) math 
c) pandas 
d) matplotlib (pyplot) 

## Bruk
Koden er fri for bruk. Opphavsrett tilhører SINTEF Energi AS.

## Kodestruktur

I "hoved_fil" er det variabelen "x_simu" (0/1) som angir om det skal gjøres en (sett x_simu til 0) eller mange simuleringer (sett x_simu til 1).   

Koden er strukturert utfra Erling Tønne sin lastmodelleringsmetodikk. 
1) Temperaturkorriger last
2) Beregn variasjonskurver 
3) Beregn relativt avvik fra estimert maks-effekt og faktisk forbruk 
4) Fordelingsfunksjon for stokastisk variabel - relativt avvik 
5) Modellering av last med stokastisk variabel 

"last_modell" gjør lastmodelleringen og tar inn hjelpefunksjoner fra "hjelpefunksjoner". Man kjører funksjonen for lastmodellen i "hoved_fil", enten en gang eller flere - spesifiserer i "hoved_fil". 

"test_data" er en forhåndsdefinert variasjonskurve man kan anvende for å genere en tilfeldig last, i så tilfelle må "test"-variablen i "hoved_fil" settes til 1. 