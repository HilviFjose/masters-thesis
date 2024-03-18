import pandas as pd
import copy
import math
import numpy.random as rnd 
import random 
import networkx as nx

import os
import sys
sys.path.append( os.path.join(os.path.split(__file__)[0],'..','..','..'))  # Include subfolders

from helpfunctions import checkCandidateBetterThanBest
from config.construction_config import *
from datageneration.distance_matrix import *
from heuristic.improvement.operator.insertor import Insertor

#TODO: Finne ut hva operator funksjonene skal returnere 
class Operators:
    def __init__(self, alns):
        self.destruction_degree = alns.destruction_degree # TODO: Skal vi ha dette?
        self.constructor = alns.constructor

        self.count = 0 


    # Uses destruction degree to set max cap for removal
    #TODO: Hva gjør denne?  
    def activities_to_remove(self, activities_remove):
        return activities_remove
    
#---------- REMOVE OPERATORS ----------
 
    
    def worst_deviation_patient_removal(self, current_route_plan):
        lowest_patient_contribute = 1000
        selected_patient = None 
        for patient in list(current_route_plan.allocatedPatients.keys()): 
            if self.constructor.patients_df.loc[patient, 'aggUtility'] < lowest_patient_contribute: 
                selected_patient = patient

        return self.patient_removal(selected_patient, current_route_plan)
    
    def random_patient_removal(self, current_route_plan):
        selected_patient = rnd.choice(list(current_route_plan.allocatedPatients.keys())) 
        return self.patient_removal(selected_patient, current_route_plan)
    

    def patient_removal(self, selected_patient, route_plan): 
        destroyed_route_plan = copy.deepcopy(route_plan)
        
        removed_activities = []
        
        #Her fjernes aktivitetne fra visits og treatments dict
        for treatment in destroyed_route_plan.allocatedPatients[selected_patient]: 
            print('treat', treatment)
            for visit in destroyed_route_plan.treatments[treatment]:
                removed_activities += destroyed_route_plan.visits[visit]
                del destroyed_route_plan.visits[visit]
            del destroyed_route_plan.treatments[treatment]
        
        #Her fjernes aktivitetne fra selve ruten 
        self.remove_activites_from_route_plan(removed_activities, destroyed_route_plan)

        #Ta bort fra allocatedpatients dict
        del destroyed_route_plan.allocatedPatients[selected_patient]
        #legge til i not allocated listen 
        destroyed_route_plan.notAllocatedPatients.append(selected_patient)

        return destroyed_route_plan, removed_activities, True

    def remove_activites_from_route_plan(self, activities, route_plan):
        for day in range(1, route_plan.days +1): 
            for route in route_plan.routes[day]: 
                for act in route.route: 
                    if act.id in activities:
                        route.removeActivityID(act.id)

    #TODO: Finne ut hvordan vi skal evaluere hvilken treatment som er verst, nå er det bare på hovedobjektiv 
    def worst_deviation_treatment_removal(self, current_route_plan):
        lowest_treatment_contribute = 1000
        selected_treatment = None 
        for treatment in list(current_route_plan.treatments.keys()): 
            treatment_contribute = 0 
            for visit in current_route_plan.treatments[treatment]:
                for activity in current_route_plan.visits[visit]:
                    treatment_contribute += self.constructor.activities_df.loc[activity, 'utility']
            if treatment_contribute < lowest_treatment_contribute: 
                selected_treatment = treatment

        return self.treatment_removal(selected_treatment, current_route_plan)
    
    
    def random_treatment_removal(self, current_route_plan):
        selected_treatment = rnd.choice(list(current_route_plan.treatments.keys())) 
        return self.treatment_removal(selected_treatment, current_route_plan)

    #TODO: Denne kan skrives ned, mange like kodelinjer
    def treatment_removal(self, selected_treatment, route_plan):
        destroyed_route_plan = copy.deepcopy(route_plan)
        removed_activities = []
        
        for visit in destroyed_route_plan.treatments[selected_treatment]:
            removed_activities += destroyed_route_plan.visits[visit]
            del destroyed_route_plan.visits[visit]

        self.remove_activites_from_route_plan(removed_activities, destroyed_route_plan)
        
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
    
    def random_visit_removal(self, current_route_plan):
        selected_visit = rnd.choice(list(current_route_plan.visits.keys())) 
        return self.visit_removal(selected_visit, current_route_plan)
    
    
    def worst_deviation_visit_removal(self, current_route_plan):
        lowest_visit_utility_contribute = 1000 
        highest_visit_skilldiff_contribute = 0
        selected_visit = None 
        for visit in list(current_route_plan.visits.keys()): 
            visit_utility_contribute = 0 
            visit_skilldiff_contribute = 0
            for activity in current_route_plan.visits[visit]:
                    visit_utility_contribute += self.constructor.activities_df.loc[activity, 'utility']
                    visit_skilldiff_contribute += current_route_plan.getRouteSkillLevForActivityID(activity) - self.constructor.activities_df.loc[activity, 'skillRequirement']
            if visit_utility_contribute < lowest_visit_utility_contribute or (
                visit_utility_contribute == lowest_visit_utility_contribute and visit_skilldiff_contribute > highest_visit_skilldiff_contribute): 
         
                selected_visit = visit
          

        return self.visit_removal(selected_visit, current_route_plan)

    
    '''
    IllegalListene: Inneholder treaments, visits eller aktiviteter som ikke er allokert  

    AllocatedDict: Skal inneholde pasient, tratment eller visit, hvis det er hele eller deler som er allokert 
    '''
    def visit_removal(self, selected_visit, route_plan):

        

        destroyed_route_plan = copy.deepcopy(route_plan)
        removed_activities = [] 

        #Hente ut aktivitene som skal fjernes 
        removed_activities += destroyed_route_plan.visits[selected_visit]

        #Vi vet at vi bare har valgt ett visit, så dagen vil være en 
        original_day = None
        for day in range(1, destroyed_route_plan.days +1): 
            for route in destroyed_route_plan.routes[day]: 
                for act in route.route: 
                    if act.id in removed_activities:
                        route.removeActivityID(act.id)
                        original_day = day
        
     
            #To alternativer
                    #1) Selected visit er en del av et visit der flere treatmentets visit ligger inne på sykehuset. -> [orgin_day]. Visit skal inn i illegalVisit
                    #2) Selected visit er det siste visitet i en treatment som er allokert ut. -> Treatmentet skal inn i illegalTreat. 
                    #3) Select visit er siste som lå på treatment, og siste treatment som lå på pasient -> Pasient ut av illegal og inn i not Allocated

            #TODO: Finne ut om det har noe å si at det er den første aktivtene som blir flyttet ut 

        
        
        last_visit_in_treatment = False
        treatment_for_visit = None 
        #Ønsker å finne treatmenten 
        for treatment, visits in list(destroyed_route_plan.treatments.items()):
            #Finne treatments i illegalNotAllocatedTreatments som også tilhører pasienten 
            if visits == [selected_visit]: 
                last_visit_in_treatment = True 
            if selected_visit in visits: 
                treatment_for_visit = treatment
                break


        #ALTERNATIV 1 
        if last_visit_in_treatment == False: 
            del destroyed_route_plan.visits[selected_visit]
            destroyed_route_plan.illegalNotAllocatedVisitsWithPossibleDays[selected_visit] = original_day
            destroyed_route_plan.treatments[treatment_for_visit].remove(selected_visit)
            
            return destroyed_route_plan, removed_activities, True
    
        #ALTERNATIV 2 
        del destroyed_route_plan.visits[selected_visit]
        #Ta bort treatmentet
        del destroyed_route_plan.treatments[treatment_for_visit]
        #Legger til treatmentet i illegal 
        last_treatment_for_patient = False
        patient_for_treatment = None
        for patient, treatments in list(destroyed_route_plan.allocatedPatients.items()):
            if treatments == [treatment_for_visit]:
                last_treatment_for_patient = True 
            if treatment_for_visit in treatments: 
                patient_for_treatment = patient
                break
        
        #Dersom pasienten ikke er den samme
        if last_treatment_for_patient == True: 
            del destroyed_route_plan.allocatedPatients[patient_for_treatment]
            destroyed_route_plan.notAllocatedPatients.append(patient_for_treatment)
        
        if last_treatment_for_patient == False: 
            destroyed_route_plan.illegalNotAllocatedTreatments.append(treatment_for_visit)

            
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

    # ----- Guro start -----    
    def kruskalAlgorithm(self, df):
        travel_time_matrix = travel_matrix_without_rush(df)
        G = nx.Graph()
        n = len(travel_time_matrix)  # Antall noder
        for i in range(n):
            for j in range(i + 1, n):
                # Legg til en kant mellom hver node med vekt lik reisetiden
                G.add_edge(i, j, weight=travel_time_matrix[i][j])

        # Generer MST ved hjelp av Kruskal's algoritme
        mst = nx.minimum_spanning_tree(G, algorithm='kruskal')

        # Finn og fjern den lengste kanten
        edges = list(mst.edges(data=True))
        longest_edge = max(edges, key=lambda x: x[2]['weight'])
        mst.remove_edge(longest_edge[0], longest_edge[1])

        # MST er nå delt i to deler, og du kan identifisere komponentene (dvs. de to gruppene av IDer)
        components = list(nx.connected_components(mst))
        shortest_component = min(components, key=len)
        longest_component = max(components,key=len)

        # Kart for å mappe indekser tilbake til IDer
        index_to_id = {index: id for index, id in enumerate(df.index)}

        # Konverter indekser til IDer
        shortest_ids = [index_to_id[index] for index in shortest_component]
        longest_ids = [index_to_id[index] for index in longest_component]

        return shortest_ids, longest_ids

    def cluster_distance_patients_removal(self, current_route_plan):
        allocatedPatientsIds = list(current_route_plan.allocatedPatients.keys())
        print('allocated patients', allocatedPatientsIds)

        df_selected_patients =  self.constructor.patients_df.loc[allocatedPatientsIds]

        selected_patients = self.kruskalAlgorithm(df_selected_patients)[0]  #Selecting the shortest part of the mst
        print('selected patients', selected_patients)
        destroyed_route_plan = copy.deepcopy(current_route_plan)
        for patientID in selected_patients: 
            print('before',destroyed_route_plan.allocatedPatients)
            destroyed_route_plan = self.patient_removal(patientID, destroyed_route_plan)[0]
            print('after',destroyed_route_plan.allocatedPatients)

        return destroyed_route_plan, None, True


    def cluster_distance_activities_removal(self, current_route_plan):
        longest_travel_time = 0
        activities_in_longest_route = []
        for day, routes in current_route_plan.routes.items():
            for route in routes:  
                if route.travel_time > longest_travel_time:
                    longest_travel_time = route.travel_time
                    activities_in_longest_route = [activity.id for activity in route.route]
            
        df_selected_activities = self.constructor.activities_df.loc[activities_in_longest_route]

        selected_activities = self.kruskalAlgorithm(df_selected_activities)[1] #Selecting the longest part of the mst
        print('selected activities ', selected_activities)
        destroyed_route_plan = copy.deepcopy(current_route_plan)
        self.remove_activites_from_route_plan(selected_activities, destroyed_route_plan)

        return destroyed_route_plan, selected_activities, True
    
    
    # ----- Guro slutt -----

