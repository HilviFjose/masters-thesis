import pandas as pd
import numpy.random as rnd

from heuristic.construction.construction import ConstructionHeuristic
from config.main_config import *
from heuristic.improvement.simulated_annealing import SimulatedAnnealing
from heuristic.improvement.alns import ALNS
from heuristic.improvement.operator.operators import Operators
from datageneration import employeeGeneration
from datageneration import patientGeneration 
from datageneration import distance_matrix

import parameters

def main():
    constructor = None

    #TODO: Burde legge til sånn try og accept kriterier her når vi er ferdig. Men Bruker ikke det enda fordi letter å jobbe uten

    
    #Input
    #TODO: Finne ut hva som skjer i datahåndteringen over. Hvordan lages dataframene, og hvordan bruks config filene
    
    #df_employees = employeeGeneration.employeeGenerator() 
    #df_patients = patientGeneration.patientGenerator(df_employees)
    #df_treatments = patientGeneration.treatmentGenerator(df_patients)
    #df_visits = patientGeneration.visitsGenerator(df_treatments)
    #df_activities = patientGeneration.activitiesGenerator(df_visits)
    #df_patients_filled = patientGeneration.autofillPatient(df_patients, df_treatments).set_index(["patientId"])
    #df_treatments_filled = patientGeneration.autofillTreatment(df_treatments, df_visits).set_index(["treatmentId"])
    #df_visits_filled = patientGeneration.autofillVisit(df_visits, df_activities).set_index(["visitId"])  
    #df_activities = df_activities.set_index(["activityId"])  
    #df_employees = df_employees.set_index(["employeeId"])

    df_employees = parameters.df_employees
    df_patients = parameters.df_patients_filled
    df_treatments = parameters.df_treatments_filled
    df_visits = parameters.df_visits_filled
    df_activities = parameters.df_activities

    T_ij = distance_matrix.travel_matrix(df_activities)

    #df_activities  = pd.read_csv("data/test/ActivitiesNY.csv").set_index(["activityId"]) 
    #df_employees = pd.read_csv("data/test/EmployeesNY.csv").set_index(["employeeId"])
    #df_patients = pd.read_csv("data/test/PatientsNY.csv").set_index(["patientId"])
    #df_treatments = pd.read_csv("data/test/TreatmentsNY.csv").set_index(["treatmentId"])
    #df_visits = pd.read_csv("data/test/VisitsNY.csv").set_index(["visitId"])
    
    #Her lages en kontruksjonsheuristikk. Våre requests vil være pasienter, og vi går gjennom alle.
    constructor = ConstructionHeuristic(df_activities, df_employees, df_patients, df_treatments, df_visits, 5)
    print("Constructing Initial Solution")
    constructor.construct_initial()
    
    constructor.route_plan.printSoultion()
    print("Objektivverdier", constructor.route_plan.objective)
    print("Hjemmesykehuspasienter ", constructor.listOfPatients)
    print("Ikke allokert ", constructor.unAssignedPatients)

    initial_objective = constructor.route_plan.objective
    initial_route_plan = constructor.route_plan 
    initial_infeasible_set = constructor.unAssignedPatients #Usikker på om dette blir riktig. TODO: Finn ut mer om hva infeasible_set er.

    """    
    #IMPROVEMENT OF INITAL SOLUTION 
    #Parameterne er hentet fra config. 
    
    criterion = SimulatedAnnealing(start_temperature, end_temperature, cooling_rate)

    alns = ALNS(weights, reaction_factor, initial_route_plan, initial_objective, initial_infeasible_set, criterion,
                    destruction_degree, constructor, rnd_state=rnd.RandomState())


    operators = Operators(alns)

    alns.set_operators(operators)

    #RUN ALNS 
    current_route_plan, current_objective, current_infeasible_set, _ = alns.iterate(
            iterations)
    
    constructor.print_new_objective(
            current_route_plan, current_infeasible_set)
    
    #LOCAL SEARCH
    """

    '''
    #TODO
    Fikse så vi har alle objektivverdier ut fra konstruksjonsheurstikken
    Forstå hva som er poenget med de ulike klassene 
    Begynne med en simulated anealing som godtar bare løsninger som er bedre 
    Legge til en operator som bare maksimerer objektivverdier innad på en dag
     - Fordele arbeidet jevnt mellom de ansatte (Vanskelig å sjekke med vårt datasett)
     - Minimere kjøretid 

    '''

    '''
    #TODO
    Agnes: 
    - Fikse tidsvindu og employee restriction-kolonne i construction - Gjort 
    - Lage en funksjon for objektivvurdering som kan brukes i simulated annealing (Lag den som en global funksjon)

    Guro:
    - FERDIG: Tidsvinduer i data generation 
    - FERDIG: Lokasjoner i data generation
    - ISH FERDIG, SE PÅ SAMMEN: Fikse slik at kolonnene stemmer overens med Agnes sitt oppsett
    - Adaptive weights
    - Se på konstruksjonsheuristikken

    Hilvi: 
    - Begynne smått på operator-filen
    - Simulated annealing
    - Se på konstruksjonsheuristikken

    Generelt: 
    - Finne noen python-pakker for evaluering av effektiviteten til koden. 
    - Lage parameterfil for inputdata

    '''
    

if __name__ == "__main__":
    main()