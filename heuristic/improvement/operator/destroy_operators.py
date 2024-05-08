import pandas as pd
import numpy as np
import copy
import math
import numpy.random as rnd 
import random 
import ast
import networkx as nx
from sklearn.cluster import KMeans
from scipy.spatial import cKDTree

from config import main_config

 #To alternativer
        #1) Selected activity er en del av et visit der flere aktiviteter ligger inne. -> Legger til i illegalActivity
        #2) Selected activity er siste som ligger inne på visit, men visit er ikke det siste som ligger inne på treatment. -> Legger til i illegalVisits 
        #3) Visitet er det siste for ligger inne på treatment. -> Legger til i illegalTreatments
        #4) Treatmentet er det siste som ligger på pasienten. -> Pasienten ut av allokeringen, pasienten inn i notAllocated 
      

import os
import sys
sys.path.append( os.path.join(os.path.split(__file__)[0],'..','..','..'))  # Include subfolders

from helpfunctions import checkCandidateBetterThanBest

from objects.activity import Activity
from config.construction_config_infusion import *
from datageneration.distance_matrix import *
from parameters import T_ij

#TODO: Finne ut hva operator funksjonene skal returnere 
class DestroyOperators:
    def __init__(self, alns):
        self.constructor = alns.constructor
        self.count = 0 
        self.alns = alns 


    '''
    Hva skal destuction degreen byttes ut med. 
    
    I removal: Når vi fjerner på visit nivå, henter ut en. 
    Når vi legger inn på illegal visit nivå, så må de aktivitene som ligger i illegla activity fjernes 
    Når vi legger inn på illegal treatment nivå, så må aktiviteten som ligger på illegal visits eller illegal activities fjeres 
    Når vi fjerner pasienter 

    Update funskjonene fungerer både slik at du beveger deg nedenfra også hopper du oppover til riktig nivå
    Oppdateringen nedover bør defor skje når du kommer deg til det nivået du gjør endringer. 
    '''
