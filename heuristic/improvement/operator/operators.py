import pandas as pd
import copy
import math
import numpy.random as rnd 
import random 

import os
import sys
sys.path.append( os.path.join(os.path.split(__file__)[0],'..','..','..'))  # Include subfolders

from helpfunctions import checkCandidateBetterThanBest
from objects.distances import *
from config.construction_config import *
from heuristic.improvement.operator.insertor import Insertor

class Operators:
    def __init__(self, alns):
        self.destruction_degree = alns.destruction_degree # TODO: Skal vi ha dette?
        self.constructor = alns.constructor

        self.count = 0 

    # Uses destruction degree to set max cap for removal
    def activities_to_remove(self, activities_remove):
        return activities_remove
    
#---------- REMOVE OPERATORS ----------
    """
   
    def random_route_removal(self, current_route_plan):
        destroyed_route_plan = copy.deepcopy(current_route_plan)
        routes = destroyed_route_plan.routes

        if destroyed_route_plan:
            index_list = list(range(len(routes)))
            selected_index = rnd.choice(index_list)
            removed_route = routes[selected_index]
            destroyed_route_plan.remove(removed_route)
       
        removed_activities = []
        for act in removed_route:
            removed_activities.add(act)
     
        return destroyed_route_plan, removed_activities, True
    
    def worst_route_removal(self, current_route_plan):
        destroyed_route_plan = copy.deepcopy(current_route_plan)
        routes = destroyed_route_plan.routes
        worst_route = None
        current_worst_objective = current_route_plan.objective

        for route in routes:
            route_plan_holder = copy.deepcopy(current_route_plan)
            removed_route = route_plan_holder.routes.pop(route)
            objective_removed_route = route_plan_holder.objective
            
            # If current worst objective is better than candidate, then candidate is the new current worst
            if checkCandidateBetterThanCurrent(current_worst_objective, objective_removed_route):
                worst_route = removed_route
                current_worst_objective = objective_removed_route
                destroyed_route_plan = route_plan_holder
            
        removed_activities = []
        for act in worst_route:
            removed_activities.add(act)

        return destroyed_route_plan, removed_activities, True
         """
    def random_treatment_removal(self, current_route_plan):

        destroyed_route_plan = copy.deepcopy(current_route_plan)

        if self.count == 0: 
            selected_treatment = 4 
        else: 
            selected_treatment = rnd.choice(list(destroyed_route_plan.treatments.keys())) 
        removed_activities = []
        
        for visit in destroyed_route_plan.treatments[selected_treatment]:
            removed_activities += destroyed_route_plan.visits[visit]
            del destroyed_route_plan.visits[visit]

        for day in range(1, destroyed_route_plan.days +1): 
            for route in destroyed_route_plan.routes[day]: 
                for act in route.route: 
                    if act.id in removed_activities:
                        route.removeActivityID(act.id)
        
        #Har fjernet en treatment, men vet ikke om treatmenten utgjør hele pasienten 
        #Alt1 treatmentet ugjør hele pasienten i utganspunktet 
        #Alt2 Pasient har treatments både inne og i illegal
        #Alt3 Den treatmenten som velges er den siste treatmenten for en pas
        for patient, treatments in list(destroyed_route_plan.allocatedPatients.items()):
            #Finne treatments i illegalNotAllocatedTreatments som også tilhører pasienten 
            allTreatments = self.constructor.patients_df.loc[patient, 'treatmentsIds']
            illegalTreatments = []
            for allTreat in allTreatments: 
                if allTreat in destroyed_route_plan.illegalNotAllocatedTreatments: 
                    illegalTreatments.append(allTreat)

            becomes_illegal = False
            if len(illegalTreatments) == 0: 
                becomes_illegal = True 
            
            #Alt 1 Siste treatment som fjernes. Alerede ulovlig
            if treatments == [selected_treatment] and becomes_illegal == False: 
                del destroyed_route_plan.allocatedPatients[patient]
                del destroyed_route_plan.treatments[selected_treatment]
                destroyed_route_plan.notAllocatedPatients.append(patient)
                for illegalTreat in illegalTreatments: 
                    destroyed_route_plan.illegalNotAllocatedTreatments.remove(illegalTreat)
                break


            #Alt 2 Siste treatmtn som fjernes. Løsningen er lovlig 
            if treatments == [selected_treatment] and becomes_illegal == True: 
                #pasienten ligger ikke lenger inne 
                #Pasient skal puttes inn i de som ikke er allokert
                del destroyed_route_plan.allocatedPatients[patient]
                del destroyed_route_plan.treatments[selected_treatment]
                destroyed_route_plan.notAllocatedPatients.append(patient)
                break

            #Alt 3 Ikke siste treatment  
            if selected_treatment in treatments: 
                #Hvorfor fjernes ikke denne? 
                del destroyed_route_plan.treatments[selected_treatment]
                #Fjerne treatment 4 fra allocated patietns 
                destroyed_route_plan.allocatedPatients[patient].remove(selected_treatment)
                destroyed_route_plan.illegalNotAllocatedTreatments.append( selected_treatment)
                break

        destroyed_route_plan.updateObjective()
        self.count += 1 
      
        return destroyed_route_plan, removed_activities, True
    
    #Dette er også en treatment removal 
    def random_pattern_removal(self, current_route_plan):
        destroyed_route_plan = copy.deepcopy(current_route_plan)
        #Må endres når vi endrer pattern 
        selected_pattern = random.randint(1, len(patternTypes))
        removed_activities = []
        new_treatments = copy.deepcopy(destroyed_route_plan.treatments)
        for treatment in destroyed_route_plan.treatments.keys(): 
            pattern_for_treatment = self.constructor.treatment_df.loc[treatment,"patternType"]
            if pattern_for_treatment != selected_pattern: 
                continue

            for visit in destroyed_route_plan.treatments[treatment]:
                removed_activities += destroyed_route_plan.visits[visit]
                #Tar bort visitene som ligger i rute planen 
                del destroyed_route_plan.visits[visit]

            del new_treatments[treatment]

            for key, value in list(destroyed_route_plan.allocatedPatients.items()):
                if value == [treatment]:
                
                    del destroyed_route_plan.allocatedPatients[key]
                    destroyed_route_plan.notAllocatedPatients.append(key)
                    break
                if treatment in value: 
                    destroyed_route_plan.illegalNotAllocatedTreatments += value
                    break
        
        destroyed_route_plan.treatments = new_treatments

        #Fjerning av aktivitetene skjer tillutt. 
        for day in range(1, destroyed_route_plan.days +1): 
            for route in destroyed_route_plan.routes[day]: 
                for act in route.route: 
                    if act.id in removed_activities:
                        route.removeActivityID(act.id)

        
        destroyed_route_plan.updateObjective()
        return destroyed_route_plan, removed_activities, True

