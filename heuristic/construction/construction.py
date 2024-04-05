from tqdm import tqdm
import pandas as pd
import copy
import os
import sys
sys.path.append( os.path.join(os.path.split(__file__)[0],'..') )  # Include subfolders
from objects.route_plan import RoutePlan
from heuristic.improvement.operator.insertor import Insertor

'''
Info: ConstructionHeurstic klassen er selve konstruskjonsheurstikken. 
Den opprettes med et løsning i form av en RoutePlan objekt, objektivverdi og null pasienter
Gjennom construct_inital funksjonen så oppdateres løsningen, objektivverdien og pasientlisten
'''


class ConstructionHeuristic:
    def __init__(self, activities_df,  employees_df, patients_df, treatment_df, visit_df, days):
        
        self.activities_df = activities_df
        self.visit_df = visit_df
        self.treatment_df = treatment_df
        self.patients_df = patients_df
        self.employees_df = employees_df
        self.days = days

        self.route_plan = RoutePlan(days, employees_df) 
        
        
    '''
    Oppdatering av matrisene. I dette statidiet vil vi bare godekjenne inserting av pasienter som fullstendig legges inn på hjemmesykehuset 

    Dersom pasientne allokeres legges nå alle de tilhørende treatments, visits og aktiviteter til 
    '''
 
    def construct_initial(self): 
        '''
        Funksjonen iterer over alle paienter som kan allokeres til hjemmesykehuset. 
        Rekkefølgen bestemmes av hvor mye aggregert suitability pasienten vil tilføre ojektivet
        '''

        #Lager en liste med pasienter i prioritert rekkefølge. 
        unassigned_patients = self.patients_df.sort_values(by="aggUtility", ascending=False)
        
        #Iterer over hver pasient i lista. Pasienten vi ser på kalles videre pasient
        for i in tqdm(range(unassigned_patients.shape[0]), colour='#39ff14'):
            #Henter ut raden i pasient dataframes som tilhører pasienten
            patient = unassigned_patients.index[i] 
            
            #Kopierer nåværende ruteplan for denne pasienten 
            route_plan_with_patient = copy.deepcopy(self.route_plan)

            patientInsertor = Insertor(self, route_plan_with_patient)
            state = patientInsertor.insert_patient(patient)
           
            if state == True: 
                #Construksjonsheuristikkens ruteplan oppdateres til å inneholde pasienten
                self.route_plan = patientInsertor.route_plan
                
                self.updateAllocationInformation(patient)
                #Oppdaterer ruteplanen 
                
            #Hvis pasienten ikke kan legges inn puttes den i Ikke allokert lista
            if state == False: 
                
                self.route_plan.notAllocatedPatients.append(patient)
        
        #TODO: Oppdatere alle dependencies når vi har konstruert løsning 
        for day in range(1, 1+ self.days): 
            for route in self.route_plan.routes[day]: 
                for activity in route.route: 
                    self.route_plan.updateActivityBasedOnRoutePlanOnDay(activity, day)

    
    def updateAllocationInformation(self, patient): 
        self.route_plan.allocatedPatients[patient] = self.patients_df.loc[patient, 'treatmentsIds']
        for treatment in [item for sublist in self.route_plan.allocatedPatients.values() for item in sublist]: 
            self.route_plan.treatments[treatment] = self.treatment_df.loc[treatment, 'visitsIds']
        for visit in [item for sublist in self.route_plan.treatments.values() for item in sublist]: 
            self.route_plan.visits[visit] = self.visit_df.loc[visit, 'activitiesIds']
        
#TODO: Endre slik at dataen ikke må hentes på denne måten

