import pandas as pd
from heuristic.construction.construction import ConstructionHeuristic

'''
Ikke ferdigarbeidet klasse. 
'''


def main():
    constructor = None


    try:
        #Input

        #Henter ut data fra dataframes som vi sender inn
        df_activities  = pd.read_csv("data/NodesNY.csv").set_index(["id"]) 
        df_employees = pd.read_csv("data/EmployeesNY.csv").set_index(["EmployeeID"])
        df_patients = pd.read_csv("data/Patients.csv").set_index(["patient"])
        df_treatments = pd.read_csv("data/Treatment.csv").set_index(["treatment"])
        df_visits = pd.read_csv("data/Visit.csv").set_index(["visit"])
        #TODO: Finne ut hva som skjer i datahåndteringen over. Hvordan lages dataframene, og hvordan bruks config filene
        #Her lages en kontruksjonsheuristikk. Våre requests vil være pasienter, og vi går gjennom alle
        constructor = ConstructionHeuristic(activities=df_activities, employees = df_employees, patients =df_patients)

        #TODO: Sjekke hva man skal ha inn av dataframes
        print(constructor.getT_ij())  #TODO: Denne er ikke riktig nå, vet ikke hvorfor den blir feil, men vi kan se på det senere. 
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