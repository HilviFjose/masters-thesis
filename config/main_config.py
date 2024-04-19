from datetime import datetime, timedelta

#TODO: Endre til verdier som er riktige for oss. Hentet fra Anna
#Denne fila inneholder variabler som brukes i ALNSen

# Adaptive Weights: Brukes i ALNS for å telle når man skal oppdatere vekter på operatorer
reaction_factor = 0.7

# Iterations in ALNS
iterations = 10

# Requirement for how good a candidate must be before doing the local search. -- TODO: these must be tuned
local_search_req = 0.02

# k-repair value
k = 3

# Insertor types [standard = 0, better = 1, best = 2]
insertor_repair = 0
insertor_construction = 1

#The amount of activities to remove in destroy operators
destruction_degree = 0.4

# Simulated annealing temperatures -- TODO: these must be tuned
start_temperature = 60
end_temperature = 10
cooling_rate = 0.96

# Distance Matrix
# Buses in Oslo om average drive in 25 kms/h.
speed = 40
rush_factor = 2

# Weight score for Acceptance Criterion and giving weights [better, not better but accepted, not better, global best]. Må se på hva disse tallene skal være 
weight_scores = [10, 5, 0, 15]

# Iterations between each weight update in ALNS
iterations_update = 0.1

# Penalty in first objective for infeasible solution
# TODO: these must be tuned
penalty_patient = 20        # Penalty per illegal patient (Not allocated patient from the pre-allocated patient list)
penalty_treat = 10          # Penalty per illegal treatment
penalty_visit = 5           # Penalty per illegal visit  
penalty_act = 3             # Penalty per illegal activity 

# Weights for objectives
weight_C = 0.0              # Max continuity of care
weight_DW = 0.3             # Balance daily workload
weight_WW = 0.3             # Balance weekly workload
weight_S = 0.4              # Min skill difference
weight_SG = 0.0             # Balance specialist/generalist

