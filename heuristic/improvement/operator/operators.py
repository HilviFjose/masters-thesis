import pandas as pd
import copy
import math
import numpy.random as rnd 
import random 
import networkx as nx
from sklearn.cluster import KMeans


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
class Operators:
    def __init__(self, alns):
        self.destruction_degree = alns.destruction_degree # TODO: Skal vi ha dette?
        self.constructor = alns.constructor

        self.count = 0 


    '''
    Fremgangsmåte for å feilsøke: 
    Gå gjennom hver operator og sjekke om den oppdaterer riktig. Forsøke å lage en generalisert funskjonalitet som kan oppdateres
    Skrive testkode for å sjekke hvilke aktiviteter som er borte i de ulike kandidatene

    Når oppdateres dictonariene, virker som at det noen ganger tar bort to ganger 
    '''
#---------- REMOVE OPERATORS ----------
 
    def relatedIllegalRemovalAfterPatientRemoval(self, route_plan, patient): 
        for treatment in self.constructor.patients_df.loc[patient, 'treatmentsIds']: 
            if treatment in route_plan.illegalNotAllocatedTreatments: 
                route_plan.illegalNotAllocatedTreatments.remove(treatment)
                continue
            self.relatedIllegalRemovalAfterTreatmentRemoval(route_plan, treatment)
            
    def relatedIllegalRemovalAfterTreatmentRemoval(self, route_plan, treatment): 
        for visit in self.constructor.treatment_df.loc[treatment, 'visitsIds']:
            if visit in list(route_plan.illegalNotAllocatedVisitsWithPossibleDays.keys()): 
                del route_plan.illegalNotAllocatedVisitsWithPossibleDays[visit]
                continue 
            self.relatedIllegalRemovalAfterVisitRemoval(route_plan, visit)
           
    def relatedIllegalRemovalAfterVisitRemoval(self, route_plan, visit):
        for activity in self.constructor.visit_df.loc[visit, 'activitiesIds']: 
            if activity in list(route_plan.illegalNotAllocatedActivitiesWithPossibleDays.keys()): 
                del route_plan.illegalNotAllocatedActivitiesWithPossibleDays[activity]

    def remove_activites_from_route_plan(self, activities, route_plan):
        for day in range(1, route_plan.days +1): 
            for route in route_plan.routes[day]: 
                for act in route.route: 
                    if act.id in activities:
                        route.removeActivityID(act.id)

    def remove_activites_from_route_plan_and_get_day(self, activities, route_plan): 
        original_day = None
        for day in range(1, route_plan.days +1): 
            for route in route_plan.routes[day]: 
                for act in route.route: 
                    if act.id in activities:
                        route.removeActivityID(act.id)
                        original_day = day
        return original_day
    
    def movePatientToNotAllocated(self, destroyed_route_plan, patient): 
        del destroyed_route_plan.allocatedPatients[patient]
        destroyed_route_plan.notAllocatedPatients.append(patient)
            
        self.relatedIllegalRemovalAfterPatientRemoval(destroyed_route_plan, patient)

        return destroyed_route_plan, None, True 
    
    def moveTreatmentToIllegal(self, destroyed_route_plan,patient_for_treatment,  treatment): 
        destroyed_route_plan.allocatedPatients[patient_for_treatment].remove(treatment)
        destroyed_route_plan.illegalNotAllocatedTreatments.append(treatment)
        
        self.relatedIllegalRemovalAfterTreatmentRemoval(destroyed_route_plan, treatment)
        return destroyed_route_plan, None, True
    
    def moveVisitToIllegal(self, destroyed_route_plan, treatment_for_visit, visit, original_day):
        destroyed_route_plan.treatments[treatment_for_visit].remove(visit) 
        destroyed_route_plan.illegalNotAllocatedVisitsWithPossibleDays[visit] = original_day
        

        self.relatedIllegalRemovalAfterVisitRemoval(destroyed_route_plan, visit)

        return destroyed_route_plan, None, True
    

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
        
       
        #1- Finner aktivitenen som skal fjernes og 2 - fjerne på nivåene under og eget nivå
        for treatment in destroyed_route_plan.allocatedPatients[selected_patient]: 
            for visit in destroyed_route_plan.treatments[treatment]:
                removed_activities += destroyed_route_plan.visits[visit]
                del destroyed_route_plan.visits[visit]
            del destroyed_route_plan.treatments[treatment]
        
        '''
        Hvorfor skal vi her fjerne på eget nivå
        '''

        #2- Her fjernes aktivitetne fra selve ruten 
        self.remove_activites_from_route_plan(removed_activities, destroyed_route_plan)

        #3- Flytte i dict på dette nivået 4- fjern mulige relaterte illegal lenger ned i hierarkiet
        return self.movePatientToNotAllocated(destroyed_route_plan, selected_patient)
    

    
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
        
        #0 - Henter ut om det er siste 
        last_treatment_for_patient = False 
        patient_for_treatment = None
        for patient, treatments in list(destroyed_route_plan.allocatedPatients.items()):
            #Finne treatments i illegalNotAllocatedTreatments som også tilhører pasienten 
            if treatments == [selected_treatment]: 
                last_treatment_for_patient = True 
            if selected_treatment in treatments: 
                patient_for_treatment = patient 
                break 

            
        #1 - Finner aktivitetene som skal fjernes og fjerner lenger ned i hierarkiet og eget lag 
        for visit in destroyed_route_plan.treatments[selected_treatment]:
            removed_activities += destroyed_route_plan.visits[visit]
            del destroyed_route_plan.visits[visit]
        del destroyed_route_plan.treatments[selected_treatment]

        #2 - Fjerner aktivitene fra selve ruten 
        self.remove_activites_from_route_plan(removed_activities, destroyed_route_plan)
        
     
        #3.1 - Flytte i dict på dette nivået  4- fjern mulige relaterte illegal lenger ned i hierarkiet
        if last_treatment_for_patient == False: 
            return self.moveTreatmentToIllegal(destroyed_route_plan, patient_for_treatment, selected_treatment)
            
        #3.2 Flytte i dict på nivået over hvis siste  4- fjern mulige relaterte illegal lenger ned i hierarkiet
        return self.movePatientToNotAllocated(destroyed_route_plan, patient_for_treatment)
    
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

  
    def visit_removal(self, selected_visit, route_plan):

        destroyed_route_plan = copy.deepcopy(route_plan)
        removed_activities = [] 

        #0 - Henter ut om det er siste visit i treatment
        last_visit_in_treatment = False
        treatment_for_visit = None 
        for treatment, visits in list(destroyed_route_plan.treatments.items()):
            #Finne treatments i illegalNotAllocatedTreatments som også tilhører pasienten 
            if visits == [selected_visit]: 
                last_visit_in_treatment = True 
            if selected_visit in visits: 
                treatment_for_visit = treatment
                break

        #1 - Finnne aktivitetene som skal fjerens og fjerne lenger ned i hierakiet og eget lag 
        removed_activities += destroyed_route_plan.visits[selected_visit]
        del destroyed_route_plan.visits[selected_visit]

        #2 - Fjerner aktivitene fra sleve ruten 
        original_day = self.remove_activites_from_route_plan_and_get_day(removed_activities, destroyed_route_plan)
        
        #3.1 
        if last_visit_in_treatment == False: 
            return self.moveVisitToIllegal(destroyed_route_plan, treatment_for_visit, selected_visit, original_day)
                  
        
        '''
        OBS: Kan det hende at den trekker en aktivitet som ikke er allokert. 
        Eller kan den det? 
        '''

        #3.2  Sjekker om det er siste 
        last_treatment_for_patient = False
        patient_for_treatment = None
        for patient, treatments in list(destroyed_route_plan.allocatedPatients.items()):
            if treatments == [treatment_for_visit]:
                last_treatment_for_patient = True 
            if treatment_for_visit in treatments: 
                patient_for_treatment = patient
                break

        #del destroyed_route_plan.allocatedPatients[patient_for_treatment]
        
        if last_treatment_for_patient == False: 
            return self.moveTreatmentToIllegal(destroyed_route_plan, patient_for_treatment, treatment_for_visit)

        #3.3 
        return self.movePatientToNotAllocated(destroyed_route_plan, patient_for_treatment)
    

        


