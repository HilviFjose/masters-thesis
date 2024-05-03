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
from functools import partial

import optuna
print(optuna.__version__)

def main():
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
    
    iterations = num_iterations
    #CONSTRUCTION HEURISTIC
    constructor = ConstructionHeuristic(df_activities, df_employees, df_patients, df_treatments, df_visits, 5, folder_name)
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
   
    alns = setup_alns(weight_score_better_default, weight_score_accepted_default, weight_score_bad, weight_score_best_default, reaction_factor_default, 
                      local_search_req_default, iterations_update_default, initial_route_plan, criterion, constructor, rnd_state=rnd.RandomState()) 

    destroy_operators = DestroyOperators(alns)
    repair_operators = RepairOperators(alns)

    alns.set_operators(destroy_operators, repair_operators)

    #RUN ALNS 
    best_route_plan = run_alns(alns)
    
    best_route_plan.updateObjective(iterations, iterations)
    best_route_plan.printSolution("final", "no operator")

    objective_func = partial(objective, initial_route_plan, criterion, constructor)

    #Run optuna
    study = optuna.create_study(direction='maximize')
    study.optimize(objective_func, n_trials=50)
    print("Best parameters:", study.best_trial.params)
   

def setup_alns(weight_score_better, weight_score_accepted, weight_score_bad, weight_score_best, reaction_factor, local_search_req, 
                iteration_update, current_route_plan, criterion, constructor, rnd_state):
    # Configuration code here
    alns = ALNS(weight_score_better, weight_score_accepted, weight_score_bad, weight_score_best, reaction_factor, local_search_req, 
                iteration_update, current_route_plan, criterion, constructor, rnd_state)
    return alns

def run_alns(alns, iterations):
    # Execute the ALNS process
    best_route_plan = alns.iterate(iterations)
    return best_route_plan

def objective(route_plan, criterion, constructor, trial):
    # Suggesting parameters
    reaction_factor = trial.suggest_float('reaction_factor', 0.4, 0.8, step=0.1)
    local_search_req = trial.suggest_float('local_search_req', 0.01, 0.05, step=0.01)
    weight_score_best = trial.suggest_int('weight_score_best', 10, 15)
    weight_score_better = trial.suggest_int('weight_score_better', 1, 5, 10)
    weight_score_accepted = trial.suggest_int('weight_score_accepted', 1, 5, 10)
    iterations_update = trial.suggest_float('iterations_update', 0.1, 0.5, step=0.1)

    # Configure and run ALNS
    alns = setup_alns(weight_score_better, weight_score_accepted, weight_score_bad, weight_score_best, reaction_factor, local_search_req, 
                iterations_update, route_plan, criterion, constructor, rnd_state=rnd.RandomState())
    result = run_alns(alns, iterations = 10) 

    return result.objective_score  # Objective to minimize
         
if __name__ == "__main__":
    main()