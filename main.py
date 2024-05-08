import pandas as pd
import numpy.random as rnd
import os
import sys
from datetime import datetime

import parameters
from config.main_config import *
from heuristic.construction.construction import ConstructionHeuristic
from heuristic.improvement.simulated_annealing import SimulatedAnnealing
from heuristic.improvement.alns import ALNS
from heuristic.improvement.operator.destroy_operators import DestroyOperators
from heuristic.improvement.operator.repair_operators import RepairOperators
from heuristic.improvement.local_search import LocalSearch
from multipro import setup, process_parallel

import cProfile
import pstats
from pstats import SortKey

def main():
    #TODO: Burde legge til sånn try og accept kriterier her når vi er ferdig. Men Bruker ikke det enda fordi letter å jobbe uten

    mp_config = setup(3,2,3)

    #INPUT DATA
    employees_container = parameters.employees_information_array
    patients_container = parameters.patients_information_array
    treatments_container = parameters.treatments_information_array
    visits_container = parameters.visits_information_array
    activities_container = parameters.activities_information_array

    # Specify the parent folder
    parent_folder = "results"

    # Create a folder with current date and time inside the parent folder
    current_datetime = datetime.now()
    date_time_str = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    folder_name = f"{parent_folder}-{date_time_str}"

    folder_path = os.path.join(parent_folder, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    #CONSTRUCTION HEURISTIC
    constructor = ConstructionHeuristic(activities_container, employees_container, patients_container, treatments_container, visits_container, 5, folder_name)
    print("Constructing Initial Solution")
    '''
    #CONSTRUCTION HEURISTIC NORMA
    constructor.construct_initial()
    '''

    #PARALELL CONSTUCTION 
    constructor.route_plans = process_parallel(constructor.construct_simple_initial, function_kwargs={} , jobs=[a for a in range(num_of_constructions)], mp_config= mp_config, paralellNum=num_of_constructions)
    constructor.setBestRoutePlan()
    
    
    constructor.route_plan.updateObjective(1, iterations)  #Egentlig iterasjon 0, men da blir det ingen penalty
    constructor.route_plan.printSolution("initial", "ingen operator")

    initial_route_plan = constructor.route_plan 
    print('Allocated patients in initial solution',len(constructor.route_plan.allocatedPatients.keys()))
    print('First objective in initial solution',constructor.route_plan.objective)
    if constructor.route_plan.objective[0] != constructor.route_plan.getOriginalObjective():
        print(f" Construction: Penalty in first objective: {constructor.route_plan.getOriginalObjective() - constructor.route_plan.objective[0]}. Original Objective: {constructor.route_plan.getOriginalObjective()}, Updated Objective: {constructor.route_plan.objective[0]} ")
        

    #IMPROVEMENT OF INITAL SOLUTION 
    #Parameterne er hentet fra config. 
    #criterion = SimulatedAnnealing(start_temperature, end_temperature, cooling_rate)
    criterion = SimulatedAnnealing(sim_annealing_diff, prob_of_choosing, rate_T_start_end)

    #TODO: Gjøre parellelt lokalsøk på denne også 
    localsearch = LocalSearch(initial_route_plan, 1, iterations) #Egentlig iterasjon 0, men da blir det ingen penalty
    initial_route_plan = localsearch.do_local_search()
    initial_route_plan.updateObjective(1, iterations) #Egentlig iterasjon 0, men da blir det ingen penalty
    initial_route_plan.printSolution("candidate_after_initial_local_search", "ingen operator")
   
    alns = ALNS(weight_scores, reaction_factor, initial_route_plan, criterion,  constructor, mp_config)

    

   

    #RUN ALNS 
    best_route_plan = alns.iterate(iterations)
    
    best_route_plan.updateObjective(iterations, iterations)
    best_route_plan.printSolution("final", "no operator")
         
if __name__ == "__main__":
    main()
    """
    # Profiler hele programmet ditt
    cProfile.run('main()', 'program_profile')

    # Last inn og analyser profildata, fokusert på dine funksjoner
    p = pstats.Stats('program_profile')
    p.strip_dirs().sort_stats(SortKey.TIME).print_stats()
    

    """ 