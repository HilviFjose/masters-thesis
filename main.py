import pandas as pd
import numpy.random as rnd
import os
import sys

from heuristic.construction.construction import ConstructionHeuristic
from config.main_config import *
from heuristic.improvement.simulated_annealing import SimulatedAnnealing
from heuristic.improvement.alns import ALNS
from heuristic.improvement.operator.operators import Operators
from datageneration import employeeGeneration
from datageneration import patientGeneration 
from datageneration import distance_matrix

import parameters

def main():
    #SKRIV TIL FIL I STEDET FOR TERMINAL
    # Åpne filen for å skrive
    with open("results.txt", "w") as log_file:
        # Omdiriger sys.stdout til filen
        original_stdout = sys.stdout
        sys.stdout = log_file
        constructor = None

        #TODO: Burde legge til sånn try og accept kriterier her når vi er ferdig. Men Bruker ikke det enda fordi letter å jobbe uten

        #INPUT DATA
        df_employees = parameters.df_employees
        df_patients = parameters.df_patients
        df_treatments = parameters.df_treatments
        df_visits = parameters.df_visits
        df_activities = parameters.df_activities

        #CONSTRUCTION HEURISTIC
        constructor = ConstructionHeuristic(df_activities, df_employees, df_patients, df_treatments, df_visits, 5)
        print("Constructing Initial Solution")
        constructor.construct_initial()
        
        constructor.route_plan.printSolution()
       

        initial_objective = constructor.route_plan.objective
        initial_route_plan = constructor.route_plan 
        initial_infeasible_set = constructor.unAssignedPatients #Usikker på om dette blir riktig. TODO: Finn ut mer om hva infeasible_set er.

        '''    
        #IMPROVEMENT OF INITAL SOLUTION 
        #Parameterne er hentet fra config. 
        
        criterion = SimulatedAnnealing(start_temperature, end_temperature, cooling_rate)

        alns = ALNS(weights, reaction_factor, initial_route_plan, initial_objective, initial_infeasible_set, criterion,
                        destruction_degree, constructor, rnd_state=rnd.RandomState())


        operators = Operators(alns)

        alns.set_operators(operators)

        #RUN ALNS 
        best_route_plan = alns.iterate(
                iterations)
        
        print("LØSNING ETTER ALNS")
        best_route_plan.printSolution()
    
        '''
        '''
        constructor.print_new_objective(current_route_plan, current_infeasible_set)
        '''
        
        # Tilbakestill sys.stdout til original
        sys.stdout = original_stdout


if __name__ == "__main__":
    main()
