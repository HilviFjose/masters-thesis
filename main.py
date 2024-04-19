import pandas as pd
import numpy.random as rnd
import os
import sys

import parameters
from config.main_config import *
from heuristic.construction.construction import ConstructionHeuristic
from heuristic.improvement.simulated_annealing import SimulatedAnnealing
from heuristic.improvement.alns import ALNS
from heuristic.improvement.operator.destroy_operators import DestroyOperators
from heuristic.improvement.operator.repair_operators import RepairOperators
from heuristic.improvement.local_search import LocalSearch

import cProfile
import pstats
from pstats import SortKey
from datetime import datetime
import contextlib
import io


def main():
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
    
    constructor.route_plan.updateObjective(1, iterations)  #Egentlig iterasjon 0, men da blir det ingen penalty
    constructor.route_plan.printSolution("initial", "ingen operator")
    
    initial_route_plan = constructor.route_plan 
    print('Allocated patients in initial solution',len(constructor.route_plan.allocatedPatients.keys()))
    print('First objective in initial solution',constructor.route_plan.objective)
    if constructor.route_plan.objective[0] != constructor.route_plan.getOriginalObjective():
        print(f" Construction: Penalty in first objective: {constructor.route_plan.getOriginalObjective() - constructor.route_plan.objective[0]}. Original Objective: {constructor.route_plan.getOriginalObjective()}, Updated Objective: {constructor.route_plan.objective[0]} ")
        

    #IMPROVEMENT OF INITAL SOLUTION 
    #Parameterne er hentet fra config. 
    criterion = SimulatedAnnealing(start_temperature, end_temperature, cooling_rate)



    localsearch = LocalSearch(initial_route_plan, 1, iterations) #Egentlig iterasjon 0, men da blir det ingen penalty
    initial_route_plan = localsearch.do_local_search()
    initial_route_plan.updateObjective(1, iterations) #Egentlig iterasjon 0, men da blir det ingen penalty
    initial_route_plan.printSolution("candidate_after_initial_local_search", "ingen operator")
   
    alns = ALNS(weight_scores, reaction_factor, initial_route_plan, criterion, destruction_degree, constructor, rnd_state=rnd.RandomState())

    destroy_operators = DestroyOperators(alns)
    repair_operators = RepairOperators(alns)

    alns.set_operators(destroy_operators, repair_operators)

    #RUN ALNS 
    best_route_plan = alns.iterate(iterations)
    
    best_route_plan.updateObjective(iterations, iterations)
    best_route_plan.printSolution("final", "no operator")
         
if __name__ == "__main__":
    main()
    """
    # Kjøre main og printe til profiler
    directory = "profilerResults"s
    os.makedirs(directory, exist_ok=True)
    filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".txt"
    filepath = os.path.join(directory, filename)

    # Profile your entire program and save the data to 'program_profile'
    cProfile.run('main()', 'program_profile')

    # Load and analyze profile data, focusing on cumulative time spent
    p = pstats.Stats('program_profile')
    p.strip_dirs().sort_stats(SortKey.CUMULATIVE)

    # Manually capture the output of print_stats()
    output = io.StringIO()
    p.print_stats(output)
    stats = output.getvalue()
    output.close()

    # Write the captured stats to the file
    with open(filepath, 'w') as f:
        f.write(stats)

    print(f"Profiler results have been written to {filepath}")
    """