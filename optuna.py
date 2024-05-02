import optuna

def objective(trial):
    # Suggesting parameters
    reaction_factor = trial.suggest_uniform('reaction_factor', 0.0, 1.0)
    local_search_req = trial.suggest_int('local_search_requirement', 1, 10)
    destruction_degree = trial.suggest_int('destruction_degree', 1, 10)
    weight_scores = trial.suggest_categorical('weight_scores', [
        [0.1, 0.2, 0.3, 0.4],  # Example weights configuration
        [0.2, 0.3, 0.1, 0.4]
    ])
    penalties = trial.suggest_categorical('penalties', [
        [10, 15],  # Example penalties configuration
        [20, 25]
    ])

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