#---------- REPAIR OPERATORS ----------
    def greedy_repair(self, destroyed_route_plan):
        #TODO: Her burde funskjonene inni kalles fra andre funskjoner 
        repaired_route_plan = copy.deepcopy(destroyed_route_plan)
        

    
        #VISIT ILLEGAL 
        #TODO: Her burde presedensen også sjekkes, 
        #For jeg vet ikke hvordan den oppdatere seg basert på det som er i ruten 
        visitInsertor = Insertor(self.constructor, repaired_route_plan)
        for visit in list(repaired_route_plan.illegalNotAllocatedVisitsWithPossibleDays.keys()):  
            status = visitInsertor.insert_visit_on_day(visit, repaired_route_plan.illegalNotAllocatedVisitsWithPossibleDays[visit])
            if status == True: 
   
                repaired_route_plan = visitInsertor.route_plan
                del repaired_route_plan.illegalNotAllocatedVisitsWithPossibleDays[visit]

                #Legger til visitet på treatmenten 
                for i in range(self.constructor.treatment_df.shape[0]):
                    treatment = self.constructor.treatment_df.index[i] 
                    if visit in self.constructor.treatment_df.loc[treatment, 'visitsIds']: 
                        break
                repaired_route_plan.treatments[treatment].append(visit) 
            



        #TREATMENT ILLEGAL 
        treatmentInsertor = Insertor(self.constructor, repaired_route_plan)
        for treatment in repaired_route_plan.illegalNotAllocatedTreatments:  
           
            status = treatmentInsertor.insert_treatment(treatment)
      
            if status == True: 
  
                repaired_route_plan = treatmentInsertor.route_plan
                repaired_route_plan.illegalNotAllocatedTreatments.remove(treatment)
                
             
        
        #Legger til treatmenten på pasienten. 
                for i in range(self.constructor.patients_df.shape[0]):
                    patient = self.constructor.patients_df.index[i] 
                    if treatment in self.constructor.patients_df.loc[patient, 'treatmentsIds']: 
                        break
                repaired_route_plan.allocatedPatients[patient].append(treatment) 
                
    
        #LEGGER TIL PASIENTER 
        patientInsertor = Insertor(self.constructor, repaired_route_plan)
        #TODO: Sortere slik at den setter inn de beste først
        repaired_route_plan = patientInsertor.insertPatients(repaired_route_plan.notAllocatedPatients)
        repaired_route_plan.updateObjective()
      
        return repaired_route_plan
    
    def random_repair(self, destroyed_route_plan):
        #Tar bort removed acktivitites, de trenger vi ikk e
        repaired_route_plan = copy.deepcopy(destroyed_route_plan)
        

    
        #VISIT ILLEGAL 
        #TODO: Her burde presedensen også sjekkes, 
        #For jeg vet ikke hvordan den oppdatere seg basert på det som er i ruten 
        visitInsertor = Insertor(self.constructor, repaired_route_plan)
        for visit in list(repaired_route_plan.illegalNotAllocatedVisitsWithPossibleDays.keys()):  
            status = visitInsertor.insert_visit_on_day(visit, repaired_route_plan.illegalNotAllocatedVisitsWithPossibleDays[visit])
            if status == True: 
   
                repaired_route_plan = visitInsertor.route_plan
                del repaired_route_plan.illegalNotAllocatedVisitsWithPossibleDays[visit]

                #Legger til visitet på treatmenten 
                for i in range(self.constructor.treatment_df.shape[0]):
                    treatment = self.constructor.treatment_df.index[i] 
                    if visit in self.constructor.treatment_df.loc[treatment, 'visitsIds']: 
                        break
                repaired_route_plan.treatments[treatment].append(visit) 
            



        #TREATMENT ILLEGAL 
        treatmentInsertor = Insertor(self.constructor, repaired_route_plan)
        for treatment in repaired_route_plan.illegalNotAllocatedTreatments:  
           
            status = treatmentInsertor.insert_treatment(treatment)
      
            if status == True: 
  
                repaired_route_plan = treatmentInsertor.route_plan
                repaired_route_plan.illegalNotAllocatedTreatments.remove(treatment)
                
             
        
        #Legger til treatmenten på pasienten. 
                for i in range(self.constructor.patients_df.shape[0]):
                    patient = self.constructor.patients_df.index[i] 
                    if treatment in self.constructor.patients_df.loc[patient, 'treatmentsIds']: 
                        break
                repaired_route_plan.allocatedPatients[patient].append(treatment) 
                
    
        #LEGGER TIL PASIENTER 
        patientInsertor = Insertor(self.constructor, repaired_route_plan)
        #TODO: Sortere slik at den setter inn de beste først
        repaired_route_plan = patientInsertor.insertPatients(repaired_route_plan.notAllocatedPatients)
        repaired_route_plan.updateObjective()
      
        return repaired_route_plan
    

    #TODO: Burde se på en operator som bytter å mye som mulig mellom to ansatte 