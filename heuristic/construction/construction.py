from tqdm import tqdm
from insertion_generator import InsertionGenerator
import pandas as pd
from typing import List
import json
import requests
import pandas as pd

import sys
sys.path.append("C:\\Users\\agnesost\\masters-thesis")

from objects.route_plan import RoutePlan



'''
INFO:
I denne klassen definerer de mange funksjoner som jeg ikke forstår hva de bruker til senere. Lurer på det
Lurer også på hvorfor de oppretter distanseamatrisen her og ikke senere. Hvordan hentes dette opp igjen senere.
Må forstå mer av strukturen på det. 
'''



class ConstructionHeuristic:
    def __init__(self, activities_df,  employees_df, patients_df, treatment_df, visit_df, days):
        
        self.activities_df = activities_df
        self.visit_df = visit_df
        self.treatment_df = treatment_df
        self.patients_df = patients_df
        self.employees_df = employees_df
        self.days = days
        
    
        #Det er mye jeg ikke forstår med hvordan de andre generer 
        #Når konstruksjonsheuristikken opprettes så gjøres det en preprossesering i etterpå. 
        #De virker som at de lager en P_ij matrise beskriver hvordan ulike deler ligge ri forhold til hverandr

    def getActivities(self):
        return self.activities

 
    '''
    Hvordan fungere det med klaser hvor de kaller hverandre. 
    Konstruksjonsheuristikken har ulike løsninger og ruter som benyttes. Disse byttes ut etterhvert og vil variere. 
    Likevel må rutene kunne hente ut datagrunnlaget som hører til selve konstrukjsonen. Nei det kan de ikke 
    Dataen som skal brukes til den spessifikke oprerasjonen må sendes inn i de andre løsningene. 

    
    Beskrivelse av klassen: 
    Må forstå hva som skjer i de to klassene. 
    Lager en ConstructionHeuristic 
    Så kaller den construct initial, som gir ut den initial_route_plan, initial_objective, initial_infeasible_set

    construct initial: 
    Går gjennom hele lista med requests og prøve å 
    Hente ut alle pasienter, og finne scoren for de. 

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
        route_plan = RoutePlan(self.days, self.employees_df)
        new_objective = 0 
        
        for i in tqdm(range(unassigned_patients.shape[0]), colour='#39ff14'):
            patient_request = unassigned_patients.iloc[i]
            print("ser på pasient" + str(patient_request))
            insertion_generator = InsertionGenerator(self, route_plan,patient_request)
            insertion_generator.generate_insertions()
        '''
        patient_request = unassigned_patients.iloc[0]
        
        insertion_generator = InsertionGenerator(self, route_plan,patient_request)

        print(insertion_generator.getTreatments())
        print("-----------------------")
        print(insertion_generator.getPatientDF())

        insertion_generator.generate_insertions()
        '''
        #Lage en insert generator som prøver å legge til pasient. 
        #Vil først få ny objektivverdi når en hel pasient er lagt til, så gir mening å kalle den her
        return route_plan, new_objective


    #Denne lager et inisielt løsningsobjekt. 
    def construct_initialG(self):
        #Tror rid er request iden, går over alle requests som er gått. Dette blir aktiviteter for oss 
        rid = 1
        unassigned_requests = self.requests.copy()
        #Henter ut en introduced veichles, som er de veiclesenen som igang
        self.introduced_vehicles.add(self.vehicles.pop(0))
        route_plan = [[]]
        for i in tqdm(range(unassigned_requests.shape[0]), colour='#39ff14'):
            # while not unassigned_requests.empty:
            request = unassigned_requests.iloc[i]
            
            #Henter ut hvert request objekt fra unassigned requests. Iterer gjennom alle. 

            #Generate insertion kalles her. Da ønsker vi å putte inn en ny request, gitt den gjeldende ruteplanen 
            route_plan, new_objective = self.insertion_generator.generate_insertions(
                route_plan=route_plan, request=request, rid=rid)

            # update current objective
            self.current_objective = new_objective

            rid += 1
        #TODO: Forstår ikke helt hvorfor infeasible set returneres her? Her har jo ikke blitt gjort noe med 
        return route_plan, self.current_objective, self.infeasible_set
    
    #IDE: Må lage en generate insertion, som kan ta inn en liste med aktiviteter. 
    #Forskjellen på vår og deres er at det blir veldig raskt ugylldig 
   

#Disse skal ikk her men limer innforeløpig
df_activities  = pd.read_csv("data/NodesNY.csv").set_index(["id"]) 
df_employees = pd.read_csv("data/EmployeesNY.csv").set_index(["EmployeeID"])
df_patients = pd.read_csv("data/Patients.csv").set_index(["patient"])
df_treatments = pd.read_csv("data/Treatment.csv").set_index(["treatment"])
df_visits = pd.read_csv("data/Visit.csv").set_index(["visit"])

testConsHeur = ConstructionHeuristic(df_activities, df_employees, df_patients, df_treatments, df_visits, 5)
route_plan, obj = testConsHeur.construct_initial()
route_plan.printSoultion()
#TODO: printe routeplan for å se om det ble noe 


#TODO: Fikse slik at pasienter enten er med eller ikkke. 
#Må få igang state variablene