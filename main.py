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
from functools import partial

import optuna

def main():
    #TODO: Burde legge til sånn try og accept kriterier her når vi er ferdig. Men Bruker ikke det enda fordi letter å jobbe uten

    mp_config = setup(3,2,3)

    #INPUT DATA
    df_employees = parameters.df_employees
    df_patients = parameters.df_patients
    df_treatments = parameters.df_treatments
    df_visits = parameters.df_visits
    df_activities = parameters.df_activities

    # CREATE RESULTS FOLDER
    current_datetime = datetime.now()
    date_time_str = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    folder_name = f"results-{date_time_str}"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    
    constructor = ConstructionHeuristic(df_activities, df_employees, df_patients, df_treatments, df_visits, 5, folder_name)
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
   
    alns = ALNS(weight_score_better_default, weight_score_accepted_default, weight_score_bad, weight_score_best_default, reaction_factor_default, 
                      local_search_req_default, iterations_update_default, initial_route_plan, criterion, constructor) 


    #RUN ALNS 
    best_route_plan = alns.iterate(iterations)
    best_route_plan.updateObjective(iterations, iterations) #Nå lages det ikke noen ruteplan her?
    
    """
    objective_func = partial(objective, initial_route_plan, criterion, constructor)

    #Run optuna
    study = optuna.create_study(direction='maximize')
    study.optimize(objective_func, n_trials=50)
    print("Best parameters:", study.best_trial.params)
    """

def objective(route_plan, criterion, constructor, trial):
    # Suggesting parameters
    reaction_factor_interval = trial.suggest_float('reaction_factor', 0.4, 0.8, step=0.1)
    local_search_req_interval = trial.suggest_float('local_search_req', 0.01, 0.05, step=0.01)
    weight_score_best_interval = trial.suggest_int('weight_score_best', 10, 15,  step=1)
    weight_score_better_interval = trial.suggest_int('weight_score_better', 1, 10, step=1)
    weight_score_accepted_interval = trial.suggest_int('weight_score_accepted', 1, 10, step=1)
    iterations_update_interval = trial.suggest_float('iterations_update', 0.1, 0.5, step=0.1)

    # Configure and run ALNS
    alns = ALNS(weight_score_better_interval, weight_score_accepted_interval, weight_score_bad, weight_score_best_interval, reaction_factor_interval, local_search_req_interval, 
                iterations_update_interval, route_plan, criterion, constructor)
    result = alns.iterate(iterations)

    return result.objective_score  # Objective to minimize
            
if __name__ == "__main__":
    main()
    """
    # Profiler hele programmet ditt
    cProfile.run('main()', 'program_profile')

    # Last inn og analyser profildata, fokusert på dine funksjoner
    p = pstats.Stats('program_profile')
    p.strip_dirs().sort_stats(SortKey.TIME).print_stats()
    

    """ 