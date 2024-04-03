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
    def greedy_repair(self, destroyed_route_plan):
        #TODO: Her burde funskjonene inni kalles fra andre funskjoner 
        repaired_route_plan = copy.deepcopy(destroyed_route_plan)
        
        #ACTIVITY ILLEGAL (forsøker legge inn illegal activites )
        self.illegal_activity_repair(repaired_route_plan)

        #VISIT ILLEGAL (forsøker legge inn illegal visits )
        self.illegal_visit_repair(repaired_route_plan)

        #TREATMENT ILLEGAL (forsøker legge inn illegal treatments )
        self.illegal_treatment_repair(repaired_route_plan)      
    
        #LEGGER TIL PASIENTER 
        patientInsertor = Insertor(self.constructor, repaired_route_plan)
        #TODO: Sortere slik at den setter inn de beste først. Den er ikkke grådig nå vel? 
        descendingUtilityNotAllocatedPatientsDict =  {patient: self.constructor.patients_df.loc[patient, 'utility'] for patient in repaired_route_plan.notAllocatedPatients}
        descendingUtilityNotAllocatedPatients = sorted(descendingUtilityNotAllocatedPatientsDict, key=descendingUtilityNotAllocatedPatientsDict.get)
        
        for patient in descendingUtilityNotAllocatedPatients: 
            status = patientInsertor.insert_patient(patient)
            
            if status == True: 
                repaired_route_plan = patientInsertor.route_plan
                self.updateAllocationAfterPatientInsertor(repaired_route_plan, patient)
        
        
        repaired_route_plan.updateObjective()
      
        return repaired_route_plan
    
    def random_repair(self, destroyed_route_plan):
        #Tar bort removed acktivitites, de trenger vi ikk e
        repaired_route_plan = copy.deepcopy(destroyed_route_plan)
        
        #TODO: Skal den ha random elementer også i innsettingen av det som er ulovlig 
        #ACTIVITY ILLEGAL (forsøker legge inn illegal activites )
        self.illegal_activity_repair(repaired_route_plan)

        #VISIT ILLEGAL (forsøker legge inn illegal visits )
        self.illegal_visit_repair(repaired_route_plan)

        #TREATMENT ILLEGAL (forsøker legge inn illegal treatments )
        self.illegal_treatment_repair(repaired_route_plan)      
    
        #LEGGER TIL PASIENTER I RANDOM REKKEFØLGE 
        patientInsertor = Insertor(self.constructor, repaired_route_plan)
        randomNotAllocatedPatients = repaired_route_plan.notAllocatedPatients
        random.shuffle(randomNotAllocatedPatients)

        for patient in randomNotAllocatedPatients: 
            status = patientInsertor.insert_patient(patient)
        
            if status == True: 
                repaired_route_plan = patientInsertor.route_plan
                self.updateAllocationAfterPatientInsertor(repaired_route_plan, patient)

    
        repaired_route_plan.updateObjective()
      
        return repaired_route_plan


    def complexity_repair(self, destroyed_route_plan):
        #Tar bort removed acktivitites, de trenger vi ikk e
        repaired_route_plan = copy.deepcopy(destroyed_route_plan)

        #ACTIVITY ILLEGAL (forsøker legge inn illegal activites )
        self.illegal_activity_repair(repaired_route_plan)

        #VISIT ILLEGAL (forsøker legge inn illegal visits )
        self.illegal_visit_repair(repaired_route_plan)

        #TREATMENT ILLEGAL (forsøker legge inn illegal treatments )
        self.illegal_treatment_repair(repaired_route_plan)  

        #LEGGER TIL PASIENTER I RANDOM REKKEFØLGE 
        patientInsertor = Insertor(self.constructor, repaired_route_plan)
        descendingComplexityNotAllocatedPatientsDict =  {patient: self.constructor.patients_df.loc[patient, 'p_complexity'] for patient in repaired_route_plan.notAllocatedPatients}
        descendingComplexityNotAllocatedPatients = sorted(descendingComplexityNotAllocatedPatientsDict, key=descendingComplexityNotAllocatedPatientsDict.get)

        for patient in descendingComplexityNotAllocatedPatients: 
            status = patientInsertor.insert_patient(patient)
            
            if status == True: 
                repaired_route_plan = patientInsertor.route_plan
                self.updateAllocationAfterPatientInsertor(repaired_route_plan, patient)


        repaired_route_plan.updateObjective()
      
        return repaired_route_plan
    

    #TODO: Burde se på en operator som bytter å mye som mulig mellom to ansatte. Hvorfor det? 

