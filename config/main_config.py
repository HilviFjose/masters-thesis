from datetime import datetime, timedelta
import math

#TODO: Endre til verdier som er riktige for oss. Hentet fra Anna
#Denne fila inneholder variabler som brukes i ALNSen

# Adaptive Weights: Brukes i ALNS for å telle når man skal oppdatere vekter på operatorer
reaction_factor_default = 0.7
reaction_factor_interval = 0.4, 0.5, 0.6, 0.7, 0.8

# Iterations in ALNS
iterations = 5

# Requirement for how good a candidate must be before doing the local search. -- TODO: these must be tuned
local_search_req_default = 0.02
local_search_interval = 0.01, 0.02, 0.03, 0.04, 0.05

# k-repair value
k = 3

#The amount of activities to remove in destroy operators
#destruction_degree = 0.4
destruction_degree_beginning = 0.4
destruction_degree_end = 0.2

# Simulated annealing temperatures -- TODO: these must be tuned
start_temperature = 60
end_temperature = 10
cooling_rate = 0.96

# Distance Matrix
# Buses in Oslo om average drive in 25 kms/h.
speed = 40
rush_factor = 2

# Weight score for Acceptance Criterion and giving weights [better, not better but accepted, not better, global best]. Må se på hva disse tallene skal være 
weight_score_best_default = 15
weight_score_better_default = 10
weight_score_accepted_default = 5
weight_score_bad_default = 0

weight_score_best_interval = 10, 15
weight_score_better_interval = 1, 5, 10
weight_score_accepted_interval = 1, 5, 10


# Iterations between each weight update in ALNS
iterations_update_default = 0.1
iterations_update_interval = 0.1, 0.2, 0.3, 0.4, 0.5

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
weight_S = 0.2              # Min skill difference
weight_SG = 0.2             # Balance specialist/generalist

#Planning period
days = 5

#Depot
depot = (59.9365, 10.7396)

#Number of constructed solutions 
num_of_constructions = 1

#Insertor choises [0,1,2, 3] for [simple, better with limited branches in search, better, best ]
construction_insertor = 2 #W
repair_insertor = 1
illegal_repair_insertor = 2
better_repair_insertor = 1 

max_num_explored_branches = 50

#How often should we use better insertion 
frequecy_of_better_insertion = 0.2
modNum_for_better_insertion = math.ceil(iterations*frequecy_of_better_insertion) 