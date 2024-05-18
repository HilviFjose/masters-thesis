from datetime import datetime, timedelta
import math

class MainConfig:
    def __init__(self):

        #Number of constructed solutions 
        self.num_of_constructions = 20  #OBS: Bør ikke settes til over 5, for er usikkert hvro mye prosessoren tåler

        # Iterations in ALNS
        self.iterations = 100

        #Number of paralell processes 
        self.num_of_paralell_iterations = 10

        #Boolean for paralell 
        self.doParalellLocalSearch = True
        self.doParalellDestroyRepair = True

        #Insertor choises [0,1,2, 3, 4] for [simple, better with max reg1, better with max regret2, better, best ]
        self.construction_insertor = 1 #W
        self.repair_insertor = 1
        self.illegal_repair_insertor = 2

        self.max_num_regret1 = 60
        self.max_num_regret2 = 80

        #Insertor som kan brukes en andel av gangene 
        self.fraction_repair_insertor = 2
        self.frequecy_of_fraction_insertion = 0.05
        self.modNum_for_fraction_insertion = math.ceil(self.iterations*self.frequecy_of_fraction_insertion) 

        # Requirement for how good a candidate must be before doing the local search. -- TODO: these must be tuned
        self.local_search_req_default = 0.05

        # Adaptive Weights: Brukes i ALNS for å telle når man skal oppdatere vekter på operatorer
        self.reaction_factor_default = 0.25

        # Weight score for Acceptance Criterion and giving weights [better, not better but accepted, not better, global best]. Må se på hva disse tallene skal være 
        self.weight_score_best_default = 35
        self.weight_score_better_default = 15
        self.weight_score_accepted_default = 5
        self.weight_score_bad = 0

        # Iterations between each weight update in ALNS
        self.iterations_update_default = 0.1

        # k-repair value
        self.k = 3

        #The amount of activities to remove in destroy operators
        self.destruction_degree_high_default = 0.5
        self.destruction_degree_low_default = 0.15

        # Simulated annealing temperatures -- TODO: these must be tuned
        #start_temperature = 60
        #end_temperature = 10
        #cooling_rate = 0.96

        self.deviation_from_best = 0.05
        self.prob_of_choosing = 0.5 
        self.rate_T_start_end = 0.2 

        # Distance Matrix
        # Buses in Oslo om average drive in 25 kms/h.
        #self.speed = 40
        #self.rush_factor = 2

        # Penalty in first objective for infeasible solution
        # TODO: these must be tuned
        self.penalty_patient = 20        # Penalty per illegal patient (Not allocated patient from the pre-allocated patient list)
        self.penalty_treat = 10          # Penalty per illegal treatment
        self.penalty_visit = 5           # Penalty per illegal visit  
        self.penalty_act = 3             # Penalty per illegal activity 

        # Weights for objectives
        self.weight_DW = 1             # Balance daily workload
        self.weight_WW = 1             # Balance weekly workload
        self.weight_S = 1/3              # Min skill difference
        self.weight_SG = 1             # Balance specialist/generalist

        #Planning period
        self.days = 5

        #Depot
        self.depot = (59.9365, 10.7396)





