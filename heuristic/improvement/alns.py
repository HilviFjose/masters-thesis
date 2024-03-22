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
        
        self.current_route_plan = current_route_plan
        self.best_route_plan = copy.deepcopy(current_route_plan)
        
        
        self.iterationNum = 0 
        

    def iterate(self, num_iterations):
        weights = np.asarray(self.weights, dtype=np.float16)
        current_route_plan = copy.deepcopy(self.route_plan)
        current_objective = copy.deepcopy(self.objective)
        best_route_plan = copy.deepcopy(self.route_plan)
        best_objective = copy.deepcopy(self.objective)
        found_solutions = {}

        # TODO: Usikker på om vi trenger dette
        #current_infeasible_set = copy.deepcopy(self.initial_infeasible_set)
        #best_infeasible_set = copy.deepcopy(self.initial_infeasible_set)
        
        
        # weights er vekter for å velge operator, score og count brukes for oppdatere weights
        d_weights = np.ones(len(self.destroy_operators), dtype=np.float16)
        r_weights = np.ones(len(self.repair_operators), dtype=np.float16)
        d_scores = np.ones(len(self.destroy_operators), dtype=np.float16)
        r_scores = np.ones(len(self.repair_operators), dtype=np.float16)
        # Kan ikke count bare være at vi hver 10 iterasjon eller noe oppdaterer?
        d_count = np.zeros(len(self.destroy_operators), dtype=np.float16)
        r_count = np.zeros(len(self.repair_operators), dtype=np.float16)

        for i in tqdm(range(num_iterations), colour='#39ff14'):
            print('Allocated patients before destroy',len(current_route_plan.allocatedPatients.keys()))
            print('First objective before destroy', current_route_plan.objective[0])

            self.iterationNum += 1

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
            
            if not destroyed:
                break

            d_count[destroy] += 1

            print('-----------------------------------------')
            print('Destroy operator: ', d_operator.__name__)
            print('Allocated patients after destroy',len(destroyed_route_plan.allocatedPatients.keys()))
            destroyed_route_plan.updateObjective()
            print('First objective after destroy',destroyed_route_plan.objective[0])


            # Repair solution
            r_operator = self.repair_operators[repair]
            candidate_route_plan = r_operator(
                destroyed_route_plan)
            
            r_count[repair] += 1

            print('-----------------------------------------')
            print('Repair operator: ', r_operator.__name__)
            print('Allocated patients after repair',len(candidate_route_plan.allocatedPatients.keys()))
            print('Infeasible treat after repair',len(candidate_route_plan.illegalNotAllocatedTreatments))
            print('Infeasible visits after repair',candidate_route_plan.illegalNotAllocatedVisitsWithPossibleDays.keys())
            print('Infeasible act after repair',candidate_route_plan.illegalNotAllocatedActivitiesWithPossibleDays.keys())
            print('First objective after repair',candidate_route_plan.objective[0])
             

            candidate_route_plan.printDictionaryTest("candidate"+str(self.iterationNum)+"dict1")

            # Local search if solution is promising
            local_search_requirement = 0.02 # TODO: Legge inn i main config
        
            if isPromisingLS(candidate_route_plan.objective, self.best_route_plan.objective, local_search_requirement) == True: 
                print("kommer hit")
                localsearch = LocalSearch(candidate_route_plan)
                candidate_route_plan = localsearch.do_local_search()
                candidate_route_plan.printSolution("candidate"+str(self.iterationNum))
            
            candidate_route_plan.printDictionaryTest("candidate"+str(self.iterationNum)+"dict2")

                #Har funnet en kandidat som er god nok til å bli current, så setter den til den 
                #self.current_route_plan = copy.deepcopy(candidate_route_plan)
                #self.current_objective = copy.deepcopy(candidate_route_plan.objective)
        
            # Konverterer til hexa-string for å sjekke om vi har samme løsning. Evaluerer og scores oppdateres kun hvis vi har en løsning som ikke er funnet før
            if hash(str(candidate_route_plan)) == hash(str(current_route_plan)) and hash(str(candidate_route_plan)) in found_solutions.keys():
                already_found = True
            else:
                found_solutions[hash(str(current_route_plan))] = 1

            if not already_found:
                # Compare solutions
                best_route_plan, best_objective, current_route_plan, current_objective, weight_score = self.evaluate_candidate(
                    best_route_plan, best_objective, current_route_plan, current_objective, candidate_route_plan, candidate_route_plan.objective, self.criterion)
                # Update scores
                d_scores[destroy] += weight_score
                r_scores[repair] += weight_score
           

            # After a certain number of iterations, update weight
            if (i+1) % iterations == 0:
                # Update weights with scores
                for destroy in range(len(d_weights)):
                    d_weights[destroy] = d_weights[destroy] * \
                        (1 - self.reaction_factor) + \
                        (self.reaction_factor *
                         d_scores[destroy] / d_count[destroy])
                    print("d_count destroy", d_count[destroy])
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
          
        return best_route_plan
    
    def set_operators(self, operators):
        # Add destroy operators
     
        self.add_destroy_operator(operators.random_patient_removal)
        self.add_destroy_operator(operators.random_treatment_removal)
        self.add_destroy_operator(operators.random_visit_removal)
        self.add_destroy_operator(operators.random_activity_removal)
        
        self.add_destroy_operator(operators.worst_deviation_patient_removal)
        self.add_destroy_operator(operators.worst_deviation_treatment_removal)
        #self.add_destroy_operator(operators.worst_deviation_visit_removal)
        self.add_destroy_operator(operators.worst_deviation_activity_removal)

        self.add_destroy_operator(operators.cluster_distance_patients_removal)
        self.add_destroy_operator(operators.cluster_distance_activities_removal)

        self.add_destroy_operator(operators.spread_distance_patients_removal)
        self.add_destroy_operator(operators.spread_distance_activities_removal)

        self.add_destroy_operator(operators.random_pattern_removal)
        
        # Add repair operators
        self.add_repair_operator(operators.greedy_repair)
        self.add_repair_operator(operators.random_repair)
        self.add_repair_operator(operators.complexity_repair)

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
    def evaluate_candidate(self, best_route_plan, best_objective, current_route_plan, current_objective, 
                           candidate_route_plan, candidate_objective, criterion):
        # If solution is accepted by criterion (simulated annealing)
        if criterion.accept_criterion(self.rnd_state, current_objective, candidate_objective):
            # TODO: Endre objektivvurdering
            if checkCandidateBetterThanBest(candidateObj= candidate_objective, currObj= current_objective):
                # Solution is better
                # TODO: Legge inn som sigma123 i main_config i stedet. 
                weight_score = 1
            else:
                # Solution is not better, but accepted
                weight_score = 2

            current_route_plan = copy.deepcopy(candidate_route_plan)
            current_objective = copy.deepcopy(candidate_objective)
        else:
            # Solution is rejected
            weight_score = 3


        # Sjekker om candidate har bedre objektiv enn best, returnerer False hvis best er bedre
        if checkCandidateBetterThanBest(candidateObj = candidate_objective, currObj = best_objective):
            # Solution is new global best
            print("ALNS iteration ", self.iterationNum, " is new global best")
            current_route_plan = copy.deepcopy(candidate_route_plan)
            current_objective = copy.deepcopy(candidate_objective)
            best_route_plan = copy.deepcopy(candidate_route_plan)
            best_objective = copy.deepcopy(candidate_objective)
            weight_score = 0

        return best_route_plan, best_objective, current_route_plan, current_objective, weight_score
