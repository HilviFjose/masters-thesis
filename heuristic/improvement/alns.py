import numpy.random as rnd 
import numpy as np 
import copy
from tqdm import tqdm 
from helpfunctions import *
import time 


from config.main_config import *
from heuristic.improvement.local_search import LocalSearch

class ALNS:
    def __init__(self,weights, reaction_factor, current_route_plan, criterion,
                     constructor, rnd_state=rnd.RandomState()): 
        self.destroy_operators = []
        self.repair_operators = []

        self.rnd_state = rnd_state
        self.reaction_factor = reaction_factor

        self.current_route_plan = copy.deepcopy(current_route_plan)
        self.best_route_plan = copy.deepcopy(current_route_plan)
        self.criterion = criterion
        self.constructor = constructor
        self.local_search_req = local_search_req
        self.iterationNum = 0
        self.weight_scores = weights

        
        
        
    def iterate(self, num_iterations):
        found_solutions = {}
        
        # weights er vekter for å velge operator, score og count brukes for oppdatere weights
        d_weights = np.ones(len(self.destroy_operators), dtype=np.float16)
        r_weights = np.ones(len(self.repair_operators), dtype=np.float16)
        d_scores = np.ones(len(self.destroy_operators), dtype=np.float16)
        r_scores = np.ones(len(self.repair_operators), dtype=np.float16)
        # Kan ikke count bare være at vi hver 10 iterasjon eller noe oppdaterer?
        d_count = np.zeros(len(self.destroy_operators), dtype=np.float16)
        r_count = np.zeros(len(self.repair_operators), dtype=np.float16)

        for i in tqdm(range(num_iterations), colour='#39ff14'):
            self.iterationNum += 1
            candidate_route_plan = copy.deepcopy(self.current_route_plan)
            already_found = False

            #Select destroy method 
            destroy = self.select_operator(self.destroy_operators, d_weights, self.rnd_state)
           
            # Select repair method
            repair = self.select_operator(self.repair_operators, r_weights, self.rnd_state)
            
            #Destroy solution 
            d_operator = self.destroy_operators[destroy]

            self.current_route_plan.printSolution(str(self.iterationNum)+"candidate_before_destroy", d_operator.__name__)
            print("destroy operator", d_operator.__name__)
            #start_time = time.perf_counter()
            candidate_route_plan, removed_activities, destroyed = d_operator(candidate_route_plan) 
            #end_time = time.perf_counter()
            #print("destroy used time", str(end_time - start_time))  
            candidate_route_plan.updateObjective(self.iterationNum, num_iterations)
            candidate_route_plan.printSolution(str(self.iterationNum)+"candidate_after_destroy",d_operator.__name__)

            if not destroyed:
                break

            d_count[destroy] += 1

            # Repair solution
            
            r_operator = self.repair_operators[repair]
            print("repair operator", r_operator.__name__)
            #start_time = time.perf_counter()
            candidate_route_plan = r_operator(candidate_route_plan, self.iterationNum, num_iterations)
            #end_time = time.perf_counter()
            #print("destroy used time", str(end_time - start_time))
            candidate_route_plan.updateObjective(self.iterationNum, num_iterations)
            candidate_route_plan.printSolution(str(self.iterationNum)+"candidate_after_repair", r_operator.__name__)
            r_count[repair] += 1

            
            if isPromisingLS(candidate_route_plan.objective, self.best_route_plan.objective, self.local_search_req) == True: 
                print("Solution promising. Doing local search.")
                localsearch = LocalSearch(candidate_route_plan, self.iterationNum, num_iterations)
                candidate_route_plan = localsearch.do_local_search()
                candidate_route_plan.updateObjective(self.iterationNum, num_iterations)
                
            candidate_route_plan.printSolution(str(self.iterationNum)+"candidate_after_local_search", "ingen operator")
            #TODO: Skal final candiate printes lenger nede? 
            if candidate_route_plan.objective[0] != candidate_route_plan.getOriginalObjective():
                print(f" ALNS: Penalty in first objective: {candidate_route_plan.getOriginalObjective() - candidate_route_plan.objective[0]}. Original Objective: {candidate_route_plan.getOriginalObjective()}, Updated Objective: {candidate_route_plan.objective[0]} ")
        
            # Konverterer til hexa-string for å sjekke om vi har samme løsning. Evaluerer og scores oppdateres kun hvis vi har en løsning som ikke er funnet før
            if hash(str(candidate_route_plan)) == hash(str(self.current_route_plan)) and hash(str(candidate_route_plan)) in found_solutions.keys():
                already_found = True
            else:
                found_solutions[hash(str(self.current_route_plan))] = 1

            if not already_found:
                # Compare solutions
                self.best_route_plan, self.current_route_plan, weight_score = self.evaluate_candidate(
                    self.best_route_plan, self.current_route_plan, candidate_route_plan, self.criterion)
                # Update scores
                d_scores[destroy] += weight_score
                r_scores[repair] += weight_score
            
            candidate_route_plan.printSolution(str(self.iterationNum)+"candidate_final", "ingen operator")
            
            # After a certain number of iterations, update weight
            if (i+1)*iterations_update == 0:
                # Update weights with scores
                for destroy in range(len(d_weights)):
                    if d_count[destroy] != 0: 
                        d_weights[destroy] = d_weights[destroy] * (1 - self.reaction_factor) + (self.reaction_factor * d_scores[destroy] / d_count[destroy])
                for repair in range(len(r_weights)):
                    if r_count[repair] != 0: 
                        r_weights[repair] = r_weights[repair] * (1 - self.reaction_factor) + (self.reaction_factor * r_scores[repair] / r_count[repair])

                # Reset scores
                d_scores = np.ones(
                    len(self.destroy_operators), dtype=np.float16)
                r_scores = np.ones(
                    len(self.repair_operators), dtype=np.float16)
                
            # Do local search to local optimum before returning last iteration
            self.best_route_plan.printSolution("candidate_before_final_local_search", "ingen operator")
            localsearch = LocalSearch(self.best_route_plan, iterations, iterations) #Egentlig iterasjon 0, men da blir det ingen penalty
            self.best_route_plan = localsearch.do_local_search_to_local_optimum()
            self.best_route_plan.updateObjective(iterations, iterations) #Egentlig iterasjon 0, men da blir det ingen penalty
                
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
        #self.add_destroy_operator(destroy_operators.related_treatments_removal)
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
    def select_operator(operators, weights, rnd_state):
        w = weights / np.sum(weights)
        a = [i for i in range(len(operators))]
        return rnd_state.choice(a=a, p=w)
    
    # Evaluate candidate
    def evaluate_candidate(self, best_route_plan, current_route_plan, candidate_route_plan, criterion):
        # If solution is accepted by criterion (simulated annealing)
        if criterion.accept_criterion(self.rnd_state, current_route_plan.objective, candidate_route_plan.objective):
            if checkCandidateBetterThanBest(candidate_route_plan.objective, current_route_plan.objective):
                # Solution is better
                weight_score = weight_scores[0]
            else:
                # Solution is not better, but accepted
                weight_score = weight_scores[1]

            current_route_plan = copy.deepcopy(candidate_route_plan)
        else:
            # Solution is rejected
            print("Candidate very bad and not accepted.")
            weight_score = weight_scores[2]

        # Check if solution is new global best
        if checkCandidateBetterThanBest(candidate_route_plan.objective, best_route_plan.objective):
            print("ALNS iteration ", self.iterationNum, " is new global best")
            best_route_plan = copy.deepcopy(candidate_route_plan)
            weight_score = weight_scores[3]

        return best_route_plan, current_route_plan, weight_score    

    