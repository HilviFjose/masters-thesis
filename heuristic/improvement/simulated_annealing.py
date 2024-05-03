import numpy as np
from helpfunctions import *
import math
from config.main_config import iterations

class SimulatedAnnealing:
    def __init__(self, sim_annealing_diff, prob_of_choosing, rate_T_start_end):

        self.start_temperature = -sim_annealing_diff/math.log(prob_of_choosing)
        self.end_temperature = self.start_temperature*rate_T_start_end
        self.cooling_rate = (self.end_temperature/self.start_temperature)**(1/iterations)
        self.temperature = self.start_temperature

        print("self.start_temperature", self.start_temperature)
        print("self.end_temperature", self.end_temperature)
        print("self.cooling_rate", self.cooling_rate)
        
        '''
        self.start_temperature = start_temperature
        self.end_temperature = end_temperature
        self.cooling_rate = cooling_rate
        self.temperature = start_temperature
        '''
        
    # Simulated annealing acceptance criterion
    def accept_criterion(self, random_state, current_objective, candidate_objective):
        accept = False
        # Always accept better solution
        if checkCandidateBetterThanBest(candidate_objective, current_objective):
            accept = True
            print("Candidate is better than current and accepted")
        
        # Sometimes accept worse
        else:
            if candidate_objective[0] < current_objective[0]:
                diff = (candidate_objective[0] - current_objective[0])/current_objective[0]
                probability = np.exp(-diff / self.temperature)
                accept = (probability >= random_state.random())
                print("Candidate not better. Accepted det solution?", accept)
            else:
                for i in range(1, len(candidate_objective)): 
                    if candidate_objective[i] > current_objective[i]: 
                        diff = (candidate_objective[i] - current_objective[i])/current_objective[i]
                        probability = np.exp(-diff / self.temperature)
                        accept = (probability >= random_state.random())
                        print("Candidate not better. Accepted det solution?", accept)
                        break
    
        # Should not set a temperature that is lower than the end temperature.
        self.temperature = self.temperature * self.cooling_rate
        return accept