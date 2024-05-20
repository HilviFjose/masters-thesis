import pandas as pd
#import numpy.random as rnd
import os
#import sys
from datetime import datetime
import time

import parameters
from config.main_config import *
from heuristic.construction.construction import ConstructionHeuristic
from heuristic.improvement.simulated_annealing import SimulatedAnnealing
from heuristic.improvement.alns import ALNS
#from heuristic.improvement.operator.destroy_operators import DestroyOperators
#from heuristic.improvement.operator.repair_operators import RepairOperators
from heuristic.improvement.local_search import LocalSearch
from multipro import setup, process_parallel

#import cProfile
#import pstats
#from pstats import SortKey
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
   
    # Specify the parent folder
    parent_folder = "results"

    # Create a folder with current date and time inside the parent folder
    current_datetime = datetime.now()
    date_time_str = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    folder_name = f"{parent_folder}-{date_time_str}"

    folder_path = os.path.join(parent_folder, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    config_info_file_path = os.path.join(folder_path, "0config_info" + ".txt")

    

    with open("config/main_config.py", 'r') as file:
        content = file.read()

    with open(config_info_file_path, 'w') as file:
        file.write("TIDSPUNKT FOR KJORING "+date_time_str)
        file.write(content)
        
     
    constructor = ConstructionHeuristic(df_activities, df_employees, df_patients, df_treatments, df_visits, 5, folder_name)
    #print("Constructing Initial Solution")
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
    #print('Allocated patients in initial solution',len(constructor.route_plan.allocatedPatients.keys()))
    #print('First objective in initial solution',constructor.route_plan.objective)
    #if constructor.route_plan.objective[0] != constructor.route_plan.getOriginalObjective():
        #print(f" Construction: Penalty in first objective: {constructor.route_plan.getOriginalObjective() - constructor.route_plan.objective[0]}. Original Objective: {constructor.route_plan.getOriginalObjective()}, Updated Objective: {constructor.route_plan.objective[0]} ")
        

    #IMPROVEMENT OF INITAL SOLUTION 
    #Parameterne er hentet fra config. 
    #criterion = SimulatedAnnealing(start_temperature, end_temperature, cooling_rate)
    

    #TODO: Gjøre parellelt lokalsøk på denne også 
    localsearch = LocalSearch(initial_route_plan, 1, iterations) #Egentlig iterasjon 0, men da blir det ingen penalty
    initial_route_plan = localsearch.do_local_search()
    initial_route_plan.updateObjective(1, iterations) #Egentlig iterasjon 0, men da blir det ingen penalty
    #initial_route_plan.printSolution("candidate_after_initial_local_search", "ingen operator")
    criterion = SimulatedAnnealing(deviation_from_best, prob_of_choosing, rate_T_start_end)
    
    alns = ALNS([destruction_degree_low_default, destruction_degree_high_default], weight_score_better_default, weight_score_accepted_default, weight_score_bad, weight_score_best_default, reaction_factor_default, 
                      local_search_req_default, iterations_update_default, initial_route_plan, criterion, constructor, mp_config, folder_path) 
    criterion.setALNS(alns)
    #RUN ALNS 
    best_route_plan = alns.iterate(iterations)
    best_route_plan.updateObjective(iterations, iterations)
    best_route_plan.printSolution("final", "no operator")


    '''

    #RUN OPTUNA
    #DESTRUCTION DEGREE
    search_space = {'destruction_degree': [(0.05, 0.15), (0.05, 0.30), (0.15, 0.30), (0.15, 0.5), (0.3, 0.5)]}
    sampler = optuna.samplers.GridSampler(search_space)
    study_destruction_degree = optuna.create_study(directions=['maximize', 'minimize', 'minimize', 'minimize'], sampler=sampler)
    #study_destruction_degree = optuna.create_study(directions=['maximize', 'minimize', 'minimize', 'minimize'])
    objective_func = partial(objective_destruction_degree, route_plan=initial_route_plan, criterion=criterion, constructor=constructor, mp_config=mp_config, folder_path=folder_path)
    study_destruction_degree.optimize(objective_func)
    #study_destruction_degree.optimize(objective_func, n_trials=5)
    
    write_trials_to_csv(study_destruction_degree, folder_name, 'destruction_degree')
    best_trial_destruction_degree = find_best_trial_lexicographically(study_destruction_degree) 
    destruction_degree_tuned = best_trial_destruction_degree.params['destruction_degree']
    destruction_degree_low_tuned, destruction_degree_high_tuned = destruction_degree_tuned
    print("DESTRUCTION DEGREE - Number of finished trials: ", len(study_destruction_degree.trials))
    print('destruction_degree_tuned', destruction_degree_tuned)

    #WEIGHT SCORES
    search_space = {'weight_scores': [(5, 10, 15), (5, 15, 25), (5, 15, 35)]}
    sampler = optuna.samplers.GridSampler(search_space)
    study_weight_scores = optuna.create_study(directions=['maximize', 'minimize', 'minimize', 'minimize'], sampler=sampler)
    objective_func = partial(objective_weight_scores, route_plan=initial_route_plan, criterion=criterion, constructor=constructor, mp_config=mp_config, folder_path=folder_path,
                             destruction_degree_low_tuned=destruction_degree_low_tuned, destruction_degree_high_tuned=destruction_degree_high_tuned)
    study_weight_scores.optimize(objective_func)    

    write_trials_to_csv(study_weight_scores, folder_name, 'weight_scores')
    best_trial_weight_scores = find_best_trial_lexicographically(study_weight_scores)
    weight_score_best_tuned, weight_score_better_tuned, weight_score_accepted_tuned = best_trial_weight_scores.params['weight_scores']
    print(f'weight score best {weight_score_best_tuned}, better {weight_score_better_tuned}, accepted {weight_score_accepted_tuned}')
    
    #REACTION FACTOR AND NUMBER OF ITERATION FOR UPDATING WEIGHTS
    search_space = {'reaction_factor': [0.1, 0.25, 0.5, 0.75, 1]}
    sampler = optuna.samplers.GridSampler(search_space)
    study_reaction_factor = optuna.create_study(directions=['maximize', 'minimize', 'minimize', 'minimize'],sampler=sampler)
    objective_func = partial(objective_reaction_factor, route_plan=initial_route_plan, criterion=criterion, constructor=constructor, mp_config=mp_config, folder_path=folder_path,
                             destruction_degree_low_tuned=destruction_degree_low_tuned, destruction_degree_high_tuned=destruction_degree_high_tuned, 
                             weight_score_better_tuned=weight_score_better_tuned, weight_score_accepted_tuned=weight_score_accepted_tuned, weight_score_best_tuned=weight_score_best_tuned)
    study_reaction_factor.optimize(objective_func)

    write_trials_to_csv(study_reaction_factor, folder_name, 'reaction_factor')
    best_trial_reaction_factor = find_best_trial_lexicographically(study_reaction_factor)
    reaction_factor_tuned = best_trial_reaction_factor.params['reaction_factor']
    
    #NUMBER OF ITERATION FOR UPDATING WEIGHTS
    search_space = {'iterations_update': [0.01, 0.05, 0.1, 0.2, 0.35, 0.5]}
    sampler = optuna.samplers.GridSampler(search_space)
    study_iterations_update = optuna.create_study(directions=['maximize', 'minimize', 'minimize', 'minimize'],sampler=sampler)
    objective_func = partial(objective_iterations_update, route_plan=initial_route_plan, criterion=criterion, constructor=constructor, mp_config=mp_config, folder_path=folder_path,
                             destruction_degree_low_tuned=destruction_degree_low_tuned, destruction_degree_high_tuned=destruction_degree_high_tuned, 
                             weight_score_better_tuned=weight_score_better_tuned, weight_score_accepted_tuned=weight_score_accepted_tuned, weight_score_best_tuned=weight_score_best_tuned,
                             reaction_factor_tuned=reaction_factor_tuned)
    study_iterations_update.optimize(objective_func)

    write_trials_to_csv(study_iterations_update, folder_name, 'iterations_update')
    best_trial_iterations_update = find_best_trial_lexicographically(study_iterations_update)
    iterations_update_tuned = best_trial_iterations_update.params['iterations_update']
    
    #LOCAL SEARCH REQUIREMENT
    search_space = {'local_search_req': [0.01, 0.05, 0.1, 0.2]}
    sampler = optuna.samplers.GridSampler(search_space)
    study_local_search = optuna.create_study(directions=['maximize', 'minimize', 'minimize', 'minimize'], sampler=sampler)
    objective_func = partial(objective_local_search, route_plan=initial_route_plan, criterion=criterion, constructor=constructor, mp_config=mp_config, folder_path=folder_path,
                             destruction_degree_low_tuned=destruction_degree_low_tuned, destruction_degree_high_tuned=destruction_degree_high_tuned, 
                             weight_score_better_tuned=weight_score_better_tuned, weight_score_accepted_tuned=weight_score_accepted_tuned, weight_score_best_tuned=weight_score_best_tuned,
                             reaction_factor_tuned=reaction_factor_tuned, iterations_update_tuned=iterations_update_tuned)
    study_local_search.optimize(objective_func)

    write_trials_to_csv(study_local_search, folder_name, 'local_search')
    best_trial_local_search = find_best_trial_lexicographically(study_local_search)
    local_search_tuned = best_trial_local_search.params['local_search_req']

    print('-----------------------------')
    print('FINAL PARAMETERS AFTER TUNING')
    print('destruction_degree_tuned', destruction_degree_tuned)
    print(f'weight scores, best {weight_score_best_tuned}, better {weight_score_better_tuned}, accepted {weight_score_accepted_tuned}')
    print(f'reaction_factor {reaction_factor_tuned}') 
    print(f'iterations_update {iterations_update_tuned}')
    print(f'local_search_req {local_search_tuned}')
    '''

def objective_destruction_degree(trial, route_plan, criterion, constructor, mp_config, folder_path):
    start_time = time.time()  
    # Suggesting parameters
    destruction_degree_low, destruction_degree_high = trial.suggest_categorical('destruction_degree', [(0.05, 0.15), (0.05, 0.30), (0.15, 0.30), (0.15, 0.5), (0.3, 0.5)])

    # Configure and run ALNS
    alns = ALNS([destruction_degree_low, destruction_degree_high], weight_score_better_default, weight_score_accepted_default, weight_score_bad, weight_score_best_default,
                    reaction_factor_default, local_search_req_default, iterations_update_default, route_plan, criterion, constructor, mp_config, folder_path)
    route_plan = alns.iterate(iterations)

    end_time = time.time()
    duration = end_time - start_time
    trial.set_user_attr('duration', duration)

    return route_plan.objective

def objective_weight_scores(trial, route_plan, criterion, constructor, mp_config, folder_path, 
                                destruction_degree_low_tuned, destruction_degree_high_tuned):
    start_time = time.time()  
    # Suggesting parameters
    weight_score_best_interval, weight_score_better_interval, weight_score_accepted_interval = trial.suggest_categorical('weight_scores', [(5, 10, 15), (5, 15, 25), (5, 15, 35)])

    # Configure and run ALNS
    alns = ALNS([destruction_degree_low_tuned, destruction_degree_high_tuned], weight_score_better_interval, weight_score_accepted_interval, weight_score_bad, weight_score_best_interval,
                    reaction_factor_default, local_search_req_default, iterations_update_default, route_plan, criterion, constructor, mp_config, folder_path)
    route_plan = alns.iterate(iterations)

    end_time = time.time()
    duration = end_time - start_time
    trial.set_user_attr('duration', duration)

    return route_plan.objective

def objective_reaction_factor(trial, route_plan, criterion, constructor, mp_config, folder_path, 
              destruction_degree_low_tuned, destruction_degree_high_tuned, 
              weight_score_better_tuned, weight_score_accepted_tuned, weight_score_best_tuned):
    start_time = time.time()  
    # Suggesting parameters
    reaction_factor_interval = trial.suggest_categorical('reaction_factor', [0.1, 0.25, 0.5, 0.75, 1])

    # Configure and run ALNS
    alns = ALNS([destruction_degree_low_tuned, destruction_degree_high_tuned], weight_score_better_tuned, weight_score_accepted_tuned, weight_score_bad, weight_score_best_tuned,
                    reaction_factor_interval, local_search_req_default, iterations_update_default, route_plan, criterion, constructor, mp_config, folder_path)
    route_plan = alns.iterate(iterations)

    end_time = time.time()
    duration = end_time - start_time
    trial.set_user_attr('duration', duration)
    
    return route_plan.objective

def objective_iterations_update(trial, route_plan, criterion, constructor, mp_config, folder_path,
              destruction_degree_low_tuned, destruction_degree_high_tuned, 
              weight_score_better_tuned, weight_score_accepted_tuned, weight_score_best_tuned,
              reaction_factor_tuned):
    start_time = time.time()  
    # Suggesting parameters
    iterations_update_interval = trial.suggest_categorical('iterations_update', [0.01, 0.05, 0.1, 0.2, 0.35, 0.5])

    # Configure and run ALNS
    alns = ALNS([destruction_degree_low_tuned, destruction_degree_high_tuned], weight_score_better_tuned, weight_score_accepted_tuned, weight_score_bad, weight_score_best_tuned,
                    reaction_factor_tuned, local_search_req_default, iterations_update_interval, route_plan, criterion, constructor, mp_config, folder_path)
    route_plan = alns.iterate(iterations)

    end_time = time.time()
    duration = end_time - start_time
    trial.set_user_attr('duration', duration)
    
    return route_plan.objective

def objective_local_search(trial, route_plan, criterion, constructor, mp_config, folder_path, 
              destruction_degree_low_tuned, destruction_degree_high_tuned, 
              weight_score_better_tuned, weight_score_accepted_tuned, weight_score_best_tuned, 
              reaction_factor_tuned, iterations_update_tuned):
    start_time = time.time()  
    # Suggesting parameters
    local_search_req_interval = trial.suggest_categorical('local_search_req', [0.01, 0.05, 0.1, 0.2])

    # Configure and run ALNS
    alns = ALNS([destruction_degree_low_tuned, destruction_degree_high_tuned], weight_score_better_tuned, weight_score_accepted_tuned, weight_score_bad, weight_score_best_tuned,
                    reaction_factor_tuned, local_search_req_interval, iterations_update_tuned, route_plan, criterion, constructor, mp_config, folder_path)
    route_plan = alns.iterate(iterations)

    end_time = time.time()
    duration = end_time - start_time
    trial.set_user_attr('duration', duration)

    return route_plan.objective

def find_best_trial_lexicographically(study):
    best_trial = None
    found_better = False 

    def is_better(a, b):
        all_equal = True
        for i, direction in enumerate(study.directions):
            if direction == optuna.study.StudyDirection.MAXIMIZE:
                if a[i] > b[i]:
                    return True
                elif a[i] < b[i]:
                    all_equal = False
            else:  # MINIMIZE
                if a[i] < b[i]:
                    return True
                elif a[i] > b[i]:
                    all_equal = False
        return False 

    for trial in study.trials:
        if trial.state == optuna.trial.TrialState.COMPLETE:
            if best_trial is None or is_better(trial.values, best_trial.values):
                best_trial = trial
                found_better = True
    '''
    if best_trial and not found_better:
        print("Alle trials har like verdier.")
    else: 
        print('Best trial', best_trial.number)
    '''
    
    return best_trial    
        
'''def write_trials_to_csv(study, folder_name, tuning_parameters):
    # Ensure directory exists
    results_dir = os.path.join('results', folder_name, tuning_parameters)
    os.makedirs(results_dir, exist_ok=True)

    # Open the file for writing in the correct directory
    file_path = os.path.join(results_dir, "optuna_results.txt")

    # Collect data for DataFrame
    data = []
    for trial in study.trials:
        # Format parameters as string for display
        params_str = ', '.join([f"{k}: {v}" for k, v in trial.params.items()])
        row = {
            "Trial Number": trial.number,
            "First Objective": trial.values[0],
            "Second Objective": trial.values[1],
            "Third Objective": trial.values[2],
            "Fourth Objective": trial.values[3],
            "Parameters": params_str  # Add formatted parameters string
        }
        data.append(row)
        
    # Create DataFrame
    df = pd.DataFrame(data)
    df.sort_values(by=["First Objective", "Second Objective", "Third Objective", "Fourth Objective"], ascending=[False, True, True, True], inplace=True)
    csv_file_path = os.path.join(results_dir, "trials_data.csv")
    df.to_csv(csv_file_path, index=False)
    '''

def write_trials_to_csv(study, folder_name, tuning_parameters):
    # Ensure the results directory exists
    results_dir = os.path.join('results', folder_name, tuning_parameters)
    os.makedirs(results_dir, exist_ok=True)

    # Collect data for DataFrame
    data = []
    for trial in study.trials:
        # Format parameters as a string for display
        params_str = ', '.join([f"{k}: {v}" for k, v in trial.params.items()])
        duration_seconds = trial.user_attrs.get('duration', 0)  # Retrieve the duration from user attributes, default to 0 if not found
        duration_seconds = round(duration_seconds)
        
        # Convert duration to minutes and hours
        duration_minutes = round(duration_seconds / 60, 2)
        duration_hours = round(duration_seconds / 3600, 4)

        row = {
            "Trial Number": trial.number,
            "First Objective": trial.values[0] if trial.values else 'None',
            "Second Objective": trial.values[1] if len(trial.values) > 1 else 'None',
            "Third Objective": trial.values[2] if len(trial.values) > 2 else 'None',
            "Fourth Objective": trial.values[3] if len(trial.values) > 3 else 'None',
            "Parameters": params_str,
            "Duration (seconds)": duration_seconds,
            "Duration (minutes)": duration_minutes,
            "Duration (hours)": duration_hours
        }
        data.append(row)
        
    # Create DataFrame from collected data
    df = pd.DataFrame(data)
    df.sort_values(by=["First Objective", "Second Objective", "Third Objective", "Fourth Objective"], 
                   ascending=[False, True, True, True], inplace=True)
    csv_file_path = os.path.join(results_dir, "trials_data.csv")
    df.to_csv(csv_file_path, index=False)


def write_trials_to_file(study, folder_name, tuning_parameters):
    # Ensure directory exists
    results_dir = os.path.join('results', folder_name, tuning_parameters)
    os.makedirs(results_dir, exist_ok=True)

    # Open the file for writing in the correct directory
    file_path = os.path.join(results_dir, "optuna_results.txt")

    # Write best trial parameters to a file
    with open(file_path, "w") as f:
        for i, trial in enumerate(study.best_trials):
            now = datetime.now()
            f.write('Trial generated at time: {}\n\n'.format(now.strftime("%Y-%m-%d %H:%M:%S")))
            f.write(f"Trial {i}:\n")
            f.write(f"  Params: {trial.params}\n")
            f.write("  Objective values:\n")
            for objective_value in trial.values:
                f.write(f"    {objective_value}\n")
            f.write("\n")

    
        
if __name__ == "__main__":
    main()
    """
    # Profiler hele programmet ditt
    cProfile.run('main()', 'program_profile')

    # Last inn og analyser profildata, fokusert på dine funksjoner
    p = pstats.Stats('program_profile')
    p.strip_dirs().sort_stats(SortKey.TIME).print_stats()

    """ 