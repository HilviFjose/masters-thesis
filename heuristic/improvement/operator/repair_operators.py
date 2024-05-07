import pandas as pd
import copy
import math
import numpy.random as rnd 
import random 
import networkx as nx
from sklearn.cluster import KMeans
from scipy.spatial import cKDTree
import ast
import time

from config import main_config


import os
import sys
sys.path.append( os.path.join(os.path.split(__file__)[0],'..','..','..'))  # Include subfolders

from helpfunctions import checkCandidateBetterThanBest

from objects.activity import Activity
from config.construction_config_infusion import *
from datageneration.distance_matrix import *
from heuristic.improvement.operator.insertor import Insertor
from parameters import T_ij

#TODO: Finne ut hva operator funksjonene skal returnere 
class RepairOperators:
    def __init__(self, alns):
        self.constructor = alns.constructor

        self.count = 0 


    #TODO: Skal vi rullere på hvilke funksjoner den gjør først? Det burde vel også vært i ALNS funksjonaliteten 
    def greedy_repair(self, destroyed_route_plan, current_iteration, total_iterations):
        repaired_route_plan = copy.deepcopy(destroyed_route_plan)
        #start_time = time.perf_counter()
        
        repaired_route_plan = self.illegal_activity_repair(repaired_route_plan)

        repaired_route_plan = self.illegal_visit_repair(repaired_route_plan)
        
        repaired_route_plan = self.illegal_treatment_repair(repaired_route_plan)   

        repaired_route_plan = self.illegal_patient_repair(repaired_route_plan)  

        #end_time = time.perf_counter()
        #print("Ferdig med illegal insetting, sekunder:", str(end_time-start_time)) 
  

        repair_insertor_level = main_config.repair_insertor
        if current_iteration % main_config.modNum_for_better_insertion == 0: 
            print("iteration ", current_iteration, "main_config.modNum_for_better_insertion", main_config.modNum_for_better_insertion)
            repair_insertor_level = main_config.better_repair_insertor
        descendingUtilityNotAllocatedPatientsDict =  {patient: self.constructor.patients_array[patient][13] for patient in repaired_route_plan.notAllocatedPatients}
        descendingUtilityNotAllocatedPatients = sorted(descendingUtilityNotAllocatedPatientsDict, key=descendingUtilityNotAllocatedPatientsDict.get, reverse = True)

        for patient in descendingUtilityNotAllocatedPatients: 
            #start_time =    time.perf_counter()
            patientInsertor = Insertor(self.constructor, repaired_route_plan, repair_insertor_level) #Må bestemmes hvor god visitInsertor vi skal bruke
            old_route_plan = copy.deepcopy(repaired_route_plan)
            status = patientInsertor.insert_patient(patient)
            
            if status == True: 
                repaired_route_plan = patientInsertor.route_plan

                #Steg 1 - Slette i allokert listene
                repaired_route_plan.notAllocatedPatients.remove(patient)

                #Steg 2 - Oppdater allokert dictionariene 
                repaired_route_plan.updateAllocationAfterPatientInsertor(patient, self.constructor)

            else:
                repaired_route_plan = copy.deepcopy(old_route_plan)

            #end_time = time.perf_counter()
            #print(status, "Pasient", patient, "brukte tid", str(end_time-start_time)) 
    
        repaired_route_plan.updateObjective(current_iteration, total_iterations)
      
        return repaired_route_plan
    
    def random_repair(self, destroyed_route_plan, current_iteration, total_iterations):
        repaired_route_plan = copy.deepcopy(destroyed_route_plan)
        
        repaired_route_plan = self.illegal_activity_repair(repaired_route_plan)

        repaired_route_plan = self.illegal_visit_repair(repaired_route_plan)

        repaired_route_plan = self.illegal_treatment_repair(repaired_route_plan)   

        repaired_route_plan = self.illegal_patient_repair(repaired_route_plan)   
    
        repair_insertor_level = main_config.repair_insertor
        if current_iteration % main_config.modNum_for_better_insertion == 0: 
            repair_insertor_level = main_config.better_repair_insertor
        randomNotAllocatedPatients = repaired_route_plan.notAllocatedPatients
        random.shuffle(randomNotAllocatedPatients)

        for patient in randomNotAllocatedPatients: 
            patientInsertor = Insertor(self.constructor, repaired_route_plan, repair_insertor_level) #Må bestemmes hvor god visitInsertor vi skal bruke
            old_route_plan = copy.deepcopy(repaired_route_plan)
            status = patientInsertor.insert_patient(patient)

            if status == True: 
                repaired_route_plan = patientInsertor.route_plan

                #Steg 1 - Slette i allokert listene
                repaired_route_plan.notAllocatedPatients.remove(patient)

                #Steg 2 - Oppdater allokert dictionariene 
                repaired_route_plan.updateAllocationAfterPatientInsertor(patient, self.constructor)
            
            else:
                repaired_route_plan = copy.deepcopy(old_route_plan)

        repaired_route_plan.updateObjective(current_iteration, total_iterations)

        return repaired_route_plan


    def complexity_repair(self, destroyed_route_plan, current_iteration, total_iterations):
        repaired_route_plan = copy.deepcopy(destroyed_route_plan)

        repaired_route_plan = self.illegal_activity_repair(repaired_route_plan)

        repaired_route_plan = self.illegal_visit_repair(repaired_route_plan)

        repaired_route_plan = self.illegal_treatment_repair(repaired_route_plan)  

        repaired_route_plan = self.illegal_patient_repair(repaired_route_plan)


        repair_insertor_level = main_config.repair_insertor
        if current_iteration % main_config.modNum_for_better_insertion == 0: 
            print("iteration ", current_iteration, "main_config.modNum_for_better_insertion", main_config.modNum_for_better_insertion)
            repair_insertor_level = main_config.better_repair_insertor
        descendingComplexityNotAllocatedPatientsDict =  {patient: self.constructor.patients_array[patient][14] for patient in repaired_route_plan.notAllocatedPatients}
        descendingComplexityNotAllocatedPatients = sorted(descendingComplexityNotAllocatedPatientsDict, key=descendingComplexityNotAllocatedPatientsDict.get, reverse=True)
        
        for patient in descendingComplexityNotAllocatedPatients: 
            patientInsertor = Insertor(self.constructor, repaired_route_plan, repair_insertor_level) #Må bestemmes hvor god visitInsertor vi skal bruke
            old_route_plan = copy.deepcopy(repaired_route_plan)
            status = patientInsertor.insert_patient(patient)

            if status == True: 

                repaired_route_plan = patientInsertor.route_plan

                #Steg 1 - Slette i allokert listene
                repaired_route_plan.notAllocatedPatients.remove(patient)

                #Steg 2 - Oppdater allokert dictionariene 
                repaired_route_plan.updateAllocationAfterPatientInsertor(patient, self.constructor)
            
            else:
                repaired_route_plan = copy.deepcopy(old_route_plan)
   
        repaired_route_plan.updateObjective(current_iteration, total_iterations)
      
        return repaired_route_plan
    


    
    def regret_k_repair(self, destroyed_route_plan, current_iteration, total_iterations):
        repaired_route_plan = copy.deepcopy(destroyed_route_plan)

        repaired_route_plan = self.illegal_activity_repair(repaired_route_plan)

        repaired_route_plan = self.illegal_visit_repair(repaired_route_plan)

        repaired_route_plan = self.illegal_treatment_repair(repaired_route_plan)  

        repaired_route_plan = self.illegal_patient_repair(repaired_route_plan)

        descendingUtilityNotAllocatedPatientsDict =  {patient: self.constructor.patients_array[patient][13] for patient in repaired_route_plan.notAllocatedPatients}
        descendingUtilityNotAllocatedPatients = sorted(descendingUtilityNotAllocatedPatientsDict, key=descendingUtilityNotAllocatedPatientsDict.get)
        
        repair_insertor_level = main_config.repair_insertor
        if current_iteration % main_config.modNum_for_better_insertion == 0: 
            print("iteration ", current_iteration, "main_config.modNum_for_better_insertion", main_config.modNum_for_better_insertion)

            repair_insertor_level = main_config.better_repair_insertor
        best_repaired_route_plan_with_k_regret = copy.deepcopy(repaired_route_plan)
        best_repaired_route_plan_with_k_regret.updateObjective(current_iteration, total_iterations)
        for k in range(1, main_config.k): 
            repaired_route_plan_with_k_regret = copy.deepcopy(repaired_route_plan)

            for patient in descendingUtilityNotAllocatedPatients[k:]: 
                patientInsertor = Insertor(self.constructor, repaired_route_plan_with_k_regret,repair_insertor_level) #Må bestemmes hvor god visitInsertor vi skal bruke
                old_route_plan = copy.deepcopy(repaired_route_plan_with_k_regret)
                status = patientInsertor.insert_patient(patient)
                
                if status == True: 
                    repaired_route_plan_with_k_regret = patientInsertor.route_plan

                    #Steg 1 - Slette i allokert listene
                    repaired_route_plan_with_k_regret.notAllocatedPatients.remove(patient)

                    #Steg 2 - Oppdater allokert dictionariene 
                    repaired_route_plan_with_k_regret.updateAllocationAfterPatientInsertor(patient, self.constructor)

                else:
                    repaired_route_plan_with_k_regret = copy.deepcopy(old_route_plan)
        
            repaired_route_plan_with_k_regret.updateObjective(current_iteration, total_iterations)

            if checkCandidateBetterThanBest(repaired_route_plan_with_k_regret.objective, best_repaired_route_plan_with_k_regret.objective): 
                best_repaired_route_plan_with_k_regret = repaired_route_plan_with_k_regret
      
        return best_repaired_route_plan_with_k_regret
    

    #TODO: Burde se på en operator som bytter å mye som mulig mellom to ansatte. Hvorfor det? 

