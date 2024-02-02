
from heuristic.construction.construction import ConstructionHeuristic
from heuristic.destroyer.random_removal import RandomRemoval
from heuristic.repairer.insertion_greedy import InsertionGreedy

#Jeg vet ikke hva det over er 

import pandas as pd




def main():
    constructor = None


    try:
        #Input

        #Her henter vi ut en dataframe som er dataen var
        df = pd.read_csv(config("test_data_construction"))

        #Her lages en kontruksjonsheuristikk. Her vil v¨re requests vare pasienter. 
        #Her tar de bare med de 20 første, men vi tar med alle 
        constructor = ConstructionHeuristic(requests=df.head(R), vehicles=V)
        print("Constructing initial solution")
        initial_route_plan, initial_objective, initial_infeasible_set = constructor.construct_initial()
        constructor.print_new_objective(
            initial_route_plan, initial_infeasible_set)





    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    main()