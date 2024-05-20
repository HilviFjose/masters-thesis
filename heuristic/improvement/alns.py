#import numpy.random as rnd 
import numpy as np 
import copy
from tqdm import tqdm 
from helpfunctions import *
import time 
import os
from heuristic.improvement.operator.destroy_operators import DestroyOperators
from heuristic.improvement.operator.repair_operators import RepairOperators
from multipro import process_parallel


from config.main_config import *
from heuristic.improvement.local_search import LocalSearch

class ALNS:
    def __init__(self, destruction_degree_interval, weight_score_better, weight_score_accepted, weight_score_bad, weight_score_best, 
                 reaction_factor, local_search_req, iterations_update_default, current_route_plan, criterion, constructor, mp_config, folder_path): 

        self.folder_path = folder_path

        self.destroy_operators = []
        self.repair_operators = []

        self.current_route_plan = copy.deepcopy(current_route_plan)
        self.best_route_plan = copy.deepcopy(current_route_plan)
        self.criterion = criterion
        self.constructor = constructor

        self.weight_score_better = weight_score_better
        self.weight_score_accepted = weight_score_accepted
        self.weight_score_bad = weight_score_bad
        self.weight_score_best = weight_score_best
        self.reaction_factor = reaction_factor
        self.local_search_req = local_search_req
        self.iterations_update = iterations_update_default
        self.iterationNum = 0

        self.destruction_degree_interval = destruction_degree_interval
        self.destruction_degree = 0
        

        destroy_operators = DestroyOperators(self)
        repair_operators = RepairOperators(self)
        self.set_operators(destroy_operators, repair_operators)

        self.d_weights = np.ones(len(self.destroy_operators), dtype=np.float16)
        self.r_weights = np.ones(len(self.repair_operators), dtype=np.float16)
        self.d_scores = np.ones(len(self.destroy_operators), dtype=np.float16)
        self.r_scores = np.ones(len(self.repair_operators), dtype=np.float16)
        # Kan ikke count bare være at vi hver 10 iterasjon eller noe oppdaterer?
        self.d_count = np.zeros(len(self.destroy_operators), dtype=np.float16)
        self.r_count = np.zeros(len(self.repair_operators), dtype=np.float16)

        self.mp_config = mp_config
        self.main_config = constructor.main_config 

        self.random_numbers = np.round(np.random.uniform(low=destruction_degree_interval[0], high=destruction_degree_interval[1], size=self.main_config.iterations),1)

        self.random_states_for_parallell = [np.random.RandomState() for i in range(1, self.main_config.num_of_paralell_iterations+1)]
        '''
        Skal fikse at den kjører i parallell slika t det blir rikig 
        '''
        
    def doIteration(self, input_tuple, random_states_for_parallell): 
        candidate_route_plan = input_tuple[0]
        parNum = input_tuple[1]
        #print("parNum", parNum)
        #print("random_states_for_parallell", random_states_for_parallell)
        random_state = random_states_for_parallell[parNum-1]
        destroy = self.select_operator(self.destroy_operators, self.d_weights, random_state)
           
        # Select repair method
        repair = self.select_operator(self.repair_operators, self.r_weights, random_state)
  

        #Destroy solution 
        d_operator = self.destroy_operators[destroy]

        candidate_route_plan = d_operator(candidate_route_plan) 

        candidate_route_plan.updateObjective(self.iterationNum, self.main_config.iterations)
        #candidate_route_plan.printSolution(str(self.iterationNum)+"candidate_after_destroy_parallel_"+str(parNum),d_operator.__name__)

        self.d_count[destroy] += 1

        # Repair solution
        
        r_operator = self.repair_operators[repair]
        #print("repair operator", r_operator.__name__)
        #start_time = time.perf_counter()
        candidate_route_plan = r_operator(candidate_route_plan, self.iterationNum, self.main_config.iterations)
        #end_time = time.perf_counter()
        #print("destroy used time", str(end_time - start_time))
        candidate_route_plan.updateObjective(self.iterationNum, self.main_config.iterations)
        #candidate_route_plan.printSolution(str(self.iterationNum)+"candidate_after_repair_parallel_"+str(parNum), r_operator.__name__)
        self.r_count[repair] += 1

        weight_score = self.update_weights(self.best_route_plan, self.current_route_plan, candidate_route_plan, self.criterion)
       
        # Update scores
        self.d_scores[destroy] += weight_score
        self.r_scores[repair] += weight_score

        return candidate_route_plan, destroy, repair

        
    def iterate(self, num_iterations):
        
        for i in tqdm(range(num_iterations), colour='#39ff14'):
            self.iterationNum += 1
            candidate_route_plan = copy.deepcopy(self.current_route_plan)

            #self.current_route_plan.printSolution(str(self.iterationNum)+"candidate_before_destroy", None)
            self.destruction_degree = self.random_numbers[self.iterationNum-1]
            
            if not self.main_config.doParalellDestroyRepair:
                #Uten parallell
                candidate_route_plan, destroy, repair = self.doIteration((candidate_route_plan, 1))

            else:
                #Kjører paralelt. 
                
                jobs = [(candidate_route_plan, parNum) for parNum in range(1, self.main_config.num_of_paralell_iterations+1)]
                
                results = process_parallel(self.doIteration, function_kwargs={'random_states_for_parallell': self.random_states_for_parallell}, jobs=jobs, mp_config=self.mp_config, paralellNum=self.main_config.num_of_paralell_iterations)
                candidate_route_plan, destroy, repair = results[0]
                for result in results[1:]: 
                    if checkCandidateBetterThanBest(result[0].objective, candidate_route_plan.objective): 
                        candidate_route_plan, destroy, repair = result
             
            #candidate_route_plan.printSolution(str(self.iterationNum)+'candidate_after_paralell', "ingen operator")

            if isPromisingLS(candidate_route_plan.objective, self.best_route_plan.objective, self.local_search_req) == True: 
                #print("Solution promising. Doing local search.")
                localsearch = LocalSearch(candidate_route_plan, self.iterationNum, num_iterations)
                
                if not self.main_config.doParalellLocalSearch:
                    #Uten parallell
                    candidate_route_plan = localsearch.do_local_search()

                else: 
                    #Med parallell 
                    results = process_parallel(localsearch.do_local_search_on_day, function_kwargs={} , jobs=[day for day in range(1, self.main_config.days+1) ], mp_config=self.mp_config, paralellNum=self.main_config.days)
                    #print("GJOR LOKALSØKET I PARALELL")
                    for day in range(1, self.main_config.days+1): 
                        candidate_route_plan.routes[day] = results[day-1].routes[day]
                    
                candidate_route_plan.updateObjective(self.iterationNum, num_iterations)
               
                
            #candidate_route_plan.printSolution(str(self.iterationNum)+"candidate_after_local_search", "ingen operator")
            
            
            #if candidate_route_plan.objective[0] != candidate_route_plan.getOriginalObjective():
                #print(f" ALNS: Penalty in first objective: {candidate_route_plan.getOriginalObjective() - candidate_route_plan.objective[0]}. Original Objective: {candidate_route_plan.getOriginalObjective()}, Updated Objective: {candidate_route_plan.objective[0]} ")
        
            # Compare solutions
             #Her settes current, til å være det det skal være 
            self.best_route_plan, self.current_route_plan = self.update_current_best( self.best_route_plan, self.current_route_plan, candidate_route_plan)
        
            #candidate_route_plan.printSolution(str(self.iterationNum)+"candidate_final", "ingen operator")
            
            # After a certain number of iterations, update weight
            if (i+1) % (self.iterations_update*self.main_config.iterations) == 0:
                # Update weights with scores
                for destroy in range(len(self.d_weights)):
                    if self.d_count[destroy] != 0: 
                        self.d_weights[destroy] = self.d_weights[destroy] * (1 - self.reaction_factor) + (self.reaction_factor * self.d_scores[destroy] / self.d_count[destroy])
                for repair in range(len(self.r_weights)):
                    if self.r_count[repair] != 0: 
                        self.r_weights[repair] = self.r_weights[repair] * (1 - self.reaction_factor) + (self.reaction_factor * self.r_scores[repair] / self.r_count[repair])

                # Reset scores
                self.d_scores = np.ones(
                    len(self.destroy_operators), dtype=np.float16)
                self.r_scores = np.ones(
                    len(self.repair_operators), dtype=np.float16)
                
        # Do local search to local optimum before returning last iteration
        #self.best_route_plan.printSolution("candidate_before_final_local_search", "ingen operator")
        localsearch = LocalSearch(self.best_route_plan, self.main_config.iterations, self.main_config.iterations) #Egentlig iterasjon 0, men da blir det ingen penalty
        self.best_route_plan = localsearch.do_local_search_to_local_optimum()
        self.best_route_plan.updateObjective(self.main_config.iterations, self.main_config.iterations) #Egentlig iterasjon 0, men da blir det ingen penalty
                
        return self.best_route_plan
    
    def set_operators(self, destroy_operators, repair_operators):
        # Add destroy operators
        
        self.add_destroy_operator(destroy_operators.random_patient_removal)
        self.add_destroy_operator(destroy_operators.random_treatment_removal)
        self.add_destroy_operator(destroy_operators.random_visit_removal)
        self.add_destroy_operator(destroy_operators.random_activity_removal)
        
        self.add_destroy_operator(destroy_operators.worst_deviation_patient_removal)
        self.add_destroy_operator(destroy_operators.worst_deviation_treatment_removal)
        self.add_destroy_operator(destroy_operators.worst_deviation_visit_removal)
        self.add_destroy_operator(destroy_operators.worst_deviation_activity_removal)

        self.add_destroy_operator(destroy_operators.cluster_distance_patients_removal)
        self.add_destroy_operator(destroy_operators.cluster_distance_activities_removal)
       
        self.add_destroy_operator(destroy_operators.spread_distance_patients_removal)
        self.add_destroy_operator(destroy_operators.spread_distance_activities_removal)
        
        self.add_destroy_operator(destroy_operators.related_patients_removal)
        self.add_destroy_operator(destroy_operators.related_treatments_removal)
        self.add_destroy_operator(destroy_operators.related_visits_removal)

        # Add repair operators
        self.add_repair_operator(repair_operators.greedy_repair)
        #self.add_repair_operator(repair_operators.random_repair)
        self.add_repair_operator(repair_operators.complexity_repair)
        self.add_repair_operator(repair_operators.regret_k_repair)


    # Add operator to the heuristic instance
        
    def add_destroy_operator(self, operator):
        self.destroy_operators.append(operator)

    def add_repair_operator(self, operator):
        self.repair_operators.append(operator)


    # Select destroy/repair operator
    @staticmethod
    def select_operator(operators, weights, random_state):
        w = weights / np.sum(weights)
        a = [i for i in range(len(operators))]
        return random_state.choice(a=a, p=w)
    #
    def update_weights(self, best_route_plan, current_route_plan, candidate_route_plan, criterion):
        if criterion.accept_criterion( current_route_plan.objective, candidate_route_plan.objective):
            if checkCandidateBetterThanBest(candidate_route_plan.objective, current_route_plan.objective):
                # Solution is better
                weight_score = self.weight_score_better
            else:
                # Solution is not better, but accepted
                weight_score = self.weight_score_accepted
                #Sjekker om løsningen blir godkjent som følge av acceptancecriteria
                
        else:
            # Solution is rejected
            weight_score = self.weight_score_bad

        # Check if solution is new global best
        if checkCandidateBetterThanBest(candidate_route_plan.objective, best_route_plan.objective):
            weight_score = self.weight_score_best 

        return weight_score
    
    def update_current_best(self, best_route_plan, current_route_plan, candidate_route_plan):
        if checkCandidateBetterThanBest(candidate_route_plan.objective, best_route_plan.objective) and candidate_route_plan.objective[0] == candidate_route_plan.getOriginalObjective():
            best_route_plan = copy.deepcopy(candidate_route_plan)
            current_route_plan = copy.deepcopy(candidate_route_plan)
            """
            # Open the file for writing in the correct directory
            file_path = os.path.join(self.folder_path, "0config_info.txt")
            with open(file_path, "a") as file: 
                file.write(f"ALNS iteration {self.iterationNum} is new global best, objective {best_route_plan.objective}\n")
            """
            return best_route_plan, current_route_plan
        
        if self.criterion.accept_criterion_without_weights_update( current_route_plan.objective, candidate_route_plan.objective):
            current_route_plan = copy.deepcopy(candidate_route_plan)

        return best_route_plan, current_route_plan

    '''
    # Evaluate candidate
    def evaluate_candidate(self, best_route_plan, current_route_plan, candidate_route_plan, criterion):
        # If solution is accepted by criterion (simulated annealing)
        if criterion.accept_criterion( current_route_plan.objective, candidate_route_plan.objective):
            if checkCandidateBetterThanBest(candidate_route_plan.objective, current_route_plan.objective):
                # Solution is better
                weight_score = self.weight_score_better
            else:
                # Solution is not better, but accepted
                weight_score = self.weight_score_accepted
            current_route_plan = copy.deepcopy(candidate_route_plan)
        else:
            # Solution is rejected
            print("Candidate very bad and not accepted.")
            weight_score = self.weight_score_bad

        # Check if solution is new global best
        if checkCandidateBetterThanBest(candidate_route_plan.objective, best_route_plan.objective):
            print("ALNS iteration ", self.iterationNum, " is new global best")
            best_route_plan = copy.deepcopy(candidate_route_plan)
            weight_score = self.weight_score_best 

            # Open the file for writing in the correct directory
            file_path = os.path.join(self.folder_path, "0config_info.txt")
            with open(file_path, "a") as file: 
                file.write(f"ALNS iteration {self.iterationNum} is new global best\n")

        return best_route_plan, current_route_plan, weight_score    
    '''
    