from datetime import datetime, timedelta

#TODO: Endre til verdier som er riktige for oss. Hentet fra Anna
#Denne fila inneholder variabler som brukes i ALNSen

#Adaptive Weights: Brukes i ALNS for å telle når man skal oppdatere vekter på operatorer
reaction_factor = 0.2

#Adaptive Weights: Gitte vektmuligheter, brukes til å velge operator
#Har en liste med alle operatorer hvor de innehar en av disse verdiene
weights = [3, 2, 1, 0.5]
#TODO: sigma_scores

#Antall iterasjoner i ALNSen
iterations = 15

#Sendes inn i ALNS og handler om hvor mye du skal destroye med operatorer altså hvor mange aktiviteter som skal ryke?
#Maxen du kan fjerne er halve løsningen
destruction_degree = 0.5

# Simulated annealing temperatures -- TODO: these must be tuned
start_temperature = 50 
end_temperature = 10
cooling_rate = 0.999

# Distance Matrix
# Buses in Oslo om average drive in 25 kms/h.
speed = 40
rush_factor = 2