# ------------ HELP FUNCTIONS ------------

    def illegal_activity_repair(self, repaired_route_plan): 
        activityIterationDict = copy.copy(repaired_route_plan.illegalNotAllocatedActivitiesWithPossibleDays)
        
        for activityID, day in activityIterationDict.items():
            activity = Activity(self.constructor.activities_array, activityID)

            #BEG: Jeg tror egentlig ikke vi trenger den som er under her 
            repaired_route_plan.updateActivityBasedOnRoutePlanOnDay(activity, day)
            status = repaired_route_plan.addActivityOnDay(activity,day)
            
            #Alternativ 1 
            if status == True: 
                
                #Steg 1 - Slette i illegal listene 
                del repaired_route_plan.illegalNotAllocatedActivitiesWithPossibleDays[activityID]
                
                for visit in range(1, len(self.constructor.visits_array)):
                    if activityID in self.constructor.visits_array[visit][14]: 
                        break

                #Steg 2 - Oppdater allokert dictionariene                
                repaired_route_plan.visits[visit].append(activityID) 
        
        #Ingen alternativ 2 
        return repaired_route_plan

  
    def illegal_visit_repair(self, repaired_route_plan): 
        illegal_visit_iteration_list = list(repaired_route_plan.illegalNotAllocatedVisitsWithPossibleDays.keys())
        for visit in illegal_visit_iteration_list:  
            visitInsertor = Insertor(self.constructor, repaired_route_plan, main_config.illegal_repair_insertor) #Må bestemmes hvor god visitInsertor vi skal bruke
            old_route_plan = copy.deepcopy(repaired_route_plan)
            status = visitInsertor.insertVisitOnDay(visit, repaired_route_plan.illegalNotAllocatedVisitsWithPossibleDays[visit])
            
            #Alternativ 1 
            if status == True: 
                repaired_route_plan = visitInsertor.route_plan
                
                #Steg 1 - Slette i illegal listene 
                del repaired_route_plan.illegalNotAllocatedVisitsWithPossibleDays[visit]

                #Legger til visitet på treatmenten. Vet at treatmenten ligger inne, for hvis ikke så ville ikke visitet vært illegal 
                for treatment in range(1, len(self.constructor.treatments_array)):
                    if visit in self.constructor.treatments_array[treatment][18]: 
                        break

                #Steg 2 - Oppdater allokert dictionariene 
                repaired_route_plan.treatments[treatment].append(visit) 
                #Legge til visit og activities som hører til treatmentet 
                repaired_route_plan.visits[visit] = self.constructor.visits_array[visit][14]

            #Alternativ 2 - Setter tilbake ruteplanen, dersom ingen insertion 
            else: 
                repaired_route_plan = copy.deepcopy(old_route_plan)
        return repaired_route_plan
    
    def illegal_treatment_repair(self, repaired_route_plan): 
        for treatment in repaired_route_plan.illegalNotAllocatedTreatments:  
            treatmentInsertor = Insertor(self.constructor, repaired_route_plan, main_config.illegal_repair_insertor) #Må bestemmes hvor god visitInsertor vi skal bruke
            old_route_plan = copy.deepcopy(repaired_route_plan)
            status = treatmentInsertor.insert_treatment(treatment)
            
            #Alternativ 1
            if status == True: 
                repaired_route_plan = treatmentInsertor.route_plan

                #Steg 1 - Slette i illegal listene  
                repaired_route_plan.illegalNotAllocatedTreatments.remove(treatment)
                
                #Legger til treatmenten på pasienten. Vet at pasienten allerede ligger inne, for hvis ikke ville ikke treatmenten i utgnaspunktet vært illegal 
                for patient_id in range(1, len(self.constructor.patients_array)):
                    if treatment in self.constructor.patients_array[patient_id][11]: 
                        break

                #Steg 2 - Oppdater allokert dictionariene 
                repaired_route_plan.allocatedPatients[patient_id].append(treatment)
                #Legge til visit og activities som hører til treatmentet 
                repaired_route_plan.treatments[treatment] = self.constructor.treatments_array[treatment][18]
                for visit in repaired_route_plan.treatments[treatment]: 
                    repaired_route_plan.visits[visit] = self.constructor.visits_array[visit][14]
            #Alternativ 2       
            else:
                repaired_route_plan = copy.deepcopy(old_route_plan)

        return repaired_route_plan

    def illegal_patient_repair(self, repaired_route_plan): 
         
        for patient in repaired_route_plan.illegalNotAllocatedPatients:  
            patientInsertor = Insertor(self.constructor, repaired_route_plan, main_config.illegal_repair_insertor) #Må bestemmes hvor god visitInsertor vi skal bruke
            old_route_plan = copy.deepcopy(repaired_route_plan)
            status = patientInsertor.insert_patient(patient)
            
            #Alternativ 1
            if status == True: 
                repaired_route_plan = patientInsertor.route_plan

                #Steg 1 - Slette i illegal listene
                repaired_route_plan.illegalNotAllocatedPatients.remove(patient)

                #Steg 2 - Oppdater allokert dictionariene 
                repaired_route_plan.updateAllocationAfterPatientInsertor(patient, self.constructor)
            
            #Alternativ 2
            else: 
                repaired_route_plan = copy.deepcopy(old_route_plan)
        
        return repaired_route_plan
        
      
