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
        self.listOfPatients = []
        self.unAssignedPatients = []
        
 
    def construct_initial(self): 
        '''
        Funksjonen iterer over alle paienter som kan allokeres til hjemmesykehuset. 
        Rekkefølgen bestemmes av hvor mye aggregert suitability pasienten vil tilføre ojektivet
        '''

        #Lager en liste med pasienter i prioritert rekkefølge. 
        unassigned_patients = self.patients_df.sort_values(by=['allocation', 'aggUtility'], ascending=[True, True])

        
        #Iterer over hver pasient i lista. Pasienten vi ser på kalles videre pasient
        for i in tqdm(range(unassigned_patients.shape[0]), colour='#39ff14'):
            #Henter ut raden i pasient dataframes som tilhører pasienten
            patient = unassigned_patients.index[i] 
            allocation = unassigned_patients.loc[patient, 'allocation']
            
            #Kopierer nåværende ruteplan for denne pasienten 
            route_plan_with_patient = copy.deepcopy(self.route_plan)

            '''
            #Oppretter et PatientInsertor objekt, hvor pasient_df og kopien av dagens ruteplan sendes inn
            patientInsertor = PatientInsertor( route_plan_with_patient, patient_request, self)
            #patientInsertor forsøker å legge til pasienten, og returnerer True hvis velykket
            state = patientInsertor.insert_patients()
            '''
            '''
            Kommentar: Forsøker å ta bort patient insertor og bytte den ut med Insertor, slik at vi bare har en fil i bruk 
            '''
            patientInsertor = Insertor(self, route_plan_with_patient)
            state = patientInsertor.insert_patient(patient)
           
            if state == True: 
                #Construksjonsheuristikkens ruteplan oppdateres til å inneholde pasienten
                self.route_plan = patientInsertor.route_plan
                #Pasienten legges til i hjemmsykehusets liste med pasienter
                self.listOfPatients.append(patient)
                

                
            #Hvis pasienten ikke kan legges inn puttes den i Ikke allokert lista
            #TODO: Hva trenger egentlig å konstrueres i dette
            if state == False: 
                self.unAssignedPatients.append(patient)
                if allocation == 0: 
                    self.route_plan.notAllocatedPatients.append(patient)
                else: 
                    self.route_plan.illegalNotAllocatedPatients.append(patient)
        
        #TODO: Oppdatere alle dependencies når vi har konstruert løsning 
        for day in range(1, 1+ self.days): 
            for route in self.route_plan.routes[day]: 
                for activity in route.route: 
                    self.route_plan.updateActivityBasedOnRoutePlanOnDay(activity, day)
        
#TODO: Endre slik at dataen ikke må hentes på denne måten