#---------- RANDOM REMOVAL ----------
    def random_patient_removal(self, current_route_plan):
        # Beregn totalt antall aktiviteter tildelt i løsningen og hvor mange som skal fjernes basert på destruction degree
        num_act_allocated = sum(len(route.route) for day in range(1,current_route_plan.days+1) for route in current_route_plan.routes[day].values())
        total_num_activities_to_remove = round(num_act_allocated * (main_config.destruction_degree_beginning - (main_config.destruction_degree_beginning-main_config.destruction_degree_end)*self.alns.iterationNum/main_config.iterations))
        activity_count = 0
        destroyed_route_plan = copy.deepcopy(current_route_plan)
        while activity_count < total_num_activities_to_remove:
            patientID = rnd.choice(list(destroyed_route_plan.allocatedPatients.keys())) 

            nActInPatient = self.constructor.patients_array[patientID][15]
            activity_count += nActInPatient

            destroyed_route_plan = self.patient_removal(patientID, destroyed_route_plan)[0]
            
        return destroyed_route_plan, None, True
    
    def random_treatment_removal(self, current_route_plan):
        # Beregn totalt antall aktiviteter tildelt i løsningen og hvor mange som skal fjernes basert på destruction degree
        num_act_allocated = sum(len(route.route) for day in range(1,current_route_plan.days+1) for route in current_route_plan.routes[day].values())
        total_num_activities_to_remove = round(num_act_allocated * (main_config.destruction_degree_beginning - (main_config.destruction_degree_beginning-main_config.destruction_degree_end)*self.alns.iterationNum/main_config.iterations))

        activity_count = 0
        destroyed_route_plan = copy.deepcopy(current_route_plan)
        while activity_count < total_num_activities_to_remove:
            treatmentID = rnd.choice(list(destroyed_route_plan.treatments.keys())) 

            visitIdInTreat = destroyed_route_plan.treatments[treatmentID][0]
            actIdInTreat = destroyed_route_plan.visits[visitIdInTreat][0]
            act = destroyed_route_plan.getActivityFromEntireRoutePlan(actIdInTreat)
            activity_count += act.nActInTreat

            destroyed_route_plan = self.treatment_removal(treatmentID, destroyed_route_plan)[0]

        return destroyed_route_plan, None, True
    
    def random_visit_removal(self, current_route_plan):
        # Beregn totalt antall aktiviteter tildelt i løsningen og hvor mange som skal fjernes basert på destruction degree
        num_act_allocated = sum(len(route.route) for day in range(1,current_route_plan.days+1) for route in current_route_plan.routes[day].values())
        total_num_activities_to_remove = round(num_act_allocated * (main_config.destruction_degree_beginning - (main_config.destruction_degree_beginning-main_config.destruction_degree_end)*self.alns.iterationNum/main_config.iterations))

        activity_count = 0
        destroyed_route_plan = copy.deepcopy(current_route_plan)
        while activity_count < total_num_activities_to_remove:
            visitID = rnd.choice(list(destroyed_route_plan.visits.keys())) 

            actIdInVisit = destroyed_route_plan.visits[visitID][0]
            act = destroyed_route_plan.getActivityFromEntireRoutePlan(actIdInVisit)
            activity_count += act.nActInVisit

            destroyed_route_plan = self.visit_removal(visitID, destroyed_route_plan)[0]

        return destroyed_route_plan, None, True
    
    def random_activity_removal(self, current_route_plan): 
        # Beregn totalt antall aktiviteter tildelt i løsningen og hvor mange som skal fjernes basert på destruction degree
        num_act_allocated = sum(len(route.route) for day in range(1,current_route_plan.days+1) for route in current_route_plan.routes[day].values())
        total_num_activities_to_remove = round(num_act_allocated * (main_config.destruction_degree_beginning - 
                                                                    (main_config.destruction_degree_beginning-main_config.destruction_degree_end)*self.alns.iterationNum/main_config.iterations))

        activity_count = 0
        destroyed_route_plan = copy.deepcopy(current_route_plan)
        while activity_count < total_num_activities_to_remove:
            selected_activity = rnd.choice([item for sublist in destroyed_route_plan.visits.values() for item in sublist])
            activity_count += 1
            self.activity_removal(selected_activity, destroyed_route_plan)[0]
        return destroyed_route_plan, None, True
   
 #---------- WORST DEVIATION REMOVAL ----------   

    def worst_deviation_patient_removal(self, current_route_plan):
        # Beregn totalt antall aktiviteter tildelt i løsningen og hvor mange som skal fjernes basert på destruction degree
        num_act_allocated = sum(len(route.route) for day in range(1,current_route_plan.days+1) for route in current_route_plan.routes[day].values())
        total_num_activities_to_remove = round(num_act_allocated * (main_config.destruction_degree_beginning - (main_config.destruction_degree_beginning-main_config.destruction_degree_end)*self.alns.iterationNum/main_config.iterations))

        lowest_patient_contribute = 1000
        activity_count = 0
        destroyed_route_plan = copy.deepcopy(current_route_plan)
        while activity_count < total_num_activities_to_remove: 
            selected_patient = None 
            
            for patient_id in list(destroyed_route_plan.allocatedPatients.keys()): 
                
                if self.constructor.patients_array[patient_id][13] < lowest_patient_contribute: 
                    selected_patient = patient_id
            
            treatIdInPatient = destroyed_route_plan.allocatedPatients[selected_patient][0]
            visitIdInPatient = destroyed_route_plan.treatments[treatIdInPatient][0]
            actIdInPatient = destroyed_route_plan.visits[visitIdInPatient][0]
            act = destroyed_route_plan.getActivityFromEntireRoutePlan(actIdInPatient)
            activity_count += act.nActInPatient

            destroyed_route_plan = self.patient_removal(selected_patient, destroyed_route_plan)[0]

        return destroyed_route_plan, None, True
    
    def worst_deviation_treatment_removal(self, current_route_plan):
        destroyed_route_plan = copy.deepcopy(current_route_plan)
        treatments_to_remove = {}

        # Calculate utility contribution for each treatment
        for treatmentID, visitIDlist in destroyed_route_plan.treatments.items():
            treatment_utility_contribute = 0 
            for visitID in visitIDlist:
                for vis, activityIDlist in destroyed_route_plan.visits.items():
                    if visitID == vis: 
                        for activityID in activityIDlist:
                            treatment_utility_contribute += destroyed_route_plan.getActivity(activityID, destroyed_route_plan.getDayForActivityID(activityID)).suitability
            treatments_to_remove[treatmentID] = treatment_utility_contribute

        # Sort treatments based on utility contribution in ascending order
        sorted_treatments = sorted(treatments_to_remove.items(), key=lambda item: item[1])

        # Calculate number of treatments to remove based on destruction degree
        total_num_treatments_to_remove = round(len(sorted_treatments) * (main_config.destruction_degree_beginning - 
                                                                        (main_config.destruction_degree_beginning - main_config.destruction_degree_end) * self.alns.iterationNum / main_config.iterations))

        # Remove the specified number of treatments with the lowest utility contributions
        for selected_treatment, _ in sorted_treatments[:total_num_treatments_to_remove]:
            for selected_visit in destroyed_route_plan.treatments[selected_treatment]:
                for selected_activity in destroyed_route_plan.visits[selected_visit]:
                    destroyed_route_plan = self.activity_removal(selected_activity, destroyed_route_plan)[0]

        return destroyed_route_plan, None, True

    def worst_deviation_visit_removal(self, current_route_plan):
        visits_to_remove = {}
        destroyed_route_plan = copy.deepcopy(current_route_plan)
     
        for visitID, activitieIDList in destroyed_route_plan.visits.items():
            visit_utility_contribute = 0
            visit_skilldiff_contribute = 0
            visit_travel_time = 0
            for activityID in activitieIDList: 
                activity, activity_index, activity_route = destroyed_route_plan.getActivityAndActivityIndexAndRoute(activityID)
                before_activity_id = 0 
                after_actitivy_id = 0 
                if activity_index != 0: 
                    before_activity_id = activity_route.route[activity_index-1].id
                if activity_index != len(activity_route.route)-1: 
                    after_actitivy_id = activity_route.route[activity_index+1].id
                visit_utility_contribute += activity.suitability
                visit_skilldiff_contribute += destroyed_route_plan.getRouteSkillLevForActivityID(activityID) - activity.skillReq
                visit_travel_time += T_ij[before_activity_id][activity_index] + T_ij[activity_index][after_actitivy_id] - T_ij[before_activity_id][after_actitivy_id]     
            
            visits_to_remove[visitID] = [visit_utility_contribute, -visit_skilldiff_contribute, -visit_travel_time]

        sorted_visits_to_remove = {k: v for k, v in sorted(visits_to_remove.items(), key=lambda item: item[1])}
        total_num_visits_to_remove = round(len(sorted_visits_to_remove) * (main_config.destruction_degree_beginning - 
                                                                           (main_config.destruction_degree_beginning-main_config.destruction_degree_end)*self.alns.iterationNum/main_config.iterations))

        for selected_visit in list(sorted_visits_to_remove.keys())[:total_num_visits_to_remove]: 
            for selected_activity in destroyed_route_plan.visits[selected_visit]:
                destroyed_route_plan = self.activity_removal(selected_activity, destroyed_route_plan)[0]
        
        return destroyed_route_plan, None, True
    
    def worst_deviation_activity_removal(self, current_route_plan):
        num_act_allocated = sum(len(route.route) for day in range(1, current_route_plan.days+1) for route in current_route_plan.routes[day].values())
        total_num_activities_to_remove = round(num_act_allocated * (main_config.destruction_degree_beginning -
                                                                    (main_config.destruction_degree_beginning - main_config.destruction_degree_end) * self.alns.iterationNum / main_config.iterations))

        activities_to_remove = {}
        destroyed_route_plan = copy.deepcopy(current_route_plan)

        # Gather all activities and calculate their negative contributions
        for day in range(1, destroyed_route_plan.days + 1):
            for route in destroyed_route_plan.routes[day].values():
                for activity_index, activity in enumerate(route.route):
                    before_activity_id = route.route[activity_index - 1].id if activity_index != 0 else None
                    after_activity_id = route.route[activity_index + 1].id if activity_index != (len(route.route) - 1) else None

                    activity_skilldiff_contribute = destroyed_route_plan.getRouteSkillLevForActivityID(activity.id) - activity.skillReq if activity.id is not None else 0
                    activity_travel_time = 0
                    if before_activity_id is not None and activity.id is not None:
                        activity_travel_time += T_ij[before_activity_id][activity.id]
                    if activity.id is not None and after_activity_id is not None:
                        activity_travel_time += T_ij[activity.id][after_activity_id]
                    if before_activity_id is not None and after_activity_id is not None:
                        activity_travel_time -= T_ij[before_activity_id][after_activity_id]

                    total_negative_contribution = activity_skilldiff_contribute + activity_travel_time
                    activities_to_remove[activity] = total_negative_contribution

        # Sort activities by their total negative impact in descending order (most negative first)
        sorted_activities = sorted(activities_to_remove.items(), key=lambda item: item[1], reverse=True)

        # Remove the specified number of activities with the highest negative impact
        for selected_activity, _ in sorted_activities[:total_num_activities_to_remove]:
            print(f"Removing activity ID: {selected_activity.id}")
            destroyed_route_plan = self.activity_removal(selected_activity.id, destroyed_route_plan)[0]

        return destroyed_route_plan, None, True

        
    def worst_deviation_activity_removalG(self, current_route_plan):
        num_act_allocated = sum(len(route.route) for day in range(1, current_route_plan.days+1) for route in current_route_plan.routes[day].values())
        total_num_activities_to_remove = round(num_act_allocated * (main_config.destruction_degree_beginning - 
                                                                    (main_config.destruction_degree_beginning-main_config.destruction_degree_end)*self.alns.iterationNum/main_config.iterations))

        activities_to_remove = {}
        destroyed_route_plan = copy.deepcopy(current_route_plan)

        for day in range(1, destroyed_route_plan.days + 1): 
            for route in destroyed_route_plan.routes[day].values(): 
                for activity_index, activity in enumerate(route.route):
                    before_activity_id = route.route[activity_index - 1].id if activity_index != 0 else None
                    after_activity_id = route.route[activity_index + 1].id if activity_index != (len(route.route) - 1) else None

                    # Calculate contributions
                    activity_skilldiff_contribute = destroyed_route_plan.getRouteSkillLevForActivityID(activity.id) - activity.skillReq
                    activity_travel_time = 0
                    if before_activity_id is not None and activity.id is not None:
                        activity_travel_time += T_ij[before_activity_id][activity.id]
                    if activity.id is not None and after_activity_id is not None:
                        activity_travel_time += T_ij[activity.id][after_activity_id]
                    if before_activity_id is not None and after_activity_id is not None:
                        activity_travel_time -= T_ij[before_activity_id][after_activity_id]

                    activities_to_remove[activity] = [-activity_skilldiff_contribute, -activity_travel_time]

        # Sorting activities based on their contribution metrics
        sorted_activities = sorted(activities_to_remove.items(), key=lambda item: item[1])

        # Removing activities
        for selected_activity, _ in sorted_activities[:total_num_activities_to_remove]: 
            destroyed_route_plan = self.activity_removal(selected_activity, destroyed_route_plan)[0]

        return destroyed_route_plan, None, True

    def worst_deviation_activity_removalG(self, current_route_plan): 
        #TODO: Virker som denne operatoren ble veldig treg ved å legge in destruction degree på denne måten
        num_act_allocated = sum(len(route.route) for day in range(1,current_route_plan.days+1) for route in current_route_plan.routes[day].values())
        total_num_activities_to_remove = round(num_act_allocated * (main_config.destruction_degree_beginning - 
                                                                    (main_config.destruction_degree_beginning-main_config.destruction_degree_end)*self.alns.iterationNum/main_config.iterations))

        activities_to_remove = {}
        destroyed_route_plan = copy.deepcopy(current_route_plan)
     
        for day in range(1, destroyed_route_plan.days +1): 
            for route in destroyed_route_plan.routes[day].values(): 
                for activity_index in range(len(route.route)):
                    activity = route.route[activity_index] 
                    
                    before_activity_id = 0 
                    after_activity_id = 0 
                    if activity_index != 0: 
                        before_activity_id = route.route[activity_index-1].id
                    if activity_index != len(route.route)-1: 
                        after_activity_id = route.route[activity_index+1].id

                    activity_skilldiff_contribute = destroyed_route_plan.getRouteSkillLevForActivityID(activity.id) - activity.skillReq
                    activity_travel_time = T_ij[before_activity_id][activity.id] + T_ij[activity.id][after_activity_id] - T_ij[before_activity_id][after_activity_id]
                    
                    activities_to_remove[activity] = [-activity_skilldiff_contribute, -activity_travel_time]
            
        sorted_activities_to_remove = {k: v for k, v in sorted(activities_to_remove.items(), key=lambda item: item[1])}

        for selected_activity in list(sorted_activities_to_remove.keys())[:total_num_activities_to_remove]: 
            destroyed_route_plan = self.activity_removal(selected_activity, destroyed_route_plan)[0]
            
        return destroyed_route_plan, None, True
    
