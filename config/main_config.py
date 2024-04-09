from datetime import datetime, timedelta

#TODO: Endre til verdier som er riktige for oss. Hentet fra Anna
#Denne fila inneholder variabler som brukes i ALNSen

#Adaptive Weights: Brukes i ALNS for å telle når man skal oppdatere vekter på operatorer
reaction_factor = 0.2

#Antall iterasjoner i ALNSen
iterations = 5

#Krav til hvor bra løsning er før vi kjører lokalsøk. Må tunes
local_search_req = 0.02

#Sendes inn i ALNS og handler om hvor mye du skal destroye med operatorer altså hvor mange aktiviteter som skal ryke?
#Maxen du kan fjerne er halve løsningen
destruction_degree = 0.5

# Simulated annealing temperatures -- TODO: these must be tuned
start_temperature = 50 
end_temperature = 10
cooling_rate = 0.95

# Distance Matrix
# Buses in Oslo om average drive in 25 kms/h.
speed = 40
rush_factor = 2

# Weight score for Acceptance Criterion and giving weights [sigma1, sigma2, sigma3, 0]. Må se på hva disse tallene skal være
weight_scores = [1, 2, 3, 0]