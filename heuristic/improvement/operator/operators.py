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
                    try:
                        visit_utility_contribute += self.constructor.activities_df.loc[activity, 'utility']
                        visit_skilldiff_contribute += current_route_plan.getRouteSkillLevForActivityID(activity) - self.constructor.activities_df.loc[activity, 'skillRequirement']
                    except:
                        print("Unable to remove worst visi3", visit)
                        print("Activity making it hard", activity)           
                        print("Visit in route plan", current_route_plan.visits[visit])
                        print("Allocated patients in current route plan", current_route_plan.allocatedPatients)
                        print("Not allocated patients in current route plan", current_route_plan.notAllocatedPatients)
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
         
        print("FJERNER AKTIVITET ", selected_activity)
        
        #Vi vet at vi bare har valgt ett visit, så dagen vil være en 
        original_day = destroyed_route_plan.removeActivityIDgetRemoveDay(selected_activity)
        
        
     
    #To alternativer
        #1) Selected activity er en del av et visit der flere aktiviteter ligger inne. -> Legger til i illegalActivity
        #2) Selected activity er siste som ligger inne på visit, men visit er ikke det siste som ligger inne på treatment. -> Legger til i illegalVisits 
        #3) Visitet er det siste for ligger inne på treatment. -> Legger til i illegalTreatments
        #4) Treatmentet er det siste som ligger på pasienten. -> Pasienten ut av allokeringen, pasienten inn i notAllocated 

      
            #TODO: Finne ut om det har noe å si at det er den første aktivtene som blir flyttet ut 

        
        last_activity_in_visit = False 
        visit_for_activity = None 
        for visit, activities in list(destroyed_route_plan.visits.items()): 
            if activities == [selected_activity]: 
                last_activity_in_visit = True 
            if selected_activity in activities: 
                visit_for_activity = visit
                break

        #Alt 1, det er ikke den siste aktiviteten innne i for visitetet 
        if last_activity_in_visit == False: 
            #Sjer ingneting på pasientnivå
            #Sjer ingenting på treatment nivå 
            destroyed_route_plan.visits[visit_for_activity].remove(selected_activity) #Fjernes fra visit dict 
            destroyed_route_plan.illegalNotAllocatedActivitiesWithPossibleDays[selected_activity] = original_day #Legges til i illegalpå Aktivitet
            print("illegalNotAllocatedActivitiesWithPossibleDays", destroyed_route_plan.illegalNotAllocatedActivitiesWithPossibleDays)
            return destroyed_route_plan, None, True

        
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


        #ALTERNATIV 2
        if last_visit_in_treatment == False: 
            #Sjer ingenting på pasient nivå
            destroyed_route_plan.treatments[treatment_for_visit].remove(visit_for_activity) # Visit fjernes fra treatment dict 
            destroyed_route_plan.illegalNotAllocatedVisitsWithPossibleDays[visit_for_activity] = original_day #Legges til i illegalVisit with possible day 
            del destroyed_route_plan.visits[visit_for_activity] # Visit fjernes fra visit dict
            print("illegalNotAllocatedVisitsWithPossibleDays", destroyed_route_plan.illegalNotAllocatedVisitsWithPossibleDays)
           
            return destroyed_route_plan, None, True
    

        #Legger til treatmentet i illegal 
        last_treatment_for_patient = False
        patient_for_treatment = None
        for patient, treatments in list(destroyed_route_plan.allocatedPatients.items()):
            if treatments == [treatment_for_visit]:
                last_treatment_for_patient = True 
            if treatment_for_visit in treatments: 
                patient_for_treatment = patient
                break
        
        #TODO: Denn må fjerne flere så blir ikke riktig å ha her 
        #ALTERNATIV 3 
        if last_treatment_for_patient == False: 
            destroyed_route_plan.allocatedPatients[patient_for_treatment].remove(treatment_for_visit) #Treatment fjernes fra pasient 
            destroyed_route_plan.illegalNotAllocatedTreatments.append(treatment_for_visit) #Treatment legges til 
            del destroyed_route_plan.treatments[treatment_for_visit] #treatment fjernes fra treatment list med tilhørende visits
            del destroyed_route_plan.visits[visit_for_activity] #Fjerne vistet som lå under treatments 
            print("illegalNotAllocatedTreatments", destroyed_route_plan.illegalNotAllocatedTreatments)
         
            
            return destroyed_route_plan, None, True

     
        #AlTERNATIV 4 - dette var siste aktivtet for denne pasienten 
        destroyed_route_plan.notAllocatedPatients.append(patient_for_treatment) #Legger til pasienten i ikke allokert, 
        del destroyed_route_plan.allocatedPatients[patient_for_treatment] #Fjerner pasent fra allocated Patenst 
        del destroyed_route_plan.treatments[treatment_for_visit] #Fjerner treatmetnen fr treatmetns 
        del destroyed_route_plan.visits[visit_for_activity] #Fjerner visitet 
        print("notAllocatedPatients", destroyed_route_plan.notAllocatedPatients)
        return destroyed_route_plan, None, True


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
    Ma forsøke å lage repair funskjoner for repair på de forskjellige lagene 

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

                #Legger til aktiviteten på treatmentet 
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