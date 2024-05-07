from datetime import datetime, timedelta
import math

#TODO: Endre til verdier som er riktige for oss. Hentet fra Anna
#Denne fila inneholder variabler som brukes i ALNSen

# Adaptive Weights: Brukes i ALNS for å telle når man skal oppdatere vekter på operatorer
reaction_factor = 0.7

# Iterations in ALNS
iterations = 30

# Requirement for how good a candidate must be before doing the local search. -- TODO: these must be tuned
local_search_req = 0.02

# k-repair value
k = 3

#The amount of activities to remove in destroy operators
#destruction_degree = 0.4
destruction_degree_beginning = 0.4
destruction_degree_end = 0.2

# Simulated annealing temperatures -- TODO: these must be tuned
#start_temperature = 60
#end_temperature = 10
#cooling_rate = 0.96

sim_annealing_diff = 0.05
prob_of_choosing = 0.5 
rate_T_start_end = 0.2 

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
weight_S = 0.2              # Min skill difference
weight_SG = 0.2             # Balance specialist/generalist

#Planning period
days = 5

#Depot
depot = (59.9365, 10.7396)

#Number of constructed solutions 
num_of_constructions = 3  #OBS: Bør ikke settes til over 5, for er usikkert hvro mye prosessoren tåler

#Insertor choises [0,1,2, 3] for [simple, better with limited regret 1, better sith limited regeret 2, better, best ]
construction_insertor = 1 #W
repair_insertor = 1
illegal_repair_insertor = 1
better_repair_insertor = 1 

max_num_explored_branches = 100

max_num_regret1 = 20
max_num_regret2 = 100

#How often should we use better insertion 
frequecy_of_better_insertion = 0.01
modNum_for_better_insertion = math.ceil(iterations*frequecy_of_better_insertion) 


#Number of paralell processes 
num_of_paralell_iterations = 1