#---------- CLUSTER DISTANCE REMOVAL ----------
    
 # TAR HENSYN TIL DESTRUCTION DEGREE
    def cluster_distance_patients_removal(self, current_route_plan): 
        '''
        Ender ofte opp med å fjerne en del mer aktiviteter enn ønsket, fordi funksjonen er skrevet slik at den alltid fjerner et helt cluster (siden det gir mest mening). 
        TODO: Sjekke om det fungerer bra å dele allocated patients i flere cluster enn 2 hver gang, slik at antall pasienter som fjernes i hver iterasjon i while-løkken er mindre. 
        
        '''
        num_act_allocated = sum(len(route.route) for day in range(1,current_route_plan.days+1) for route in current_route_plan.routes[day].values())
        total_num_activities_to_remove = round(num_act_allocated * (main_config.destruction_degree_beginning - 
                                                                    (main_config.destruction_degree_beginning-main_config.destruction_degree_end)*self.alns.iterationNum/main_config.iterations))
        
        # Forbered en kopi av ruteplanen for modifikasjoner
        destroyed_route_plan = copy.deepcopy(current_route_plan)
        removed_activities_count = 0

        while removed_activities_count < total_num_activities_to_remove:
            # Oppdater listen over tildelte pasienter basert på den nåværende (potensielt modifiserte) ruteplanen
            allocatedPatientsIds = list(destroyed_route_plan.allocatedPatients.keys())
            if not allocatedPatientsIds:  # Avslutt hvis det ikke er flere pasienter å fjerne
                break

            patients_and_location = []
            for i in range(len(self.constructor.patients_array)):
                for patient in allocatedPatientsIds:
                    if i == patient: 
                        patients_and_location.append((patient, self.constructor.patients_array[patient][7]))

            selected_patients = self.k_means_clustering(patients_and_location)

            # Beregn antallet aktiviteter som vil bli fjernet i denne iterasjonen
            activities_to_remove_now = sum([self.constructor.patients_array[patient_id][15] for patient_id in selected_patients])
            
            for patientID in selected_patients:
                destroyed_route_plan = self.patient_removal(patientID, destroyed_route_plan)[0]

            removed_activities_count += activities_to_remove_now
            
            if removed_activities_count >= total_num_activities_to_remove:
                break

        #print(f'Removed {removed_activities_count} of {num_act_allocated} allocated activities. Wanted to remove {round(num_act_allocated * (main_config.destruction_degree_beginning - (main_config.destruction_degree_beginning-main_config.destruction_degree_end)*self.alns.iterationNum/main_config.iterations))}') # with a destruction degree {main_config.destruction_degree}')

        return destroyed_route_plan, None, True



    # TAR HENSYN TIL DESTRUCTION DEGREE
    def cluster_distance_activities_removal(self, current_route_plan):
        num_act_allocated = sum(len(route.route) for day in range(1,current_route_plan.days+1) for route in current_route_plan.routes[day].values())
        total_num_activities_to_remove = round(num_act_allocated * (main_config.destruction_degree_beginning - 
                                                                    (main_config.destruction_degree_beginning-main_config.destruction_degree_end)*self.alns.iterationNum/main_config.iterations))
        
        sorted_routes =  sorted((route for day in range(1,current_route_plan.days+1) for route in current_route_plan.routes[day].values()), key=lambda x: x.travel_time, reverse=True)
        destroyed_route_plan = copy.deepcopy(current_route_plan)
        removed_activities_count = 0
        selected_activities = []

        while removed_activities_count < total_num_activities_to_remove and sorted_routes:
            current_route = sorted_routes.pop(0)
            activities_in_current_route = [activity.id for activity in current_route.route]
            
            if len(activities_in_current_route) == 0:
                # Hvis den går inn i denne betyr det at vi har gått inn i alle ruter og fjernet noe, men ikke klart å fjerne nok aktiviteter til å dekke destruction degree.
                # Hvis du vil justere dette kan du justere på hvor mange prosent av hver rute som skal fjernes i hver rute (nå står den på 30 % av ruten)
                #print(f'Removed {removed_activities_count} of {num_act_allocated} allocated activities. Wanted to remove {round(num_act_allocated * (main_config.destruction_degree_beginning - (main_config.destruction_degree_beginning-main_config.destruction_degree_end)*self.alns.iterationNum/main_config.iterations))} with a destruction degree {main_config.destruction_degree}')
                break

            elif len(activities_in_current_route) == 1:
                removed_activities_count += 1
                total_num_activities_to_remove -= 1
                continue

            activities_and_location = []
            for i in range(len(self.constructor.activities_array)):
                for act in activities_in_current_route:
                    if i == act: 
                        activities_and_location.append((act, current_route_plan.getActivity(act, current_route_plan.getDayForActivityID(act)).location))
            
            selected_activities += self.k_means_clustering(activities_and_location)

            removed_activities_count += len(selected_activities)
    
            if removed_activities_count >= total_num_activities_to_remove:
                break

        for activityID in selected_activities:
            destroyed_route_plan = self.activity_removal(activityID, destroyed_route_plan)[0]
            

        return destroyed_route_plan, None, True
    


