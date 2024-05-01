import numpy as np
from helpfunctions import *

class SimulatedAnnealing:
    def __init__(self, start_temperature, end_temperature, cooling_rate):
        self.start_temperature = start_temperature
        self.end_temperature = end_temperature
        self.cooling_rate = cooling_rate
        self.temperature = start_temperature

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
                diff = current_objective[0] - candidate_objective[0] 
                print("diff for objektiv 0", diff)
                probability = np.exp(-diff / self.temperature)
                accept = (probability >= random_state.random())
                print("Candidate not better. Accepted det solution?", accept)
            else:
                for i in range(1, len(candidate_objective)): 
                    if candidate_objective[i] > current_objective[i]: 
                        diff = candidate_objective[i] - current_objective[i]
                        print("diff for objektiv",i, diff)
                        probability = np.exp(-diff / self.temperature)
                        accept = (probability >= random_state.random())
                        print("Candidate not better. Accepted det solution?", accept)
                        break
        
        # Should not set a temperature that is lower than the end temperature.
        self.temperature = self.temperature * self.cooling_rate
        return accept