import numpy as np
from helpfunctions import *
import numpy.random as rnd
import math
#from config.main_config import iterations

class SimulatedAnnealing:
    def __init__(self, deviation_from_best, prob_of_choosing, rate_T_start_end, iterations):
    #def __init__(self, sim_annealing_diff, prob_of_choosing, rate_T_start_end):
        
        self.cooling_rate = (rate_T_start_end)**(1/iterations)
        self.start_temperature = math.log(prob_of_choosing)/deviation_from_best
        self.end_temperature = self.start_temperature*rate_T_start_end
        self.temperature = self.start_temperature

        
    # Simulated annealing acceptance criterion
    def accept_criterion(self, current_objective, candidate_objective):
        accept = False
        # Always accept better solution
        if checkCandidateBetterThanBest(candidate_objective, current_objective):
            accept = True
            #print("Candidate is better than current and accepted")
        
        # Sometimes accept worse

            '''
            Vet at hvis første objektiv er bedre, så vil vi returnere True 
            Så når vi er her så vet vi at kandiat er dårligere eller like god som current
            '''
        #TODO: Finne ut om vi skal ha current eller best under her. Kan sjekke i KP og de sin 
        else:
            if candidate_objective[0] < current_objective[0]:
                deviation_diff = (candidate_objective[0] - current_objective[0])/current_objective[0]
                probability = np.exp(-deviation_diff * self.temperature)
                accept = (probability >= rnd.random())
                #print("Candidate not better. Accepted det solution?", accept)
            else:

                #Nå vet vi at første objektivet er likt som det første, vil da evaluere på de neste objektivene? 
                #Vi vet at dette objektivet ikke er bedre enn de neste, for da ville den slått ut
                #Vi vil hoppe ned helt til vi finner der hvor den ikke fungerer lenger. 
                for i in range(1, len(candidate_objective)): 
                    if candidate_objective[i] > current_objective[i]: 
                        diff = (candidate_objective[i] - current_objective[i])/current_objective[i]
                        probability = np.exp(-diff * self.temperature)
                        accept = (probability >= rnd.random())
                        #print("Candidate not better. Accepted det solution?", accept)
                        break
    
        # Should not set a temperature that is lower than the end temperature.
        self.temperature = self.temperature * self.cooling_rate
        return accept