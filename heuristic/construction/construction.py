from tqdm import tqdm
from insertion_generator import InsertionGenerator
import pandas as pd
from typing import List
import json
import requests
import pandas as pd
import copy

import sys
sys.path.append("C:\\Users\\agnesost\\masters-thesis")

from objects.route_plan import RoutePlan


class ConstructionHeuristic:
    def __init__(self, activities_df,  employees_df, patients_df, treatment_df, visit_df, days):
        
        self.activities_df = activities_df
        self.visit_df = visit_df
        self.treatment_df = treatment_df
        self.patients_df = patients_df
        self.employees_df = employees_df
        self.days = days
        self.route_plan = RoutePlan(days, employees_df) 
        self.current_objective = 0 
        self.listOfPatients = []
        
 
    '''
 

    Det først vi gjør etter at cosntruction heuristikken er laget. 
    Her konstrueres det et løsningsobjekt, som er route plan

    Objektivverdi: Hvorfor vil vi ha objektivverdi i denne klassen, og ikke i routeplan?
    Hvorfor skal det hentes opp? 
    
    Prove å forstå selve konstruksjonsheurstikk klassen. Den har en ruteplan. Denne må være for hver ansatt på hver dag som jobber.  
    '''
    def construct_initial(self): 
        #Lage en liste med requests og sortere de. Lage en prioritert liste med pasienter
        unassigned_patients = df_patients.sort_values(by="aggSuit", ascending=False)
        
        #Lager en original ruteplan
        
        for i in tqdm(range(unassigned_patients.shape[0]), colour='#39ff14'):
            patient_request = unassigned_patients.iloc[i]
            insert_routeplan = copy.deepcopy(self.route_plan)
            insertion_generator = InsertionGenerator(self, insert_routeplan, patient_request, self.treatment_df, self.visit_df, self.activities_df)
            state = insertion_generator.generate_insertions()
            #Sender inn self_route plan men skal ikke hente den ut igjen. 
            if state == True: 
                self.route_plan = insertion_generator.route_plan
                self.current_objective += patient_request["aggSuit"]
                self.listOfPatients.append(patient_request[0])
       
        #Lage en insert generator som prøver å legge til pasient. 
        #Vil først få ny objektivverdi når en hel pasient er lagt til, så gir mening å kalle den her
        return self.route_plan, self.current_objective
    
    #IDE: Må lage en generate insertion, som kan ta inn en liste med aktiviteter. 
    #Forskjellen på vår og deres er at det blir veldig raskt ugylldig 
   
'''
Ruten oppdateres selv om pasienten ikke legges til. Construct iital henter ut ritkig state

Det er ikke gjensidig avhengighet. Fordi nå hentes alt fra contriction, og sendes inn
Problem state blir aldri sant for treatment 8, likevel så legges aktivitet 13 og 14 til. 
Den oppdaterte ruten med disse verdiene tar steget videre 
'''

#Disse skal ikk her men limer innforeløpig
df_activities  = pd.read_csv("data/NodesNY.csv").set_index(["id"]) 
df_employees = pd.read_csv("data/EmployeesNY.csv").set_index(["EmployeeID"])
df_patients = pd.read_csv("data/Patients.csv").set_index(["patient"])
df_treatments = pd.read_csv("data/Treatment.csv").set_index(["treatment"])
df_visits = pd.read_csv("data/Visit.csv").set_index(["visit"])

testConsHeur = ConstructionHeuristic(df_activities, df_employees, df_patients, df_treatments, df_visits, 5)
route_plan, obj = testConsHeur.construct_initial()
testConsHeur.route_plan.printSoultion()
print("Dette er objektivet", testConsHeur.current_objective)
print(testConsHeur.listOfPatients)
#TODO: printe routeplan for å se om det ble noe 


#TODO: Fikse slik at pasienter enten er med eller ikkke. 
#Må få igang state variablene

'''
Arbeid: 

TODO: Usikker på om employeerestrictions slår inn eller ikke. Det må vi sjekke 

TODO: Tror vi ville fått feil i ruteobjektet hele det første visitet var mulig. 
Slik at det legger seg inn også få neste plass i et annet pattern. Da blir det duplisert,
MÅ sjekkes ut 
'''