import pandas as pd
import copy
import math
import numpy.random as rnd 
import random 
import networkx as nx
from sklearn.cluster import KMeans
from scipy.spatial import cKDTree

from config import main_config


import os
import sys
sys.path.append( os.path.join(os.path.split(__file__)[0],'..','..','..'))  # Include subfolders

from helpfunctions import checkCandidateBetterThanBest

from objects.activity import Activity
from config.construction_config import *
from datageneration.distance_matrix import *
from heuristic.improvement.operator.insertor import Insertor
from parameters import T_ij

#TODO: Finne ut hva operator funksjonene skal returnere 
class RepairOperators:
    def __init__(self, alns):
        self.destruction_degree = alns.destruction_degree # TODO: Skal vi ha dette?
        self.constructor = alns.constructor

        self.count = 0 


    #TODO: Skal vi rullere på hvilke funksjoner den gjør først? Det burde vel også vært i ALNS funksjonaliteten 
    def greedy_repair(self, destroyed_route_plan, current_iteration, total_iterations):
        repaired_route_plan = copy.deepcopy(destroyed_route_plan)
        
        repaired_route_plan = self.illegal_activity_repair(repaired_route_plan)

        repaired_route_plan = self.illegal_visit_repair(repaired_route_plan)
        
        repaired_route_plan = self.illegal_treatment_repair(repaired_route_plan)   

        repaired_route_plan = self.illegal_patient_repair(repaired_route_plan)   
  
        descendingUtilityNotAllocatedPatientsDict =  {patient: self.constructor.patients_df.loc[patient, 'utility'] for patient in repaired_route_plan.notAllocatedPatients}
        descendingUtilityNotAllocatedPatients = sorted(descendingUtilityNotAllocatedPatientsDict, key=descendingUtilityNotAllocatedPatientsDict.get)
        
        for patient in descendingUtilityNotAllocatedPatients: 
            patientInsertor = Insertor(self.constructor, repaired_route_plan, 0) #Må bestemmes hvor god visitInsertor vi skal bruke
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
    
    def random_repair(self, destroyed_route_plan, current_iteration, total_iterations):
        repaired_route_plan = copy.deepcopy(destroyed_route_plan)
        
        repaired_route_plan = self.illegal_activity_repair(repaired_route_plan)

        repaired_route_plan = self.illegal_visit_repair(repaired_route_plan)

        repaired_route_plan = self.illegal_treatment_repair(repaired_route_plan)   

        repaired_route_plan = self.illegal_patient_repair(repaired_route_plan)   
    
        randomNotAllocatedPatients = repaired_route_plan.notAllocatedPatients
        random.shuffle(randomNotAllocatedPatients)

        for patient in randomNotAllocatedPatients: 
            patientInsertor = Insertor(self.constructor, repaired_route_plan, 0) #Må bestemmes hvor god visitInsertor vi skal bruke
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

        descendingComplexityNotAllocatedPatientsDict =  {patient: self.constructor.patients_df.loc[patient, 'p_complexity'] for patient in repaired_route_plan.notAllocatedPatients}
        descendingComplexityNotAllocatedPatients = sorted(descendingComplexityNotAllocatedPatientsDict, key=descendingComplexityNotAllocatedPatientsDict.get)
        
        for patient in descendingComplexityNotAllocatedPatients: 
            patientInsertor = Insertor(self.constructor, repaired_route_plan, 0) #Må bestemmes hvor god visitInsertor vi skal bruke
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

        descendingUtilityNotAllocatedPatientsDict =  {patient: self.constructor.patients_df.loc[patient, 'utility'] for patient in repaired_route_plan.notAllocatedPatients}
        descendingUtilityNotAllocatedPatients = sorted(descendingUtilityNotAllocatedPatientsDict, key=descendingUtilityNotAllocatedPatientsDict.get)
        

        '''
        Ønsker å hente ut den beste repair løsningen, så vil
        '''
        best_repaired_route_plan_with_k_regret = copy.deepcopy(repaired_route_plan)
        best_repaired_route_plan_with_k_regret.updateObjective(current_iteration, total_iterations)
        for k in range(1, main_config.k): 
            repaired_route_plan_with_k_regret = copy.deepcopy(repaired_route_plan)

            for patient in descendingUtilityNotAllocatedPatients[k:]: 
                patientInsertor = Insertor(self.constructor, repaired_route_plan_with_k_regret, 1) #Må bestemmes hvor god visitInsertor vi skal bruke
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
            activity = Activity(self.constructor.activities_df, activityID)

            #BEG: Jeg tror egentlig ikke vi trenger den som er under her 
            repaired_route_plan.updateActivityBasedOnRoutePlanOnDay(activity, day)
            status = repaired_route_plan.addActivityOnDay(activity,day)
            
            #Alternativ 1 
            if status == True: 
                
                #Steg 1 - Slette i illegal listene 
                del repaired_route_plan.illegalNotAllocatedActivitiesWithPossibleDays[activityID]
                
                for i in range(self.constructor.visit_df.shape[0]):
                    visit = self.constructor.visit_df.index[i] 
                    if activityID in self.constructor.visit_df.loc[visit, 'activitiesIds']: 
                        break

                #Steg 2 - Oppdater allokert dictionariene                
                repaired_route_plan.visits[visit].append(activityID) 
        
        #Ingen alternativ 2 
        return repaired_route_plan

  
    def illegal_visit_repair(self, repaired_route_plan): 
        illegal_visit_iteration_list = list(repaired_route_plan.illegalNotAllocatedVisitsWithPossibleDays.keys())
        for visit in illegal_visit_iteration_list:  
            visitInsertor = Insertor(self.constructor, repaired_route_plan, 0) #Må bestemmes hvor god visitInsertor vi skal bruke
            old_route_plan = copy.deepcopy(repaired_route_plan)
            status = visitInsertor.insertVisitOnDay(visit, repaired_route_plan.illegalNotAllocatedVisitsWithPossibleDays[visit])
            
            #Alternativ 1 
            if status == True: 
                repaired_route_plan = visitInsertor.route_plan
                
                #Steg 1 - Slette i illegal listene 
                del repaired_route_plan.illegalNotAllocatedVisitsWithPossibleDays[visit]

                #Legger til visitet på treatmenten. Vet at treatmenten ligger inne, for hvis ikke så ville ikke visitet vært illegal 
                for i in range(self.constructor.treatment_df.shape[0]):
                    treatment = self.constructor.treatment_df.index[i] 
                    if visit in self.constructor.treatment_df.loc[treatment, 'visitsIds']: 
                        break

                #Steg 2 - Oppdater allokert dictionariene 
                repaired_route_plan.treatments[treatment].append(visit) 
                #Legge til visit og activities som hører til treatmentet 
                repaired_route_plan.visits[visit] = self.constructor.visit_df.loc[visit, 'activitiesIds']

            #Alternativ 2 - Setter tilbake ruteplanen, dersom ingen insertion 
            else: 
                repaired_route_plan = copy.deepcopy(old_route_plan)
        return repaired_route_plan
    
    def illegal_treatment_repair(self, repaired_route_plan): 
        for treatment in repaired_route_plan.illegalNotAllocatedTreatments:  
            treatmentInsertor = Insertor(self.constructor, repaired_route_plan, 0) #Må bestemmes hvor god visitInsertor vi skal bruke
            old_route_plan = copy.deepcopy(repaired_route_plan)
            status = treatmentInsertor.insert_treatment(treatment)
            
            #Alternativ 1
            if status == True: 
                repaired_route_plan = treatmentInsertor.route_plan

                #Steg 1 - Slette i illegal listene  
                repaired_route_plan.illegalNotAllocatedTreatments.remove(treatment)
                
                #Legger til treatmenten på pasienten. Vet at pasienten allerede ligger inne, for hvis ikke ville ikke treatmenten i utgnaspunktet vært illegal 
                for i in range(self.constructor.patients_df.shape[0]):
                    patient = self.constructor.patients_df.index[i] 
                    if treatment in self.constructor.patients_df.loc[patient, 'treatmentsIds']: 
                        break

                #Steg 2 - Oppdater allokert dictionariene 
                repaired_route_plan.allocatedPatients[patient].append(treatment)
                #Legge til visit og activities som hører til treatmentet 
                repaired_route_plan.treatments[treatment] = self.constructor.treatment_df.loc[treatment, 'visitsIds']
                for visit in repaired_route_plan.treatments[treatment]: 
                    repaired_route_plan.visits[visit] = self.constructor.visit_df.loc[visit, 'activitiesIds'] 
            #Alternativ 2       
            else:
                repaired_route_plan = copy.deepcopy(old_route_plan)

        return repaired_route_plan

    def illegal_patient_repair(self, repaired_route_plan): 
         
        for patient in repaired_route_plan.illegalNotAllocatedPatients:  
            patientInsertor = Insertor(self.constructor, repaired_route_plan, 0) #Må bestemmes hvor god visitInsertor vi skal bruke
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
        
      