#---------- SPREAD DISTANCE REMOVAL ----------
    
    # TAR HENSYN TIL DESTRUCTION DEGREE
    def spread_distance_patients_removal(self, current_route_plan):
        num_act_allocated = sum(len(route.route) for day in range(1,current_route_plan.days+1) for route in current_route_plan.routes[day].values())
        total_num_activities_to_remove = round(num_act_allocated * (main_config.destruction_degree_beginning - (main_config.destruction_degree_beginning-main_config.destruction_degree_end)*self.alns.iterationNum/main_config.iterations))

        allocatedPatientsIds = list(current_route_plan.allocatedPatients.keys())

        patients_and_location = []
        for i in range(len(self.constructor.patients_array)):
            for patient in allocatedPatientsIds:
                if i == patient: 
                    patients_and_location.append((patient, self.constructor.patients_array[patient][7]))

        # Beregne "spread" for hver pasient
        nearest_neighbor_distances = self.find_nearest_neighbors_with_kdtree(patients_and_location)

        # Sortere pasientene basert på "spread"
        patients_with_spread = list(zip(allocatedPatientsIds, nearest_neighbor_distances))
        patients_sorted_by_spread = sorted(patients_with_spread, key=lambda x: x[1], reverse=True)
        sorted_patient_ids = [patient[0] for patient in patients_sorted_by_spread]

        # Velge pasienter for fjerning basert på "spread" og antall aktiviteter som skal fjernes
        removed_activities_count = 0
        patients_to_remove = []
        for patientID in sorted_patient_ids:
            if removed_activities_count >= total_num_activities_to_remove:
                break
            num_activities_for_patient = self.constructor.patients_array[patientID][15]  # Assume this dictionary exists or implement accordingly
            removed_activities_count += num_activities_for_patient
            patients_to_remove.append(patientID)
        
        #print(f'Removed {removed_activities_count} of {num_act_allocated} allocated activities. Wanted to remove {round(num_act_allocated * (main_config.destruction_degree_beginning - (main_config.destruction_degree_beginning-main_config.destruction_degree_end)*self.alns.iterationNum/main_config.iterations))} with a destruction degree {(main_config.destruction_degree_beginning - (main_config.destruction_degree_beginning-main_config.destruction_degree_end)*self.alns.iterationNum/main_config.iterations)}')
        #print("patients_to_remove", patients_to_remove)
        
        # Fjerne valgte pasienter og deres aktiviteter fra ruteplanen
        destroyed_route_plan = copy.deepcopy(current_route_plan)
        for patientID in patients_to_remove:
            destroyed_route_plan = self.patient_removal(patientID, destroyed_route_plan)[0]

        return destroyed_route_plan, None, True

    # TAR HENSYN TIL DESTRUCTION DEGREE
    def spread_distance_activities_removal(self, current_route_plan):
        num_act_allocated = sum(len(route.route) for day in range(1, current_route_plan.days + 1) for route in current_route_plan.routes[day].values())
        total_num_activities_to_remove = round(num_act_allocated * (main_config.destruction_degree_beginning - 
                                                                (main_config.destruction_degree_beginning - main_config.destruction_degree_end) * self.alns.iterationNum / main_config.iterations))
        
        sorted_routes = sorted((route for day in range(1, current_route_plan.days + 1) for route in current_route_plan.routes[day].values()), key=lambda x: x.travel_time, reverse=True)
        destroyed_route_plan = copy.deepcopy(current_route_plan)
        activities_to_remove = []

        while total_num_activities_to_remove > 0 and sorted_routes:
            current_route = sorted_routes.pop(0)
            activities_in_current_route = [activity.id for activity in current_route.route]

            if len(activities_in_current_route) == 0:
                break
            elif len(activities_in_current_route) == 1:
                activities_to_remove.append(activities_in_current_route[0])
                total_num_activities_to_remove -= 1
                continue

            activities_and_locations = [(act, self.constructor.activities_array[act][14]) for act in activities_in_current_route]       
            nearest_neighbor_distances = self.find_nearest_neighbors_with_kdtree(activities_and_locations)

            num_activities_to_remove = min(total_num_activities_to_remove, round(len(nearest_neighbor_distances) * 0.3))
            activities_to_remove_indices = np.argsort(-nearest_neighbor_distances)[:num_activities_to_remove]
            activities_to_remove.extend([activities_in_current_route[idx] for idx in activities_to_remove_indices])

            total_num_activities_to_remove -= num_activities_to_remove

        for activityID in activities_to_remove:
            destroyed_route_plan = self.activity_removal(activityID, destroyed_route_plan)[0]

        return destroyed_route_plan, None, True

    
    


