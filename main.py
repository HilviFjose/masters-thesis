import pandas as pd
from heuristic.construction.construction import ConstructionHeuristic
from config.main_config import *
from heuristic.improvement.simulated_annealing import SimulatedAnnealing
from heuristic.improvement.alns import ALNS
from heuristic.improvement.operator.operators import Operators

'''
Ikke ferdigarbeidet klasse. 
'''

#Anna Helle importert 
import numpy.random as rnd

def main():
    constructor = None

    #TODO: Burde legge til sånn try og accept kriterier her når vi er ferdig. Men Bruker ikke det enda fordi letter å jobbe uten

    
    #Input
    #TODO: Finne ut hva som skjer i datahåndteringen over. Hvordan lages dataframene, og hvordan bruks config filene
    
    df_activities  = pd.read_csv("data/NodesNY.csv").set_index(["id"]) 
    df_employees = pd.read_csv("data/EmployeesNY.csv").set_index(["EmployeeID"])
    df_patients = pd.read_csv("data/Patients.csv").set_index(["patient"])
    df_treatments = pd.read_csv("data/Treatment.csv").set_index(["treatment"])
    df_visits = pd.read_csv("data/Visit.csv").set_index(["visit"])

    #Her lages en kontruksjonsheuristikk. Våre requests vil være pasienter, og vi går gjennom alle.
    constructor = ConstructionHeuristic(df_activities, df_employees, df_patients, df_treatments, df_visits, 5)
    print("Constructing Inital Solution")
    constructor.construct_initial()
    
    constructor.route_plan.printSoultion()
    print("Dette er objektivet", constructor.current_objective)
    print("Hjemmesykehuspasienter ", constructor.listOfPatients)
    print("Ikke allokert ", constructor.unAssignedPatients)

    #TODO: Finne ut hva dette er 
    delayed = (False, None, None) 

    #IMPROVEMENT OF INITAL SOLUTION 
    random_state = rnd.RandomState()

    #Parameterne er hentet fra config. 
    criterion = SimulatedAnnealing(start_temperature, end_temperature, cooling_rate)

    alns = ALNS(weights, reaction_factor, initial_route_plan, initial_objective, initial_infeasible_set, criterion,
                    destruction_degree, constructor, rnd_state=rnd.RandomState())


    operators = Operators(alns)

    alns.set_operators(operators)

    #RUN ALNS 



    '''
    #TODO
    Fikse så vi har alle objektivverdier ut fra konstruksjonsheurstikken
    Forstå hva som er poenget med de ulike klassene 
    Begynne med en simulated anealing som godtar bare løsninger som er bedre 
    Legge til en operator som bare maksimerer objektivverdier innad på en dag
     - Fordele arbeidet jevnt mellom de ansatte (Vanskelig å sjekke med vårt datasett)
     - Minimere kjøretid 

    '''


if __name__ == "__main__":
    main()