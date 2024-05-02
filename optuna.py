import optuna

def objective(trial):
    # Suggesting parameters
    reaction_factor = trial.suggest_float('reaction_factor', reaction_factor_interval)
    local_search_req = trial.suggest_float('local_search_req', local_search_interval)
    weight_score_best = trial.suggest_int('weight_score_best', weight_score_best_interval)
    weight_score_better = trial.suggest_int('weight_score_better', weight_score_better_interval)
    weight_score_accepted = trial.suggest_int('weight_score_accepted', weight_score_accepted_interval)
    iteartions_update = trial.suggest_float('iterations_update', iterations_update_interval)

    # Configure and run ALNS
    alns = setup_alns(reaction_factor, local_search_req, destruction_degree, weight_scores, penalties)
    result = run_alns(alns, iterations=200, patients_count=30)  # Reduced for tuning

    return result.objective_score  # Objective to minimize

def main():
    study = optuna.create_study(direction='minimize')
    study.optimize(objective, n_trials=50)  # Fewer trials for initial exploration

    print("Best parameters:", study.best_trial.params)

if __name__ == '__main__':
    main()