#RANDOM
    def random_activity_removal(self, route_plan): 
        selected_activity = rnd.choice([item for sublist in route_plan.visits.values() for item in sublist])
        return self.activity_removal(selected_activity, route_plan)

    #TODO: Finne ut hva vi skal ha på worst på aktivitetsnivå 
    def worst_deviation_activity_removal(self, route_plan): 

        lowest_activity_utility_contribute = 1000 
        highest_activity_skilldiff_contribute = 0
        highest_activity_travel_time = 0
        selected_activity = None 
        #Her er det kanskje letter å gå gjennom aktivitene i rutene 
        for day in range(1, route_plan.days +1): 
            for route in route_plan.routes[day]: 
                for activity_index in range(len(route.route)):
                    activity = route.route[activity_index] 
                    before_activity_id = 0 
                    after_actitivy_id = 0 
                    if activity_index != 0: 
                        before_activity_id = route.route[activity_index-1].id
                    if activity_index != len(route.route)-1: 
                        after_actitivy_id = route.route[activity_index+1].id
                    activity_utility_contribute = self.constructor.activities_df.loc[activity.id, 'utility']
                    activity_skilldiff_contribute = route_plan.getRouteSkillLevForActivityID(activity.id) - self.constructor.activities_df.loc[activity.id, 'skillRequirement']
                    activity_travel_time = T_ij[before_activity_id][activity.id] + T_ij[activity.id][after_actitivy_id] - T_ij[before_activity_id][after_actitivy_id]
                    if activity_utility_contribute < lowest_activity_utility_contribute or (
                        activity_utility_contribute == lowest_activity_utility_contribute and activity_skilldiff_contribute > highest_activity_skilldiff_contribute) or (
                            activity_utility_contribute == lowest_activity_utility_contribute and activity_skilldiff_contribute ==  highest_activity_skilldiff_contribute and activity_travel_time > highest_activity_travel_time):
                        lowest_activity_utility_contribute = activity_utility_contribute
                        highest_activity_skilldiff_contribute = activity_skilldiff_contribute
                        highest_activity_travel_time = activity_travel_time
                        selected_activity = activity.id
                      
                   
       
        return self.activity_removal(selected_activity, route_plan)


    def activity_removal(self, selected_activity, route_plan):

        destroyed_route_plan = copy.deepcopy(route_plan)
        
        #Vi vet at vi bare har valgt ett visit, så dagen vil være en 
        original_day = destroyed_route_plan.removeActivityIDgetRemoveDay(selected_activity)
        

        last_activity_in_visit = False 
        visit_for_activity = None 
        for visit, activities in list(destroyed_route_plan.visits.items()): 
            if activities == [selected_activity]: 
                last_activity_in_visit = True 
            if selected_activity in activities: 
                visit_for_activity = visit
                break

        #Alt 1 
        if last_activity_in_visit == False: 
            destroyed_route_plan.illegalNotAllocatedActivitiesWithPossibleDays[selected_activity] = original_day #Legges til i illegalpå Aktivitet
        
            destroyed_route_plan.visits[visit_for_activity].remove(selected_activity) #Fjernes fra visit dict 
            #Trenger ingen Illegalrelated å ta bort 
            return destroyed_route_plan, None, True

        #Alt 2
        last_visit_in_treatment = False
        treatment_for_visit = None 
        #Ønsker å finne treatmenten 
        for treatment, visits in list(destroyed_route_plan.treatments.items()):
            #Finne treatments i illegalNotAllocatedTreatments som også tilhører pasienten 
            if visits == [visit_for_activity]: 
                last_visit_in_treatment = True 
            if visit_for_activity in visits: 
                treatment_for_visit = treatment
                break

        del destroyed_route_plan.visits[visit_for_activity]

        
        if last_visit_in_treatment == False: 
            #Sjer ingenting på pasient nivå
            return self.moveVisitToIllegal(destroyed_route_plan, treatment_for_visit, visit_for_activity, original_day)
    
        #Alt 3
        #Legger til treatmentet i illegal 
        last_treatment_for_patient = False
        patient_for_treatment = None
        for patient, treatments in list(destroyed_route_plan.allocatedPatients.items()):
            if treatments == [treatment_for_visit]:
                last_treatment_for_patient = True 
            if treatment_for_visit in treatments: 
                patient_for_treatment = patient
                break
        
        del destroyed_route_plan.treatments[treatment_for_visit] #treatment fjernes fra treatment list med tilhørende visits
           

        if last_treatment_for_patient == False: 
            return self.moveTreatmentToIllegal(destroyed_route_plan, patient_for_treatment, treatment_for_visit)
     
        #Alt 4
        return self.movePatientToNotAllocated(destroyed_route_plan, patient_for_treatment)


    #TODO: Denne må testes opp mot gammel 
    def random_pattern_removal(self, current_route_plan):
        destroyed_route_plan = copy.deepcopy(current_route_plan)
        #Må endres når vi endrer pattern 
        selected_pattern = random.randint(1, len(patternTypes))
        selected_treatments = []
        for treatment in destroyed_route_plan.treatments.keys(): 
            pattern_for_treatment = self.constructor.treatment_df.loc[treatment,"patternType"]
            if pattern_for_treatment == selected_pattern: 
                selected_treatments.append(treatment)
        
        for treatment in selected_treatments: 
            destroyed_route_plan = self.treatment_removal(treatment, destroyed_route_plan)[0]
        
        return destroyed_route_plan, None, True

    

    
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

    def k_means_clustering(self, df, location_col='location', n_clusters=2):
        """
        Clusters activities based on their geographical coordinates using k-means clustering.
        n_clusters: Number of clusters to divide the data into, default is 2.

        Returns:
        - A list of indices for the activities in the smallest cluster.
        """

        # Preprocess data: location-column both string and tuple as type
        coordinates = []
        for x in df[location_col]:
            if isinstance(x, str):
                # Hvis x er en streng, fjern parenteser og splitt
                lat_str, lon_str = x.strip("()").split(",")
                lat, lon = float(lat_str), float(lon_str)
            elif isinstance(x, tuple):
                # Hvis x er en tuple, bruk verdien direkte
                lat, lon = x
            else:
                raise ValueError("Ukjent datatype i 'location'-kolonnen")
            coordinates.append((lat, lon))
        
        coordinates = np.array(coordinates)
        
        # Perform k-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(coordinates)
        labels = kmeans.labels_

        # Identify and select the indices of the activities in the smallest cluster
        df['cluster_label'] = labels  # Temporarily add a column for cluster labels
        cluster_sizes = df['cluster_label'].value_counts()
        smallest_cluster_label = cluster_sizes.idxmin()
        selected_indices = df[df['cluster_label'] == smallest_cluster_label].index.tolist()
        
        # Remove the temporary column
        df.drop(columns=['cluster_label'], inplace=True)

        return selected_indices


    def cluster_distance_patients_removal(self, current_route_plan):
        allocatedPatientsIds = list(current_route_plan.allocatedPatients.keys())

        df_selected_patients =  self.constructor.patients_df.loc[allocatedPatientsIds]

        #selected_patients = self.kruskalAlgorithm(df_selected_patients)[0]  #Selecting the shortest part of the mst       
        selected_patients = self.k_means_clustering(df_selected_patients)

        destroyed_route_plan = copy.deepcopy(current_route_plan)
        for patientID in selected_patients: 
            destroyed_route_plan = self.patient_removal(patientID, destroyed_route_plan)[0]

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

        #selected_activities = self.kruskalAlgorithm(df_selected_activities)[1] #Selecting the longest part of the mst
        selected_activities = self.k_means_clustering(df_selected_activities)

        destroyed_route_plan = copy.deepcopy(current_route_plan)
        self.remove_activites_from_route_plan(selected_activities, destroyed_route_plan)

        return destroyed_route_plan, selected_activities, True
    
    
