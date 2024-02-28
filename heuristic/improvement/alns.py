import numpy.random as rnd 
import numpy as np 
import copy
from tqdm import tqdm 
from helpfunctions import *

from config.main_config import *
from heuristic.improvement.local_search import LocalSearch

class ALNS:
    def __init__(self, weights, reaction_factor, current_route_plan, current_objective, initial_infeasible_set, criterion,
                    destruction_degree, constructor, rnd_state=rnd.RandomState()): 
        self.destroy_operators = []
        self.repair_operators = []
        #Spinner hjulet med ny styrke hver gang
        self.rnd_state = rnd_state
        self.reaction_factor = reaction_factor
        #Litt uklart hva dette er, er det de som ikke har klart å bli plassert, eller er det pasienter som ikke har blitt plassert
        self.initial_infeasible_set = initial_infeasible_set 
        #Disse kommer fra config mail filen 
        self.weights = weights
        self.route_plan = current_route_plan
        self.destruction_degree = destruction_degree
        self.objective = current_objective
        self.criterion = criterion
        self.constructor = constructor
        #TODO: Finne ut om vi skal ha denn klassen med. Eller om det har noe med ALNS å gjøre
        #self.destroy_repair_updater = Destroy_Repair_Updater(constructor)

    
    def iterate(self, num_iterations):
        weights = np.asarray(self.weights, dtype=np.float16)
        
        current_route_plan = copy.deepcopy(self.route_plan)
        best = copy.deepcopy(self.route_plan)
        current_objective = copy.deepcopy(self.objective)
        best_objective = copy.deepcopy(self.objective)
        current_infeasible_set = copy.deepcopy(self.initial_infeasible_set)
        best_infeasible_set = copy.deepcopy(self.initial_infeasible_set)
        
        #TODO: Forstå hva disse to parameterne gjør 
        found_solutions = {}
        initial_route_plan = copy.deepcopy(self.route_plan)

        # weights er vekter for å velge operator, score og count brukes for oppdatere weights
        d_weights = np.ones(len(self.destroy_operators), dtype=np.float16)
        r_weights = np.ones(len(self.repair_operators), dtype=np.float16)
        d_scores = np.ones(len(self.destroy_operators), dtype=np.float16)
        r_scores = np.ones(len(self.repair_operators), dtype=np.float16)
        # Kan ikke count bare være at vi hver 10 iterasjon eller noe oppdaterer?
        d_count = np.zeros(len(self.destroy_operators), dtype=np.float16)
        r_count = np.zeros(len(self.repair_operators), dtype=np.float16)

        '''
        print("lager local search")
        candidate = current_route_plan
        localsearch = LocalSearch(candidate)
        candidate = localsearch.do_local_search()
        print("NY LØSNING FRA LØKALSØK")
        candidate.printSolution()
        print(candidate.objective)
        '''

        for i in tqdm(range(num_iterations), colour='#39ff14'):
            #Hva er dette? Løsning vi allerede har funnet??
            already_found = False

            #Select destroy method 
            destroy = self.select_operator(
                self.destroy_operators, d_weights, self.rnd_state)

            # Select repair method
            repair = self.select_operator(
                self.repair_operators, r_weights, self.rnd_state)
            
            #Destroy solution 
            #henter ut d_operator objekt fra index i destroy operator lister
            #Har en liste over funskjoner og henter ut en av de og kaller denne funskjoenen d_operator 
            #deretter kalles denne ufnskjoenen med de gitte parameterne 
            d_operator = self.destroy_operators[destroy]
            destroyed_route_plan, removed_activities, destroyed = d_operator(
                current_route_plan)
            
            print("d_operator",d_operator)
            
            if not destroyed:
                break
        
            d_count[destroy] += 1

            # Update solution
            # Undersøke hva denne filen gjør. Er den kun aktuell på lunde sin?
            #updated_route_plan = self.destroy_repair_updater.update_solution(destroyed_route_plan, index_removed, disruption_time)
          
            # Fix solution
            #TODO: Lage repair iteratorer, de er kommentert ut, mens vi jobber med lokalsøket, på samme måte som destroy operatorer 
            
            r_operator = self.repair_operators[repair]
            candidate, candidate_objective, candidate_infeasible_set = r_operator(
                destroyed_route_plan, removed_activities, current_infeasible_set, current_route_plan, index_removed_activities)
    

            r_count[repair] += 1
           
            # Local search if solution is promising
            local_search_requirement = 0.05 # TODO: Legge inn i main config
            if candidate_objective.isPromising(candidate_objective, best_objective, local_search_requirement): # TODO: Lage denne i helpfunctions
                print("lager local search")
                candidate_for_local_search = copy.deepcopy(candidate)
                localsearch = LocalSearch(candidate_for_local_search)
                candidate = localsearch.do_local_search()
            """
            # Compare solutions
            best, best_objective, best_infeasible_set, current_route_plan, current_objective, current_infeasible_set, weight_score = self.evaluate_candidate(
                best, best_objective, best_infeasible_set,
                current_route_plan, current_objective, current_infeasible_set,
                candidate, candidate_objective, candidate_infeasible_set, self.criterion)
            
            # Konverterer til hexa-string for å sjekke om vi har samme løsning. Scores oppdateres kun hvis vi har en løsning som ikke er funnet før
            if hash(str(candidate)) == hash(str(current_route_plan)) and hash(str(candidate)) in found_solutions.keys():
                already_found = True
            else:
                found_solutions[hash(str(current_route_plan))] = 1

            if not already_found:
                # Update scores
                d_scores[destroy] += weight_score
                r_scores[repair] += weight_score

            
            # After a certain number of iterations, update weight
            # TODO: Noen får denne i oppgave
            if (i+1) % N_U == 0: #TODO: Se på i sammenheng med initial_improvement_config. 
                # Update weights with scores
                for destroy in range(len(d_weights)):
                    d_weights[destroy] = d_weights[destroy] * \
                        (1 - self.reaction_factor) + \
                        (self.reaction_factor *
                         d_scores[destroy] / d_count[destroy])
                for repair in range(len(r_weights)):
                    r_weights[repair] = r_weights[repair] * \
                        (1 - self.reaction_factor) + \
                        (self.reaction_factor *
                         r_scores[repair] / r_count[repair])

                # Reset scores
                d_scores = np.ones(
                    len(self.destroy_operators), dtype=np.float16)
                r_scores = np.ones(
                    len(self.repair_operators), dtype=np.float16)
            """
        return best, best_objective, best_infeasible_set
    
    def set_operators(self, operators):
        # Add destroy operators
        self.add_destroy_operator(operators.worst_route_removal)
        self.add_destroy_operator(operators.random_route_removal)

        # Add repair operators
        self.add_repair_operator(operators.greedy_repair)

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
    def evaluate_candidate(self, best, best_objective, best_infeasible_set, current, current_objective,
                           current_infeasible_set, candidate, candidate_objective, candidate_infeasible_set,
                           criterion):
        # If solution is accepted by criterion (simulated annealing)
        if criterion.accept_criterion(self.rnd_state, current_objective, candidate_objective):
            # TODO: Endre objektivvurdering
            if checkCandidateBetterThanCurrent(candidateObj= candidate_objective, currObj= current_objective):
                # Solution is better
                # TODO: Legge inn som sigma123 i main_config i stedet. 
                weight_score = 1
            else:
                # Solution is not better, but accepted
                weight_score = 2
            current = copy.deepcopy(candidate)
            current_objective = copy.deepcopy(candidate_objective)
            current_infeasible_set = copy.deepcopy(candidate_infeasible_set)
        else:
            # Solution is rejected
            weight_score = 3

        if candidate_objective <= best_objective:
            # Solution is new global best
            current = copy.deepcopy(candidate)
            current_objective = copy.deepcopy(candidate_objective)
            current_infeasible_set = copy.deepcopy(candidate_infeasible_set)
            best = copy.deepcopy(candidate)
            best_objective = copy.deepcopy(candidate_objective)
            best_infeasible_set = copy.deepcopy(candidate_infeasible_set)
            weight_score = 0

        return best, best_objective, best_infeasible_set, current, current_objective, current_infeasible_set, weight_score
