from tqdm import tqdm
import pandas as pd
import numpy as np
import copy
import os
import sys
sys.path.append( os.path.join(os.path.split(__file__)[0],'..') )  # Include subfolders
from objects.route_plan import RoutePlan
from heuristic.improvement.operator.insertor import Insertor
from helpfunctions import checkCandidateBetterThanBest
from config.main_config import num_of_constructions, iterations, construction_insertor

'''
Info: ConstructionHeurstic klassen er selve konstruskjonsheurstikken. 
Den opprettes med et løsning i form av en RoutePlan objekt, objektivverdi og null pasienter
Gjennom construct_inital funksjonen så oppdateres løsningen, objektivverdien og pasientlisten
'''


class ConstructionHeuristic:
    def __init__(self, activities_array,  employees_array, patients_array, treatments_array, visits_array, days, folder_name):
        
        self.activities_array = activities_array
        self.visits_array = visits_array
        self.treatments_array = treatments_array
        self.patients_array = patients_array
        self.employees = employees_array
        self.days = days
        self.folder_name = folder_name
        #self.route_plan = RoutePlan(days, employees_df) 

        self.route_plans = [RoutePlan(days, employees_array, folder_name) for _ in range(num_of_constructions) ]

        self.route_plan = None
        
    '''s
    Oppdatering av matrisene. I dette statidiet vil vi bare godekjenne inserting av pasienter som fullstendig legges inn på hjemmesykehuset 

    Dersom pasientne allokeres legges nå alle de tilhørende treatments, visits og aktiviteter til 
    '''
 
    def construct_simple_initial(self, a): 
        route_plan = RoutePlan(self.days, self.employees_df, self.folder_name)
        #Lager en liste med pasienter i prioritert rekkefølge. 
        unassigned_patients = self.patients_df.sort_values(by=['allocation', 'aggUtility'], ascending=[False, False])
        #Iterer over hver pasient i lista. Pasienten vi ser på kalles videre pasient
        for i in tqdm(range(unassigned_patients.shape[0]), colour='#39ff14'):
            #Henter ut raden i pasient dataframes som tilhører pasienten
            patient = unassigned_patients.index[i] 
            allocation = unassigned_patients.loc[patient, 'allocation']
            
            #Kopierer nåværende ruteplan for denne pasienten 
            route_plan_with_patient = copy.deepcopy(route_plan)

            patientInsertor = Insertor(self, route_plan_with_patient, construction_insertor) #Må bestemmes hvor god visitInsertor vi skal bruke
            state = patientInsertor.insert_patient(patient)
        
            if state == True: 
                #Construksjonsheuristikkens ruteplan oppdateres til å inneholde pasienten
                route_plan = patientInsertor.route_plan
                
                #Pasienten legges til i hjemmsykehusets liste med pasienter
                self.updateConstructionAllocationInformation(route_plan, patient)
                #Oppdaterer ruteplanen 
                
            #Hvis pasienten ikke kan legges inn puttes den i Ikke allokert lista
            #TODO: Hva trenger egentlig å konstrueres i dette
            if state == False: 
                
            
                if allocation == 0: 
                    route_plan.notAllocatedPatients.append(patient)
                else: 
                    route_plan.illegalNotAllocatedPatients.append(patient)
        
        #TODO: Oppdatere alle dependencies når vi har konstruert løsning - Jeg forstår ikke helt denne 
        for day in range(1, 1+ self.days): 
            for route in route_plan.routes[day].values(): 
                for activity in route.route: 
                    route_plan.updateActivityBasedOnRoutePlanOnDay(activity, day)
        route_plan.updateObjective(0, iterations)

        return route_plan 
        

    def construct_initial(self): 
        patient_list = self.patients_array[1:].tolist()
        sorted_unassigned_patients = sorted(patient_list, key=lambda x: (x[2], x[13]))
        #Iterer over hver pasient i lista. Pasienten vi ser på kalles videre pasient
        for j in range(len(self.route_plans)): 
            route_plan = self.route_plans[j]
            for i in tqdm(range(len(sorted_unassigned_patients)), colour='#39ff14'):
                patient_id = i+1
                allocation = sorted_unassigned_patients[i][2]
                
                #Kopierer nåværende ruteplan for denne pasienten 
                route_plan_with_patient = copy.deepcopy(route_plan)

                patientInsertor = Insertor(self, route_plan_with_patient, construction_insertor) #Må bestemmes hvor god visitInsertor vi skal bruke
                state = patientInsertor.insert_patient(patient_id)
            
                if state == True: 
                    #Construksjonsheuristikkens ruteplan oppdateres til å inneholde pasienten
                    route_plan = patientInsertor.route_plan
                    
                    #Pasienten legges til i hjemmsykehusets liste med pasienter
                    self.updateConstructionAllocationInformation(route_plan, patient_id)
                    #Oppdaterer ruteplanen 
                    
                #Hvis pasienten ikke kan legges inn puttes den i Ikke allokert lista
                #TODO: Hva trenger egentlig å konstrueres i dette
                if state == False: 
                    
                
                    if allocation == 0: 
                        route_plan.notAllocatedPatients.append(patient_id)
                    else: 
                        route_plan.illegalNotAllocatedPatients.append(patient_id)
            
            #TODO: Oppdatere alle dependencies når vi har konstruert løsning - Jeg forstår ikke helt denne 
            for day in range(1, 1+ self.days): 
                for route in route_plan.routes[day].values(): 
                    for activity in route.route: 
                        route_plan.updateActivityBasedOnRoutePlanOnDay(activity, day)
            route_plan.updateObjective(0, iterations)
            self.route_plans[j] = route_plan
            
        self.setBestRoutePlan()

    def setBestRoutePlan(self): 
        best_route_plan = self.route_plans[0]
        for route_plan in self.route_plans[1:]: 
            if checkCandidateBetterThanBest(route_plan.objective, best_route_plan.objective) and self.checkIfConstructionIsLegal(route_plan) or (
                not self.checkIfConstructionIsLegal(best_route_plan) and self.checkIfConstructionIsLegal(route_plan)) or (
                    checkCandidateBetterThanBest(route_plan.objective, best_route_plan.objective) and not self.checkIfConstructionIsLegal(route_plan) and
                not self.checkIfConstructionIsLegal(best_route_plan)
            ): 
             
                best_route_plan = route_plan
        self.route_plan = best_route_plan


    def checkIfConstructionIsLegal(self, route_plan): 
        if len(route_plan.illegalNotAllocatedPatients) > 0: 
            return False 
        return True 
    

    def updateConstructionAllocationInformation(self, route_plan, patient): 
        route_plan.allocatedPatients[patient] = self.patients_array[patient][11] 
        for treatment in [item for sublist in route_plan.allocatedPatients.values() for item in sublist]: 
            route_plan.treatments[treatment] = self.treatments_array[treatment][18]
        for visit in [item for sublist in route_plan.treatments.values() for item in sublist]: 
            route_plan.visits[visit] = self.visits_array[visit][14]