#---------- RELATED REMOVAL ----------

    def related_visits_removal(self, current_route_plan):
        # Beregn det totale antallet aktiviteter som skal fjernes fra hele ruteplanen
        num_act_allocated = sum(len(route.route) for day in range(1,current_route_plan.days+1) for route in current_route_plan.routes[day].values())
        total_num_activities_to_remove = round(num_act_allocated * (main_config.destruction_degree_beginning - (main_config.destruction_degree_beginning-main_config.destruction_degree_end)*self.alns.iterationNum/main_config.iterations))

        # Forberede liste med visits
        allocatedVisitsIds = list(current_route_plan.visits.keys())

        primary_visitId = random.choice(allocatedVisitsIds)
        p_firstActId = current_route_plan.visits[primary_visitId][0] #Henter ut første aktivitet for gitt visit
        p_lastActId = current_route_plan.visits[primary_visitId][-1] #Henter ut siste aktivitet for gitt visit
        p_day = current_route_plan.getDayForActivityID(p_firstActId)
    

        # Get the highest professional reequirement for the primary visit
        p_maxSkillReq = 0
        for p_actId in current_route_plan.visits[primary_visitId]: 
            p_act = current_route_plan.getActivity(p_actId, p_day)
            p_skillReq = p_act.skillReq
            if p_skillReq > p_maxSkillReq:
                p_maxSkillReq = p_skillReq

        # Time windows and duration for the primary visit
        p_firstAct = current_route_plan.getActivityFromEntireRoutePlan(p_firstActId)
        p_lastAct = current_route_plan.getActivityFromEntireRoutePlan(p_lastActId)
        p_visitStarted = p_firstAct.startTime
        p_visitFinished = p_lastAct.startTime + p_lastAct.duration
        p_visitDuration = 0
        for p_actId in current_route_plan.visits[primary_visitId]:
            p_act = current_route_plan.getActivityFromEntireRoutePlan(p_actId)
            p_visitDuration += p_act.duration
        p_visitEarliestStart = p_firstAct.earliestStartTime
        p_visitLatestStart = p_firstAct.latestStartTime        

        visitsSameDay = []
        visitsSameSkillReq = []
        visitsSameNumAct = []
        visitsOverlapTW = []
        visitsRelatedStartTimes = []
        related_visit_dict = {}
        for visitId, activitiesIds in current_route_plan.visits.items(): 
            if visitId != primary_visitId:
                related_score = 0
                # Visits on the same day as the primary visit
                #NOTE: SKAL ALLE DE UNDER EGENTLIG KUN SKJE OM DET ER SAMME DAG?? DVS AT ALLE IF UNDER DENNE SKAL INN ET HAKK
                if ((current_route_plan.getDayForActivityID(activitiesIds[0]) == p_day) and (visitId not in visitsSameDay)):
                    visitsSameDay.append(visitId)
                    related_score += 1

                # Visits with the same max professional requirement as the primary visit
                maxSkillReq = 0
                for actId in activitiesIds:
                    act = current_route_plan.getActivityFromEntireRoutePlan(actId)
                    skillReq = act.skillReq
                    if skillReq > maxSkillReq:
                        maxSkillReq = skillReq
                if (maxSkillReq == p_maxSkillReq and visitId not in visitsSameSkillReq):
                    visitsSameSkillReq.append(visitId)
                    related_score += 1

                # Visits with the same amount of activities as the primary visit
                if (len(activitiesIds) == len(current_route_plan.visits[primary_visitId]) and (visitId not in visitsSameNumAct)):
                    visitsSameNumAct.append(visitId)
                    related_score += 1

                # Data for checks regarding time windows, start times and durations
                firstAct = current_route_plan.getActivityFromEntireRoutePlan(activitiesIds[0])
                lastAct = current_route_plan.getActivityFromEntireRoutePlan(activitiesIds[-1])
                visitStarted = firstAct.startTime
                visitFinished = lastAct.startTime + lastAct.duration
                visitDuration = 0
                for actId in activitiesIds:
                    act = current_route_plan.getActivityFromEntireRoutePlan(actId)
                    visitDuration += act.duration
                visitEarliestStart = firstAct.earliestStartTime
                visitLatestStart = firstAct.latestStartTime

                # Visits where the time windows overlap with the primary visit's time window
                if ((visitEarliestStart < p_visitLatestStart) and (visitLatestStart > p_visitEarliestStart)     #legge inn duration her?
                    and (p_visitEarliestStart < visitLatestStart) and (p_visitLatestStart > visitEarliestStart) #legge inn duration her?
                    and (visitId not in visitsOverlapTW)):
                    visitsOverlapTW.append(visitId)
                    related_score += 1

                    # Visits with start times related with the primary visit
                    if ((visitStarted + visitDuration < p_visitLatestStart) and (visitStarted > p_visitEarliestStart)     
                        and (p_visitStarted + visitDuration < visitLatestStart) and (p_visitStarted > visitEarliestStart) 
                        and (visitId not in visitsRelatedStartTimes)):                     
                        visitsRelatedStartTimes.append(visitId)
                        related_score += 1

                # Add visit and score to related visit dictionary
                related_visit_dict[visitId] = related_score
                
        sorted_related_visit_dict = dict(sorted(related_visit_dict.items(), key=lambda item: item[1], reverse=True))

        destroyed_route_plan = copy.deepcopy(current_route_plan)
        # Removing primary visit
        destroyed_route_plan = self.visit_removal(primary_visitId, destroyed_route_plan)[0]
        activities_count = len(current_route_plan.visits[primary_visitId])
        # Removing visits with the highest relatedness score
        removed_visits = [primary_visitId]
        for visitId in list(sorted_related_visit_dict.keys()): 
            if activities_count >= total_num_activities_to_remove:
                break
            # Visits are only removed if the relatedness score is higher than 0
            if sorted_related_visit_dict[visitId] > 0:
                destroyed_route_plan = self.visit_removal(visitId, destroyed_route_plan)[0]
                activities_count += len(current_route_plan.visits[visitId])
                removed_visits.append(visitId)
        #print(f'Removed visits: ', removed_visits)
        #print(f'Removed {activities_count} of {num_act_allocated} allocated activities. Wanted to remove {round(num_act_allocated * main_config.destruction_degree)} with a destruction degree {main_config.destruction_degree}')

        return destroyed_route_plan, None, True

    def related_treatments_removalG(self, current_route_plan):
            #TODO: Forbedre ytelse, den har veldig dårlig ytelse nå. 
            # Beregn det totale antallet aktiviteter som skal fjernes fra hele ruteplanen
            num_act_allocated = sum(len(route.route) for day in range(1,current_route_plan.days+1) for route in current_route_plan.routes[day].values())
            total_num_activities_to_remove = round(num_act_allocated * (main_config.destruction_degree_beginning - 
                                                                        (main_config.destruction_degree_beginning-main_config.destruction_degree_end)*self.alns.iterationNum/main_config.iterations))

            allocatedTreatmentsIds = list(current_route_plan.treatments.keys())

            # Velger en random treatment og finner hvilket pattern og patterntype det har i ruteplanen.
            primary_treatmentId = random.choice(allocatedTreatmentsIds)
            filtered_row = self.constructor.treatments_array[primary_treatmentId]
            patternType = self.constructor.treatments_array[primary_treatmentId][1]
            TreatSamePatternType = self.constructor.treatment_df[self.constructor.treatment_array['patternType'] == patternType].index.intersection(allocatedTreatmentsIds).tolist()

            #Vet at vi har funnet de ulike treatmentsene som er riktig 
            firstActId = self.constructor.treatments_array[filtered_row][20][0]
            visitID = self.constructor.activities_array[firstActId][12]
            for act in self.constructor.visits_array[visitID][14]:
                act = current_route_plan.getActivityFromEntireRoutePlan(act)
                if act != None: 
                    break 
        
            if act == None: 
                firstDay = current_route_plan.illegalNotAllocatedVisitsWithPossibleDays[visitID]
            else: 
                firstDay = current_route_plan.getDayForActivityID(act)

            related_treatment_list = [primary_treatmentId]
    
            activities_count = 0
            for visitID in current_route_plan.treatments[primary_treatmentId]: 
                activities_count += len(current_route_plan.visits[visitID])

            # Fjerner treatments som har samme pattern
            filtered_df = self.constructor.treatment_df.loc[TreatSamePatternType]
            firstActInTreatSamePatternType = [ids[0] if ids else None for ids in filtered_df['activitiesIds']] #Liste: Første aktivitet i alle treatments som har samme patterntype og er allokert i current_route_plan
            firstActInTreatSamePatternType.remove(firstActId) 
        
            backup_treatments = []
        
            for actId in firstActInTreatSamePatternType:
                if activities_count >= total_num_activities_to_remove:
                    break

                visitID = self.constructor.activities_array[actId][12]
                for act in self.constructor.visits_array[visitID][14]: 
                    act = current_route_plan.getActivityFromEntireRoutePlan(act)
                    if act != None: 
                        break 

                if act == None: 
                    day_for_first_activity_in_treatment = current_route_plan.illegalNotAllocatedVisitsWithPossibleDays[visitID]
                else: 
                    day_for_first_activity_in_treatment = current_route_plan.getDayForActivityID(act)

                treatment_for_activity = self.contructor.activities_array[actId][13]

                if day_for_first_activity_in_treatment == firstDay:
                    if treatment_for_activity not in related_treatment_list:
                        related_treatment_list.append(treatment_for_activity)
                        activities_count += len([current_route_plan.visits[visitID] for visitID in current_route_plan.treatments[treatment_for_activity]])
        
                
                else: 
                    if treatment_for_activity not in backup_treatments and treatment_for_activity not in related_treatment_list:
                        backup_treatments.append(treatment_for_activity)

            while activities_count < total_num_activities_to_remove and len(backup_treatments) > 0: 
                related_treatment_list.append(backup_treatments.pop(0))
                activities_count += len([current_route_plan.visits[visitID] for visitID in current_route_plan.treatments[treatment_for_activity]])

            destroyed_route_plan = copy.deepcopy(current_route_plan)
            for treatId in related_treatment_list:
                destroyed_route_plan = self.treatment_removal(treatId, destroyed_route_plan)[0] 
            
            return destroyed_route_plan, None, True
    
    def related_treatments_removal(self, current_route_plan):
        num_act_allocated = sum(len(route.route) for day in range(1, current_route_plan.days+1) for route in current_route_plan.routes[day].values())
        total_num_activities_to_remove = round(num_act_allocated * (main_config.destruction_degree_beginning - 
                                                                    (main_config.destruction_degree_beginning - main_config.destruction_degree_end) * self.alns.iterationNum / main_config.iterations))
        
        allocatedTreatmentsIds = list(current_route_plan.treatments.keys())

        # Select a random treatment and determine its pattern type
        primary_treatmentId = random.choice(allocatedTreatmentsIds)
        patternType = self.constructor.treatments_array[primary_treatmentId][1]  # Accessing pattern type directly from the array

        # Find all treatments with the same pattern type
        TreatSamePatternType = [treatment_id for treatment_id in allocatedTreatmentsIds if self.constructor.treatments_array[treatment_id][1] == patternType]

        # Assuming that the first activity ID for a treatment is stored in the 20th index of the treatment's array
        firstActId = self.constructor.treatments_array[primary_treatmentId][20][0]
        visitID = self.constructor.activities_array[firstActId][12]

        # Get the first activity in the visit or determine the day if none are allocated
        act = None
        for act_id in self.constructor.visits_array[visitID][14]:
            act = current_route_plan.getActivityFromEntireRoutePlan(act_id)
            if act:
                break
        
        firstDay = current_route_plan.getDayForActivityID(act.id) if act else current_route_plan.illegalNotAllocatedVisitsWithPossibleDays[visitID]

        related_treatment_list = [primary_treatmentId]
        activities_count = sum(len(current_route_plan.visits[visitID]) for visitID in current_route_plan.treatments[primary_treatmentId])

        # Iterate over found treatments with the same pattern type
        for treatment_id in TreatSamePatternType:
            firstActId_in_treatment = self.constructor.treatments_array[treatment_id][20][0]
            visitID = self.constructor.activities_array[firstActId_in_treatment][12]
            act = None
            for act_id in self.constructor.visits_array[visitID][14]:
                act = current_route_plan.getActivityFromEntireRoutePlan(act_id)
                if act:
                    break
            
            day_for_first_activity_in_treatment = current_route_plan.getDayForActivityID(act.id) if act else current_route_plan.illegalNotAllocatedVisitsWithPossibleDays[visitID]
            treatment_for_activity = self.constructor.activities_array[firstActId_in_treatment][13]

            if day_for_first_activity_in_treatment == firstDay:
                if treatment_for_activity not in related_treatment_list:
                    related_treatment_list.append(treatment_for_activity)
                    activities_count += sum(len(current_route_plan.visits[visitID]) for visitID in current_route_plan.treatments[treatment_for_activity])

        # Remove treatments if necessary
        destroyed_route_plan = copy.deepcopy(current_route_plan)
        for treatId in related_treatment_list:
            destroyed_route_plan = self.treatment_removal(treatId, destroyed_route_plan)[0]
        
        return destroyed_route_plan, None, True
        

   
    def patients_removal(self, current_route_plan, patient_list): 
        destroyed_route_plan = copy.deepcopy(current_route_plan)
        for patientID in patient_list: 
            destroyed_route_plan = self.patient_removal(patientID, destroyed_route_plan)[0]
        return destroyed_route_plan, None, True
 

    def related_patients_removal(self, current_route_plan):
        num_act_allocated = sum(len(route.route) for day in range(1,current_route_plan.days+1) for route in current_route_plan.routes[day].values())
        total_num_activities_to_remove = round(num_act_allocated * (main_config.destruction_degree_beginning - (main_config.destruction_degree_beginning-main_config.destruction_degree_end)*self.alns.iterationNum/main_config.iterations))
        
        activities_to_remove = []
        patientsIDs_to_removed = []
        
        for illegalActivityID in current_route_plan.illegalNotAllocatedActivitiesWithPossibleDays.keys(): 
            i_day = current_route_plan.getDayForActivityID(illegalActivityID)
            allocated_patientID_for_illegalActivityID = self.current_route_plan.getActivity(illegalActivityID, i_day).patientId
            if allocated_patientID_for_illegalActivityID in patientsIDs_to_removed: 
                continue
            
            for allocated_treatment in current_route_plan.allocatedPatients[allocated_patientID_for_illegalActivityID]: 
                for allocated_visit in current_route_plan.treatments[allocated_treatment]: 
                    for allocated_activity in current_route_plan.visits[allocated_visit]: 
                        activities_to_remove.append(allocated_activity)
            patientsIDs_to_removed.append(allocated_patientID_for_illegalActivityID)
            if len(activities_to_remove) >= total_num_activities_to_remove: 
                return self.patients_removal(current_route_plan, patientsIDs_to_removed)
       
        #Vet at vi ikke har nådd tilstrekkelig antall aktiviteter ved å bare fjerne aktivitene som er i illegalActiviy 
        for illegalVisitID in current_route_plan.illegalNotAllocatedVisitsWithPossibleDays.keys(): 
            allocated_patientID_for_illegalVisitID = self.constructor.visits_array[illegalVisitID][1]
            if allocated_patientID_for_illegalVisitID in patientsIDs_to_removed: 
                continue

            for allocated_treatment in current_route_plan.allocatedPatients[allocated_patientID_for_illegalVisitID]: 
                for allocated_visit in current_route_plan.treatments[allocated_treatment]: 
                    for allocated_activity in current_route_plan.visits[allocated_visit]: 
                        activities_to_remove.append(allocated_activity)
            patientsIDs_to_removed.append(allocated_patientID_for_illegalVisitID)
            if len(activities_to_remove) >= total_num_activities_to_remove: 
                return self.patients_removal(current_route_plan, patientsIDs_to_removed)
        
        #Går illegal Treatments og legger til relaterte pasienter i pasienter som skal fjernes 
        for illegalTreatmentID in current_route_plan.illegalNotAllocatedTreatments: 
            allocated_patientID_for_illegalTreatmentID = self.constructor.treatments_array[illegalTreatmentID][0]
            if allocated_patientID_for_illegalTreatmentID in patientsIDs_to_removed: 
                continue

            for allocated_treatment in current_route_plan.allocatedPatients[allocated_patientID_for_illegalTreatmentID]: 
                for allocated_visit in current_route_plan.treatments[allocated_treatment]: 
                    for allocated_activity in current_route_plan.visits[allocated_visit]: 
                        activities_to_remove.append(allocated_activity)
            patientsIDs_to_removed.append(allocated_patientID_for_illegalTreatmentID)
            if len(activities_to_remove) >= total_num_activities_to_remove: 
                return self.patients_removal(current_route_plan, patientsIDs_to_removed)

        # Remove based on utility if destruction degree is not met
        ascendingUtilityAllocatedPatientsDict =  {patient: self.constructor.patients_array[patient][13] for patient in current_route_plan.allocatedPatients.keys()}
        ascendingUtilityNotAllocatedPatients = sorted(ascendingUtilityAllocatedPatientsDict, key=ascendingUtilityAllocatedPatientsDict.get)

        for patientID in ascendingUtilityNotAllocatedPatients: 
            if patientID in patientsIDs_to_removed: 
                continue
            for allocated_treatment in current_route_plan.allocatedPatients[patientID]: 
                for allocated_visit in current_route_plan.treatments[allocated_treatment]: 
                    for allocated_activity in current_route_plan.visits[allocated_visit]: 
                        activities_to_remove.append(allocated_activity)
            patientsIDs_to_removed.append(patientID)
            if len(activities_to_remove) >= total_num_activities_to_remove: 
                return self.patients_removal(current_route_plan, patientsIDs_to_removed)