# ------------ HELP FUNCTIONS ------------

    def illegal_activity_repair(self, repaired_route_plan): 
        activityIterationDict = copy.copy(repaired_route_plan.illegalNotAllocatedActivitiesWithPossibleDays)
        for activityID, day in activityIterationDict.items():
            activity = Activity(self.constructor.activities_df, activityID)
            repaired_route_plan.updateActivityBasedOnRoutePlanOnDay(activity, day)
            status = repaired_route_plan.addActivityOnDay(activity,day)
            if status == True: 
                del repaired_route_plan.illegalNotAllocatedActivitiesWithPossibleDays[activityID]

                #Legger til aktiviteten på visitet
                for i in range(self.constructor.visit_df.shape[0]):
                    visit = self.constructor.visit_df.index[i] 
                    if activityID in self.constructor.visit_df.loc[visit, 'activitiesIds']: 
                        break
                repaired_route_plan.visits[visit].append(activityID) 

  
    def illegal_visit_repair(self, repaired_route_plan): 
        #TODO: Her burde presedensen også sjekkes, usikker på om riktig nå 
        visitInsertor = Insertor(self.constructor, repaired_route_plan)
        illegal_visit_iteration_list = list(repaired_route_plan.illegalNotAllocatedVisitsWithPossibleDays.keys())
        for visit in illegal_visit_iteration_list:  
            status = visitInsertor.insert_visit_on_day(visit, repaired_route_plan.illegalNotAllocatedVisitsWithPossibleDays[visit])
            if status == True: 
                repaired_route_plan = visitInsertor.route_plan
                del repaired_route_plan.illegalNotAllocatedVisitsWithPossibleDays[visit]

                #Legger til visitet på treatmenten. Vet at treatmenten ligger inne, for hvis ikke så ville ikke visitet vært illegal 
                for i in range(self.constructor.treatment_df.shape[0]):
                    treatment = self.constructor.treatment_df.index[i] 
                    if visit in self.constructor.treatment_df.loc[treatment, 'visitsIds']: 
                        break
                repaired_route_plan.treatments[treatment].append(visit) 

                #Legge til visit og activities som hører til treatmentet 
                repaired_route_plan.visits[visit] = self.constructor.visit_df.loc[visit, 'activitiesIds']
    
    def illegal_treatment_repair(self, repaired_route_plan): 
        treatmentInsertor = Insertor(self.constructor, repaired_route_plan)
        for treatment in repaired_route_plan.illegalNotAllocatedTreatments:  
            status = treatmentInsertor.insert_treatment(treatment)
            if status == True: 
                repaired_route_plan = treatmentInsertor.route_plan

                #Fjerner treatmenten fra illegal Treatments 
                repaired_route_plan.illegalNotAllocatedTreatments.remove(treatment)
                
                #Legger til treatmenten på pasienten. Vet at pasienten allerede ligger inne, for hvis ikke ville ikke treatmenten i utgnaspunktet vært illegal 
                for i in range(self.constructor.patients_df.shape[0]):
                    patient = self.constructor.patients_df.index[i] 
                    if treatment in self.constructor.patients_df.loc[patient, 'treatmentsIds']: 
                        break
                repaired_route_plan.allocatedPatients[patient].append(treatment)

                #Legge til visit og activities som hører til treatmentet 
                repaired_route_plan.treatments[treatment] = self.constructor.treatment_df.loc[treatment, 'visitsIds']
                for visit in [item for sublist in repaired_route_plan.treatments.values() for item in sublist]: 
                    repaired_route_plan.visits[visit] = self.constructor.visit_df.loc[visit, 'activitiesIds'] 
    
    
    def updateAllocationAfterPatientInsertor(self, route_plan, patient): 
        #Oppdaterer allokerings dictionariene 
        route_plan.allocatedPatients[patient] = self.constructor.patients_df.loc[patient, 'treatmentsIds']
        for treatment in [item for sublist in route_plan.allocatedPatients.values() for item in sublist]: 
            route_plan.treatments[treatment] = self.constructor.treatment_df.loc[treatment, 'visitsIds']
        for visit in [item for sublist in route_plan.treatments.values() for item in sublist]: 
            route_plan.visits[visit] = self.constructor.visit_df.loc[visit, 'activitiesIds']

        #Fjerner pasienten fra ikkeAllokert listen 
        if patient in route_plan.notAllocatedPatients: 
            route_plan.notAllocatedPatients.remove(patient)