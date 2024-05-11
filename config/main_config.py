from datetime import datetime, timedelta
import math

#Number of constructed solutions 
num_of_constructions = 20  #OBS: Bør ikke settes til over 5, for er usikkert hvro mye prosessoren tåler

# Adaptive Weights: Brukes i ALNS for å telle når man skal oppdatere vekter på operatorer
reaction_factor_default = 0.7

# Iterations in ALNS
iterations = 400

# Requirement for how good a candidate must be before doing the local search. -- TODO: these must be tuned
local_search_req_default = 0.02

# k-repair value
k = 3

#The amount of activities to remove in destroy operators
#destruction_degree = 0.4
destruction_degree_high_default = 0.3
destruction_degree_low_default = 0.15

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
weight_score_best_default = 15
weight_score_better_default = 10
weight_score_accepted_default = 5
weight_score_bad = 0

# Iterations between each weight update in ALNS
iterations_update_default = 0.1

# Penalty in first objective for infeasible solution
# TODO: these must be tuned
penalty_patient = 20        # Penalty per illegal patient (Not allocated patient from the pre-allocated patient list)
penalty_treat = 10          # Penalty per illegal treatment
penalty_visit = 5           # Penalty per illegal visit  
penalty_act = 3             # Penalty per illegal activity 

# Weights for objectives
#weight_C = 0.0              # Max continuity of care
weight_DW = 0.3             # Balance daily workload
weight_WW = 0.3             # Balance weekly workload
weight_S = 0.2              # Min skill difference
weight_SG = 0.2             # Balance specialist/generalist

#Planning period
days = 5

#Depot
depot = (59.9365, 10.7396)

#Insertor choises [0,1,2, 3, 4] for [simple, better with max reg1, better with max regret2, better, best ]
construction_insertor = 2 #W
repair_insertor = 1
illegal_repair_insertor = 2

max_num_regret1 = 50
max_num_regret2 = 100

#Insertor som kan brukes en andel av gangene 
fraction_repair_insertor = 1
frequecy_of_fraction_insertion = 0.01
modNum_for_fraction_insertion = math.ceil(iterations*frequecy_of_fraction_insertion) 


#Number of paralell processes 
num_of_paralell_iterations = 3

#Boolean for paralell 
doParalellLocalSearch = True
doParalellDestroyRepair = True

