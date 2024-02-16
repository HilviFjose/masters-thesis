import numpy.random as rnd 
import numpy as np 
import copy
from tqdm import tqdm 

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
        self.construcor = constructor
        #TODO: Finne ut om vi skal ha denn klassen med. Eller om det har noe med ALNS å gjøre
        #self.destroy_repair_updater = Destroy_Repair_Updater(constructor)

    
    def iterate(self, num_iterations,  index_removed, delayed):
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

        #destroy operators vil være tom når denne lages? 
        d_weights = np.ones(len(self.destroy_operators), dtype=np.float16)
        r_weights = np.ones(len(self.repair_operators), dtype=np.float16)
        d_scores = np.ones(len(self.destroy_operators), dtype=np.float16)
        r_scores = np.ones(len(self.repair_operators), dtype=np.float16)
        d_count = np.zeros(len(self.destroy_operators), dtype=np.float16)
        r_count = np.zeros(len(self.repair_operators), dtype=np.float16)


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
            #henter ut d_operator objekt fra index i destroy perator lister
            #Har en liste over funskjoner og henter ut en av de og kaller denne funskjoenen d_operator 
            #deretter kalles denne ufnskjoenen med de gitte parameterne 
            d_operator = self.destroy_operators[destroy]
            destroyed_route_plan, removed_requests, index_removed, destroyed = d_operator(
                current_route_plan, current_infeasible_set)
            
            if not destroyed:
                break

            d_count[destroy] += 1

          
    # Select destroy/repair operator
    @staticmethod
    def select_operator(operators, weights, rnd_state):
        w = weights / np.sum(weights)
        a = [i for i in range(len(operators))]
        return rnd_state.choice(a=a, p=w)