#---------- REPAIR OPERATORS ----------
    

    '''
    Se på inserter til de ulike, sjekke at de har med hele logikken. 



    TODO: Skal vi ha insertor på hvert nivå, eller kan vi beholde den inserteren som er. 
    '''
    def illegal_activity_repair(self, repaired_route_plan): 
        activityIterationDict = copy.copy(repaired_route_plan.illegalNotAllocatedActivitiesWithPossibleDays)
        for activityID, day in activityIterationDict.items():
            activity = Activity(self.constructor.activities_df, activityID)
            repaired_route_plan.updateActivityBasedOnRoutePlanOnDay(activity, day)
            
            status = repaired_route_plan.addActivityOnDay(activity,day)
            if status == True: 
                del repaired_route_plan.illegalNotAllocatedActivitiesWithPossibleDays[activityID]

                #Legger til aktivitten på visitet over, trenger ikke legge til mer
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

                #Fjerner visitet som illegal Visits 
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

        #TODO: Skal vi rullere på hvilke funksjoner den gjør først? Det burde vel også vært i ALNS funksjonaliteten 
        #TODO: Må straffe basert på hva som ikke kommer inn. Den funksjonaliteten er ikke riktig 
    
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
                self.updateAllocationAfterPatientInsertor(repaired_route_plan, patient)
                repaired_route_plan = patientInsertor.route_plan
        
        
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


        #Fjerner pasienten fra ikkeAllokert listen 
        if patient in route_plan.notAllocatedPatients: 
            route_plan.notAllocatedPatients.remove(patient)


    def complexity_repair(self, destroyed_route_plan):
        #Tar bort removed acktivitites, de trenger vi ikk e
        repaired_route_plan = copy.deepcopy(destroyed_route_plan)
        
        
    
        #LEGGER TIL PASIENTER I RANDOM REKKEFØLGE 
        patientInsertor = Insertor(self.constructor, repaired_route_plan)
        descendingComplexityNotAllocatedPatientsDict =  {patient: self.constructor.patients_df.loc[patient, 'p_complexity'] for patient in repaired_route_plan.notAllocatedPatients}
        descendingComplexityNotAllocatedPatients = sorted(descendingComplexityNotAllocatedPatientsDict, key=descendingComplexityNotAllocatedPatientsDict.get)


        for patient in descendingComplexityNotAllocatedPatients: 
            status = patientInsertor.insert_patient(patient)
            
            if status == True: 
                repaired_route_plan = patientInsertor.route_plan
                self.updateAllocationAfterPatientInsertor(repaired_route_plan, patient)
        

        #TODO: Skal vi ha disse under i denne
        #TREATMENT ILLEGAL (forsøker legge inn illegal treatments )
        self.illegal_treatment_repair(repaired_route_plan)  

        #VISIT ILLEGAL (forsøker legge inn illegal visits )
        self.illegal_visit_repair(repaired_route_plan)

        #ACTIVITY ILLEGAL (forsøker legge inn illegal activites )
        self.illegal_activity_repair(repaired_route_plan)

        repaired_route_plan.updateObjective()
      
        return repaired_route_plan
    

    '''
    FORSTÅR IKKE HVA DETTE UNDER ER, KOMMENTERT UT 
  

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
    '''

    #TODO: Burde se på en operator som bytter å mye som mulig mellom to ansatte. Hvorfor det? 