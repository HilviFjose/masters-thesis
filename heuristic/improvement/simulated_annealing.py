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

        # Always accept better solution
        # TODO: Legge inn en ny objektivvurdering. Må iterere oss gjennom flere objektiver. 
        if checkCandidateBetterThanCurrent(candidateObj= candidate_objective, currObj= current_objective):
            #print("Found better solution")
            accept = True

        # Sometimes accept worse
        else:
            #print("Did not find better solution")
            # TODO: Legge inn en ny objektivvurdering
            diff = (candidate_objective.total_seconds() -
                    current_objective.total_seconds())/60
            probability = np.exp(-diff / self.temperature)
            #print("Probability ", probability)
            accept = (probability >= random_state.random())
            #print("Did we still go with worse solution: ", accept)

        # Should not set a temperature that is lower than the end temperature.
        self.temperature = self.temperature*self.cooling_rate

        return accept