#---------- HELP FUNCTIONS ----------
    def patient_removal(self, selected_patient, route_plan): 
        destroyed_route_plan = copy.deepcopy(route_plan)
        removed_activities = []
        # Activities for patient removed from visit and treatment dictionary
        for treatment in destroyed_route_plan.allocatedPatients[selected_patient]: 
            for visit in destroyed_route_plan.treatments[treatment]:
                removed_activities += destroyed_route_plan.visits[visit]
                del destroyed_route_plan.visits[visit]
            del destroyed_route_plan.treatments[treatment]
        # Activities for patient removed from route
        destroyed_route_plan.remove_activityIDs_from_route_plan(removed_activities)
        # Patient removed from allocated and added in not allocated dictionary 
    
        return self.updateDictionariesForRoutePlanPatientLevel(selected_patient, destroyed_route_plan)

    
    
    def treatment_removal(self, selected_treatment, route_plan):
        destroyed_route_plan = copy.deepcopy(route_plan)
        removed_activities = []
        for visit in destroyed_route_plan.treatments[selected_treatment]:
            removed_activities += destroyed_route_plan.visits[visit]
            del destroyed_route_plan.visits[visit]
        #del route_plan.treatments[selected_treatment]
        destroyed_route_plan.remove_activityIDs_from_route_plan(removed_activities)
        return self.updateDictionariesForRoutePlanTreatmentLevel(selected_treatment, destroyed_route_plan)
    
    
    def visit_removal(self, selected_visit, route_plan):
        destroyed_route_plan = copy.deepcopy(route_plan)
        removed_activities = destroyed_route_plan.visits[selected_visit]
        #del destroyed_route_plan.visits[selected_visit]
        original_day = destroyed_route_plan.remove_activityIDs_return_day(removed_activities)
        return self.updateDictionariesForRoutePlanVisitLevel(selected_visit, destroyed_route_plan, original_day)
 
    def activity_removal(self, selected_activity, route_plan):
        destroyed_route_plan = copy.deepcopy(route_plan)
        original_day = destroyed_route_plan.removeActivityIDgetRemoveDay(selected_activity)
        return self.updateDictionariesForRoutePlanActivityLevel(selected_activity, destroyed_route_plan, original_day)
   
    def updateDictionariesForRoutePlanPatientLevel(self, patient_removed, route_plan):
        allocation = self.constructor.patients_array[patient_removed][2]
        if allocation == 0: 
            route_plan.notAllocatedPatients.append(patient_removed)
        else: 
            route_plan.illegalNotAllocatedPatients.append(patient_removed) 
        del route_plan.allocatedPatients[patient_removed] 
           
        treatments_for_patient = self.constructor.patients_array[patient_removed][11]
        for possible_illegal_treatment in treatments_for_patient: 
            if possible_illegal_treatment in route_plan.illegalNotAllocatedTreatments: 
                route_plan.illegalNotAllocatedTreatments.remove(possible_illegal_treatment)
            visits_in_treatment = self.constructor.treatments_array[possible_illegal_treatment][18]
            for not_longer_illegal_visit in visits_in_treatment: 
                if not_longer_illegal_visit in list(route_plan.illegalNotAllocatedVisitsWithPossibleDays.keys()): 
                    del route_plan.illegalNotAllocatedVisitsWithPossibleDays[not_longer_illegal_visit]
                activities_in_visits = self.constructor.visits_array[not_longer_illegal_visit][14]
                for not_longer_illegal_activity  in activities_in_visits: 
                    if not_longer_illegal_activity in list(route_plan.illegalNotAllocatedActivitiesWithPossibleDays.keys()): 
                        del route_plan.illegalNotAllocatedActivitiesWithPossibleDays[not_longer_illegal_activity]

        return route_plan, None, True


    def updateDictionariesForRoutePlanTreatmentLevel(self, treatment_removed, route_plan):
        del route_plan.treatments[treatment_removed]

        last_treatment_for_patient = False
        patient_for_treatment = None
        for patient, treatments in list(route_plan.allocatedPatients.items()):
            if treatments == [treatment_removed]:
                last_treatment_for_patient = True 
            if treatment_removed in treatments: 
                patient_for_treatment = patient
                break
            
        #  Treatment is not last for patient
        if last_treatment_for_patient == False:   
            route_plan.allocatedPatients[patient_for_treatment].remove(treatment_removed) 
            route_plan.illegalNotAllocatedTreatments.append(treatment_removed) 

            visits_in_treatment = self.constructor.treatment_arrays[treatment_removed][18]
            for not_longer_illegal_visit in visits_in_treatment: 
                if not_longer_illegal_visit in list(route_plan.illegalNotAllocatedVisitsWithPossibleDays.keys()): 
                    del route_plan.illegalNotAllocatedVisitsWithPossibleDays[not_longer_illegal_visit]
                activities_in_visits = self.constructor.visits_array[not_longer_illegal_visit][14]
                for not_longer_illegal_activity  in activities_in_visits: 
                    if not_longer_illegal_activity in list(route_plan.illegalNotAllocatedActivitiesWithPossibleDays.keys()): 
                        del route_plan.illegalNotAllocatedActivitiesWithPossibleDays[not_longer_illegal_activity]
            
            return route_plan, None, True
        
        # hvis dette var siste treatmentet for denne pasienten 
        treatments_for_patient = self.constructor.patients_array[patient][11]
        for possible_illegal_treatment in treatments_for_patient: 
            if possible_illegal_treatment in route_plan.illegalNotAllocatedTreatments: 
                route_plan.illegalNotAllocatedTreatments.remove(possible_illegal_treatment)
        # Hele patienten slettes fra allocated dict
        
        return self.updateDictionariesForRoutePlanPatientLevel(patient_for_treatment, route_plan)
    
        
    

    def updateDictionariesForRoutePlanVisitLevel(self,  visit_removed, route_plan, original_day): 
        del route_plan.visits[visit_removed]

        last_visit_in_treatment = False
        treatment_for_visit = None 
        for treatment, visits in list(route_plan.treatments.items()):
            if visits == [visit_removed]: 
                last_visit_in_treatment = True 
            if visit_removed in visits: 
                treatment_for_visit = treatment
                break

        # Selected visit er del av treatment hvor flere visits ligger inne. Skal kun fjerne enkelt visit.
        if last_visit_in_treatment == False: 
            route_plan.treatments[treatment_for_visit].remove(visit_removed)
            route_plan.illegalNotAllocatedVisitsWithPossibleDays[visit_removed] = original_day
            #Fjerner aktiviteter som var ullovlige tidligere, men som nå er inkludert i det ulovlige visitet, og ikke står som egen uiloglig aktiviteter 
            activities_in_visits = self.constructor.visits_array[visit_removed][14]
            for not_longer_illegal_activity  in activities_in_visits: 
                if not_longer_illegal_activity in list(route_plan.illegalNotAllocatedActivitiesWithPossibleDays.keys()): 
                    del route_plan.illegalNotAllocatedActivitiesWithPossibleDays[not_longer_illegal_activity]
            
            return route_plan, None, True
        
        # Visit er siste i treatmentet, så skal slette på treatment nivå eller høyere

        return self.updateDictionariesForRoutePlanTreatmentLevel(treatment_for_visit, route_plan)
    
    def updateDictionariesForRoutePlanActivityLevel(self, activity_removed, route_plan, original_day):
        last_activity_in_visit = False
        visit_for_activity = None
        
        for visit, activities in list(route_plan.visits.items()):
            if activity_removed in activities:
                visit_for_activity = visit
                if len(activities) == 1:
                    last_activity_in_visit = True
                break

        if visit_for_activity is None:
            return route_plan, None, False

        # Case where it's not the last activity in the visit
        if not last_activity_in_visit:
            route_plan.visits[visit_for_activity].remove(activity_removed)  # Remove from visit dict
            route_plan.illegalNotAllocatedActivitiesWithPossibleDays[activity_removed] = original_day  # Add to illegal on Activity day mapping
            return route_plan, None, True

        # Handle the case where it's the last activity in the visit
        return self.updateDictionariesForRoutePlanVisitLevel(visit_for_activity, route_plan, original_day)
   

    def updateDictionariesForRoutePlanActivityLevelG(self,  activity_removed, route_plan, original_day): 
        last_activity_in_visit = False 
        visit_for_activity = None
        for visit, activities in list(route_plan.visits.items()): 
            if activities == [activity_removed]: 
                last_activity_in_visit = True 
            if activity_removed in activities:
                visit_for_activity = visit
                break

        #Alt 1, det er ikke den siste aktiviteten innne i for visitetet. -> Trenger ikke rokkere på noen av de andre. Har ingen søsken som ligger igjen 
        if last_activity_in_visit == False: 
            #print("Hopper inn i Alt 1")
            route_plan.visits[visit_for_activity].remove(activity_removed) #Fjernes fra visit dict 
            route_plan.illegalNotAllocatedActivitiesWithPossibleDays[activity_removed] = original_day #Legges til i illegal på Aktivitet
            return route_plan, None, True

        return self.updateDictionariesForRoutePlanVisitLevel(visit_for_activity, route_plan, original_day)



    def k_means_clustering(self, tuple_with_loc, n_clusters=2):
        coordinates = []
        unique_locs = {}
        
        # Aggregating and counting duplicate locations
        for _, loc in tuple_with_loc:
            if loc in unique_locs:
                unique_locs[loc] += 1
            else:
                unique_locs[loc] = 1

        # Preparing the data for clustering, considering unique locations
        for loc, count in unique_locs.items():
            coordinates.extend([loc] * count)
            
        coordinates = np.array(coordinates)

        # Adjusting the number of clusters if necessary
        actual_clusters = min(len(set(map(tuple, coordinates))), n_clusters)

        # Perform k-means clustering
        kmeans = KMeans(n_clusters=actual_clusters, random_state=0).fit(coordinates)
        labels = kmeans.labels_

        # Combine patient ids with their corresponding cluster label
        tuple_with_labels = [(pat[0], label) for pat, label in zip(tuple_with_loc, labels)]

        # Identify the indices of the activities in the smallest cluster
        cluster_sizes = {label: 0 for label in range(actual_clusters)}
        for _, label in tuple_with_labels:
            cluster_sizes[label] += 1
        smallest_cluster_label = min(cluster_sizes, key=cluster_sizes.get)
        selected_indices = [pat for pat, label in tuple_with_labels if label == smallest_cluster_label]

        return selected_indices
    

    def find_nearest_neighbors_with_kdtree(self, tuple_with_location):
            coordinates = []

            # Cleaning and parsing location data
            for _, loc in tuple_with_location:
                if isinstance(loc, str):
                    # This handles locations stored as strings, converting them to tuples
                    try:
                        loc = ast.literal_eval(loc)
                    except ValueError:
                        print(f"Error parsing location: {loc}")
                        continue
                # Assuming loc is now a tuple of (latitude, longitude)
                try:
                    lat, lon = loc
                    coordinates.append((lat, lon))
                except ValueError:
                    print(f"Invalid location format: {loc}")
                    continue

            coordinates = np.array(coordinates)

            # Construct KDTree and query for nearest neighbor distances
            if coordinates.size == 0:
                print("No valid coordinates provided.")
                return []

            tree = cKDTree(coordinates)
            nearest_neighbor_distances = tree.query(coordinates, k=2)[0][:, 1]
        
            return nearest_neighbor_distances