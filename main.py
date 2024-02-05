
'''
from heuristic.construction.construction import ConstructionHeuristic
from heuristic.destroyer.random_removal import RandomRemoval
from heuristic.repairer.insertion_greedy import InsertionGreedy
'''
#Jeg vet ikke hva det over er 

import pandas as pd
from heuristic.construction.construction import ConstructionHeuristic




def main():
    constructor = None


    try:
        #Input

        #Henter ut data fra dataframes som vi sender inn
        df_activities = pd.read_csv("data/EmployeesNY.csv")
        print("kommer hit")
        df_employees = pd.read_csv("data/NodesNY.csv")
        df_patients = pd.read_csv("data/VisitsNY.csv")
        #TODO: Finne ut hva som skjer i datahåndteringen over. Hvordan lages dataframene, og hvordan bruks config filene
        print(df_activities)
        #Her lages en kontruksjonsheuristikk. Våre requests vil være pasienter, og vi går gjennom alle
        constructor = ConstructionHeuristic(df_activities, employees = df_employees, patients =df_patients)
        constructor.jegFinnes
        #TODO: Sjekke hva man skal ha inn av dataframes

        print("Constructing initial solution")
        #bruke construct inital funksjonen til konstruksjonsheristkken som er opprettet
        #Denne funskjonen returnerer en inisell rute med objektiv, og inisiell ifeasible set 
        #TODO: Forstå mer hva dette med infeasible set er, tror det brukes senere. 
        #Er det typ
        '''
        initial_route_plan, initial_objective, initial_infeasible_set = constructor.construct_initial()
        constructor.print_new_objective(
            initial_route_plan, initial_infeasible_set)
        '''


    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    main()