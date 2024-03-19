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
        #print("Found better solution")
        if checkCandidateBetterThanBest(candidateObj= candidate_objective, currObj= current_objective):
            accept = True
        
        # Sometimes accept worse
        else:
            #print("Did not find better solution")
            # Håndterer første objektiv separat fordi det er maksimering
            if candidate_objective[0] < current_objective[0]:
                diff = current_objective[0] - candidate_objective[0] 
                probability = np.exp(-diff / self.temperature)
                print("Cooling on first objective")
                print("Diff", diff, "Probability ", probability)
                accept = (probability >= random_state.random())
                print("Accepted det solution?", accept)
            for i in range(1, len(candidate_objective)): 
                if candidate_objective[i] > current_objective[i]: 
                    diff = candidate_objective[i] - current_objective[i]
                    probability = np.exp(-diff / self.temperature)
                    print("Cooling on objective", i)
                    print("Diff", diff, "Probability ", probability)
                    accept = (probability >= random_state.random())
                    print("Accepted det solution?", accept)
                    break
        # Should not set a temperature that is lower than the end temperature.
        self.temperature = self.temperature * self.cooling_rate
        return accept
    