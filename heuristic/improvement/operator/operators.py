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

  
        print("FØR DESTROY")

        print("illegalNotAllocatedTreatments", destroyed_route_plan.illegalNotAllocatedTreatments) 
        print("notAllocatedPatients", destroyed_route_plan.notAllocatedPatients)
        print("    ")
        print("allocatedPatients", destroyed_route_plan.allocatedPatients)
        print("    ")
        print("treatments", destroyed_route_plan.treatments)

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

        '''
        Oppdate feil. Allocated patients skal ikke inneholde treatment 4, bare tratment 3 
        Treatment 4 skal hellerikke ligge i treatments 
        '''

        destroyed_route_plan.updateObjective()
        self.count += 1 
        #print("treatment", destroyed_route_plan.treatments[selected_treatment],"før",destroyed_route_plan.treatments)
        #del destroyed_route_plan.treatments[selected_treatment]
        #print("etter",destroyed_route_plan.treatments)
        print(" ")
        print("ETTER DESTROY REMOVED TREATMENT ", selected_treatment)
        
        print("illegalNotAllocatedTreatments", destroyed_route_plan.illegalNotAllocatedTreatments) 
        print("notAllocatedPatients", destroyed_route_plan.notAllocatedPatients)
        print("    ")
        print("allocatedPatients", destroyed_route_plan.allocatedPatients)
        print("    ")
        print("treatments", destroyed_route_plan.treatments)
        return destroyed_route_plan, removed_activities, True
    
    

#---------- REPAIR OPERATORS ----------
    def greedy_repair(self, destroyed_route_plan):
        #Tar bort removed acktivitites, de trenger vi ikk e
        repaired_route_plan = copy.deepcopy(destroyed_route_plan)
        
        '''
        Nå henter vi repaired route plan fra insertoren, så den endringen som vi har gjort selv 
        i denne funksjonen blir ikkke inkludert 

        Det må returneres en ruteplan, for inserter 
        '''

        #Forsøker å legge til de aktivitetene vi har tatt ut
        treatmentInsertor = Insertor(self.constructor, repaired_route_plan)
        for treatment in repaired_route_plan.illegalNotAllocatedTreatments:  
           
            status = treatmentInsertor.insert_treatment(treatment)
            if treatment == 4: 
                print("status for å legge til treatment ", treatment, "får status ", status)
            if status == True: 
                if treatment == 4:
                    print("illegalNotAllocatedTreatments FØR ", repaired_route_plan.illegalNotAllocatedTreatments)
                repaired_route_plan = treatmentInsertor.route_plan
                repaired_route_plan.illegalNotAllocatedTreatments.remove(treatment)
                if treatment == 4:
                    print("illegalNotAllocatedTreatments ETTER ", repaired_route_plan.illegalNotAllocatedTreatments)
            
                #Må legge inn informasjonen om de treament og pasient. Må hente ut pasientenførst 
             
        
        #Iterer over hver pasient i lista. Pasienten vi ser på kalles videre pasient
                for i in range(self.constructor.patients_df.shape[0]):
                    patient = self.constructor.patients_df.index[i] 
                    if treatment in self.constructor.patients_df.loc[patient, 'treatmentsIds']: 
                        break
                repaired_route_plan.allocatedPatients[patient].append(treatment) 
                

        #Den får til å legge det på treatment nivå, men ikke på illegal og allocatedPatients 

                


    
        #TODO: Nå legger den ikke til disse 
        patientInsertor = Insertor(self.constructor, repaired_route_plan)
        repaired_route_plan = patientInsertor.insertPatients(repaired_route_plan.notAllocatedPatients)
        repaired_route_plan.updateObjective()
        '''
        route_plan, new_objective = self.repair_generator.generate_insertions(
            route_plan=route_plan, activity=activity, rid=rid, infeasible_set=infeasible_set, initial_route_plan=current_route_plan, index_removed=index_removal, objectives=0)

        # update current objective
        current_objective = new_objective
        '''

        '''
        Konseptet: 
        Vi har ulike lister med aktiviteter 
        '''
        return repaired_route_plan
    

