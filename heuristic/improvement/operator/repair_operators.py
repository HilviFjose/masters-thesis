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
        descendingUtilityNotAllocatedPatients = sorted(descendingUtilityNotAllocatedPatientsDict, key=descendingUtilityNotAllocatedPatientsDict.get, reverse = True)

        for patient in descendingUtilityNotAllocatedPatients: 
            patientInsertor = Insertor(self.constructor, repaired_route_plan, 1) #Må bestemmes hvor god visitInsertor vi skal bruke
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
            patientInsertor = Insertor(self.constructor, repaired_route_plan, 1) #Må bestemmes hvor god visitInsertor vi skal bruke
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
        descendingComplexityNotAllocatedPatients = sorted(descendingComplexityNotAllocatedPatientsDict, key=descendingComplexityNotAllocatedPatientsDict.get, reverse=True)
        
        for patient in descendingComplexityNotAllocatedPatients: 
            patientInsertor = Insertor(self.constructor, repaired_route_plan, 1) #Må bestemmes hvor god visitInsertor vi skal bruke
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

        #TODO: Avgjøre om vi skal ha med sorteringen. Kan gjøre det vanskeligere 
        activities_df = pd.DataFrame(list(activityIterationDict.items()), columns=['activity', 'days'])

        # Assuming self.constructor.activities_df is your DataFrame with complexities
        # Ensure 'activity' is the index for vectorized access
        complexities_df = self.constructor.activities_df[['a_complexity']]

        # Join the two DataFrames on activity
        joined_df = activities_df.join(complexities_df, on='activity')

        # Sort the DataFrame by complexity
        sorted_df = joined_df.sort_values(by='a_complexity', ascending=False )

        # Convert back to a dictionary if needed
        sorted_activities_dict = pd.Series(sorted_df.days.values,index=sorted_df.activity).to_dict()

        for activityID, day in sorted_activities_dict.items():
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

        #TODO: Avgjøre om vi skal ha med sorteringen. Kan gjøre det vanskeligere 
        visits_df = pd.DataFrame(list(repaired_route_plan.illegalNotAllocatedVisitsWithPossibleDays.items()), columns=['visit', 'days'])

        # Assuming self.constructor.activities_df is your DataFrame with complexities
        # Ensure 'activity' is the index for vectorized access
        complexities_df = self.constructor.visit_df[['v_complexity']]

        # Join the two DataFrames on activity
        joined_df = visits_df.join(complexities_df, on='visit')

        # Sort the DataFrame by complexity
        sorted_df = joined_df.sort_values(by='v_complexity', ascending=False )

        # Convert back to a dictionary if needed
        sorted_visit_dict = pd.Series(sorted_df.days.values,index=sorted_df.visit).to_dict()

        for visit in sorted_visit_dict.keys():  
        #for visit in illegal_visit_iteration_list:  
            visitInsertor = Insertor(self.constructor, repaired_route_plan, 1) #Må bestemmes hvor god visitInsertor vi skal bruke
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

        #TODO: Avgjøre om vi skal ha med sorteringen. Kan gjøre det vanskeligere 
        # Convert your list to a DataFrame
        treatments_df = pd.DataFrame(repaired_route_plan.illegalNotAllocatedTreatments, columns=['treatment'])

        # Assuming self.constructor.activities_df is your DataFrame with complexities
        # Ensure 'activity' is the index for vectorized access
        complexities_df = self.constructor.treatment_df[['t_complexity']]

        # Join the two DataFrames on activity
        joined_df = treatments_df.join(complexities_df, on='treatment')

        # Sort the DataFrame by complexity, highest complexity first
        sorted_df = joined_df.sort_values(by='t_complexity', ascending=False)

        # Extract the sorted list of activity IDs
        sorted_treatment_list = sorted_df['treatment'].tolist()   

        for treatment in sorted_treatment_list:
        #for treatment in repaired_route_plan.illegalNotAllocatedTreatments:  
            treatmentInsertor = Insertor(self.constructor, repaired_route_plan, 1) #Må bestemmes hvor god visitInsertor vi skal bruke
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

        patients_df = pd.DataFrame(repaired_route_plan.illegalNotAllocatedPatients, columns=['patient'])

        # Assuming self.constructor.activities_df is your DataFrame with complexities
        # Ensure 'activity' is the index for vectorized access
        complexities_df = self.constructor.patients_df[['p_complexity']]

        # Join the two DataFrames on activity
        joined_df = patients_df.join(complexities_df, on='patient')

        # Sort the DataFrame by complexity, highest complexity first
        sorted_df = joined_df.sort_values(by='p_complexity', ascending=False)

        # Extract the sorted list of activity IDs
        sorted_patient_list = sorted_df['patient'].tolist() 
         
        for patient in sorted_patient_list: 
        #for patient in repaired_route_plan.illegalNotAllocatedPatients:  
            patientInsertor = Insertor(self.constructor, repaired_route_plan, 1) #Må bestemmes hvor god visitInsertor vi skal bruke
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
        
      