#---------- REPAIR OPERATORS ----------
    def greedy_repair(self, destroyed_route_plan):
        repaired_route_plan = copy.deepcopy(destroyed_route_plan)

        #Forsøker å legge til de aktivitetene vi har tatt ut ulovlig 
        insertor = Insertor(self.constructor, repaired_route_plan)
        for treatment in repaired_route_plan.illegalNotAllocatedTreatments: 
            status = insertor.insert_treatment(treatment)
            if status == True: 
                repaired_route_plan.illegalNotAllocatedTreatments.remove(treatment)

            

        #Forsøker å legge til pasienten som ikke er inne nå 
        #TODO: Denne er ikke greedy nå, pasienten emå sorteres etter hvor gode de er å ha inne
        '''
        patient_ids = repaired_route_plan.notAllocatedPatients
        filtered_df = self.constructor.patients_df[self.constructor.patients_df.keys().isin(patient_ids)]
        # Sort the filtered DataFrame by 'ColumnValue'
        sorted_filtered_df = filtered_df.sort_values(by='ColumnValue')
        # Extracting the sorted list of patient IDs
        sorted_patient_ids = sorted_filtered_df['patientId'].tolist()
        '''
        not_sorted_patients = repaired_route_plan.notAllocatedPatients
        
        unassigned_patients = self.constructor.patients_df.sort_values(by="aggUtility", ascending=False)

        sorted_patients = []
        #Iterer over hver pasient i lista. Pasienten vi ser på kalles videre pasient
        for i in range(unassigned_patients.shape[0]):
            #Henter ut raden i pasient dataframes som tilhører pasienten
            patient = unassigned_patients.index[i]
            if patient in not_sorted_patients:
                sorted_patients.append(patient)
        '''
        for patient in unassigned_patients['patientId'].tolist(): 
            if patient in not_sorted_patients: 
                sorted_patients.append(patient)
        '''
        print("sorted_patients", sorted_patients)
        insertor.insertPatients(sorted_patients)
        insertor.route_plan.updateObjective()
       
        return insertor.route_plan
    
    def random_repair(self, destroyed_route_plan):
        #Tar bort removed acktivitites, de trenger vi ikk e
        repaired_route_plan = copy.deepcopy(destroyed_route_plan)
        


        #Forsøker å legge til de aktivitetene vi har tatt ut
        treatmentInsertor = Insertor(self.constructor, repaired_route_plan)
        for treatment in repaired_route_plan.illegalNotAllocatedTreatments:  
           
            status = treatmentInsertor.insert_treatment(treatment)
      
            if status == True: 
  
                repaired_route_plan = treatmentInsertor.route_plan
                repaired_route_plan.illegalNotAllocatedTreatments.remove(treatment)
                
            
                #Må legge inn informasjonen om de treament og pasient. Må hente ut pasientenførst 
             
        
        #Iterer over hver pasient i lista. Pasienten vi ser på kalles videre pasient
                for i in range(self.constructor.patients_df.shape[0]):
                    patient = self.constructor.patients_df.index[i] 
                    if treatment in self.constructor.patients_df.loc[patient, 'treatmentsIds']: 
                        break
                repaired_route_plan.allocatedPatients[patient].append(treatment) 
                
    
        #TODO: Nå legger den ikke til disse 
        patientInsertor = Insertor(self.constructor, repaired_route_plan)
        repaired_route_plan = patientInsertor.insertPatients(repaired_route_plan.notAllocatedPatients)
        repaired_route_plan.updateObjective()
      
        return repaired_route_plan
    

    #TODO: Burde se på en operator som bytter å mye som mulig mellom to ansatte 