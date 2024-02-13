import os
import pandas as pd
import numpy as np
import random 

import sys
sys.path.append( os.path.join(os.path.split(__file__)[0],'..') )  #include subfolders

from config import construction_config

#TODO: Legge inn at fordelinger ikke kan ta verdien 0. Pasienter kan ikke få null treatments osv.

def patientGenerator():
    df_patients = pd.DataFrame(columns=['patientId', 'treatments', 'visits', 'activities', 'utility', 'agg_utility','employeeRestrictions', 'continuityGroup', 'employeeHistory', 'heaviness'])
    #df_patients = pd.DataFrame(columns=['patientId', 'treatments','visits','utility','agg_utility','continuityGroup','heaviness'])
     
    patientId = []
    treatments = []
    utility = []
    agg_utility = []
    continuityGroup = []
    heaviness = []

    for i in range(construction_config.P_num):
        patientId.append(i+1)
        treatments = np.random.poisson(lam=construction_config.treatmentsPerPatient, size=construction_config.P_num)
        treatments = np.maximum(treatments, 1) #TODO: gjør at ingen pasienter har 0 treatments, MEN det gjør at snittet på antall treatments per pasient blir mye høyere enn planlagt.
        utility.append(np.random.choice([j+1 for j in range(5)]))
        #agg_utility.append(visits[i]*utility[i-1]) #Må flyttes ned til en annen funksjon etter at visits er generert.  
        continuityGroup.append(np.random.choice([j+1 for j in range(3)], p=construction_config.continuityDistribution))
        heaviness.append(np.random.choice([i+1 for i in range(5)], p=construction_config.heavinessDistribution))
        
        df_patients = df_patients._append({
                'patientId': i+1,
                'treatments': treatments[i],
                #'visits': visits[i], #Dette skal endres
                'utility': utility[i],
                #'agg_utility': agg_utility[i],
                'continuityGroup': continuityGroup[i],
                'heaviness': heaviness[i]
            }, ignore_index=True)

    file_path = os.path.join(os.getcwd(), 'data', 'patients.csv')
    df_patients.to_csv(file_path, index=False)

    return df_patients

def treatmentGenerator(df_patients):
    df_treatments = pd.DataFrame(columns=['treatmentId', 'patientId', 'patternType','pattern','visits'])

    # Generate rows for each treatment with the patientId
    expanded_rows = df_patients.loc[df_patients.index.repeat(df_patients['treatments'])].reset_index(drop=False)
    expanded_rows['treatmentId'] = range(1, len(expanded_rows) + 1)
    # Generate pattern type for each treatment. Will decide the number of visits per treatment.
    patternType = np.random.choice([i+1 for i in range(len(construction_config.patternTypes))], len(expanded_rows), p=construction_config.patternTypes)
    
    df_treatments['treatmentId'] = expanded_rows['treatmentId']
    df_treatments['patientId'] = expanded_rows['patientId']
    df_treatments['patternType'] = patternType

    for index, row in df_treatments.iterrows():
        #Fill rows with possible patterns
        if row['patternType'] == 1:
            df_treatments.at[index, 'pattern'] = construction_config.patterns_5days
            df_treatments.at[index, 'visits'] = 5
        elif row['patternType'] == 2:
            df_treatments.at[index, 'pattern'] = construction_config.patterns_4days
            df_treatments.at[index, 'visits'] = 4
        elif row['patternType'] == 3:
            df_treatments.at[index, 'pattern'] = construction_config.patterns_3days
            df_treatments.at[index, 'visits'] = 3
        elif row['patternType'] == 4:
            df_treatments.at[index, 'pattern'] = construction_config.pattern_2daysspread
            df_treatments.at[index, 'visits'] = 2
        elif row['patternType'] == 5:
            df_treatments.at[index, 'pattern'] = construction_config.patterns_2daysfollowing
            df_treatments.at[index, 'visits'] = 2
        else:
            df_treatments.at[index, 'pattern'] = construction_config.patterns_1day
            df_treatments.at[index, 'visits'] = 1
        
    file_path = os.path.join(os.getcwd(), 'data', 'treatments.csv')
    df_treatments.to_csv(file_path, index=False)

    return df_treatments

def visitsGenerator(df_treatments):
    df_visits = pd.DataFrame(columns=['visitId', 'treatmentId', 'patientId', 'activities'])

    # Generate rows for each visit with the treatmentId and patientId
    expanded_rows = df_treatments.loc[df_treatments.index.repeat(df_treatments['visits'])].reset_index(drop=False)
    expanded_rows['visitId'] = range(1, len(expanded_rows) + 1)

    df_visits['visitId'] = expanded_rows['visitId']
    df_visits['treatmentId'] = expanded_rows['treatmentId']
    df_visits['patientId'] = expanded_rows['patientId']

    #TODO: Skriv om dette til at det er en choice i stedet for en poisson-fordeling. Det gir f.eks. mye mer mening at det ofte er 5 aktiviteter enn 6 aktiviteter i et besøk. 
    # Distribution of number of activities per visit
    V_num = df_visits.shape[0]
    activities = np.random.poisson(lam=construction_config.activitiesPerVisit, size=V_num)
    # A minimum of 1 and maximum of 7 activities per visit. 
    activities = np.maximum(activities, 1) #TODO: gjør at ingen visits har 0 aktiviteter, MEN det gjør at snittet på antall aktivititeter per visit blir mye høyere enn planlagt.
    activities = np.minimum(activities, 7) 

    df_visits['activities'] = activities

    file_path = os.path.join(os.getcwd(), 'data', 'visits.csv')
    df_visits.to_csv(file_path, index=False)

    return df_visits

def activitiesGenerator(df_visits):
    #Opprinnelige kolonner fra i høst
    df_activities_prosjektoppgave = pd.DataFrame(columns=['activityId', 'patientId', 'earliestStartTime', 'latestStartTime', 
                                          'duration', 'synchronisation', 'skillRequirement', 'precedence', 
                                          'sameEmployeeActivityId', 'visitId', 'treatmentId', 
                                          'possiblePatterns', 'patternType', 'numOfVisits', 
                                          'utility', 'location', 'continuityGroup', 'heaviness'])
    
    #Noen av disse kolonnene skal ikke fylles med data i denne funksjonen, men i senere funksjoner: 
    #continuitygroup, heaviness (logistikkoppgaver må håndteres...), (location, om det ikke er henting/levering av utstyr på sykehus), utility (halveres for synch-aktiviteter)

    df_activities = pd.DataFrame(columns=['activityId', 'patientId', 'activityType','numActivitiesInVisit','earliestStartTime', 'latestStartTime', 
                                          'duration', 'synchronisation', 'skillRequirement', 'precedence', 
                                          'sameEmployeeActivityId', 'visitId', 'treatmentId', 'location'])

    # Generate rows for each activity with the visitId, treatmentId and patientId
    expanded_rows = df_visits.loc[df_visits.index.repeat(df_visits['activities'])].reset_index(drop=False)
    expanded_rows['activityId'] = range(1, len(expanded_rows) + 1)

    df_activities['activityId'] = expanded_rows['activityId']
    df_activities['visitId'] = expanded_rows['visitId']
    df_activities['treatmentId'] = expanded_rows['treatmentId']
    df_activities['patientId'] = expanded_rows['patientId']
    df_activities['numActivitiesInVisit'] = expanded_rows['activities']

    
    #TODO: Generate location for all activities. Kan gjøres på pasienter og så overstyre det her for pick-up/delivery i denne funksjonen.
    
    # Distribute activities between healthcare activities [H] and equipment activities [E]
    #TODO: Vurdere om det skal håndteres forskjellig ut fra om det er partall eller oddetall antall aktiviteter i et visit
    #TODO: Overstyre lokasjon for pick-up/delivery på sykehuset. 
    for visitId, group in df_activities.groupby('visitId'):
        if group['numActivitiesInVisit'].iloc[0] < 3:
            # For 1 to 2 activities: 60 % for Healthcare and 40 % for Equipment
            df_activities.loc[group.index, 'activityType'] = np.random.choice(['H', 'E'], size=len(group), p=[0.6, 0.4])
        elif group['numActivitiesInVisit'].iloc[0] >= 3 and group['numActivitiesInVisit'].iloc[0] <= 4:
            # For 3 to 4 activities
            if np.random.rand() < 0.5:
                # 50 % chance: The two first activities in the visit is a pick-up and delivery
                sorted_indices = group.sort_values(by='activityId').index[:2]  # Ta de to første etter sortering for laveste activityId
                df_activities.loc[sorted_indices, 'activityType'] = 'E'
                remaining_indices = group.index.difference(sorted_indices)
                df_activities.loc[remaining_indices, 'activityType'] = 'H'
            else:
                # 50 % chance: The two last activities in the visit is a pick-up and delivery
                sorted_indices = group.sort_values(by='activityId', ascending=False).index[:2]  # Ta de to første for høyeste activityId
                df_activities.loc[sorted_indices, 'activityType'] = 'E'
                remaining_indices = group.index.difference(sorted_indices)
                df_activities.loc[remaining_indices, 'activityType'] = 'H'
        else:
            # For more than 5 activities - 'E' to the two last and two first activities (pick-up and delivery)
            lowest_indices = group.sort_values(by='activityId').index[:2]  # De to med lavest activityId
            highest_indices = group.sort_values(by='activityId', ascending=False).index[:2]  # De to med høyest activityId
            df_activities.loc[lowest_indices, 'activityType'] = 'E'
            df_activities.loc[highest_indices, 'activityType'] = 'E'
            remaining_indices = group.index.difference(lowest_indices.union(highest_indices))
            df_activities.loc[remaining_indices, 'activityType'] = 'H'  

        # Generate duration of activities
        for activityType, group in df_activities.groupby('activityType'):
            if activityType == 'E':
                # Normal distribution for equipment activities
                mu = (construction_config.minDurationEquip + construction_config.maxDurationEquip) / 2
                sigma = (construction_config.maxDurationEquip - construction_config.minDurationEquip) / 6
                duration = np.random.normal(mu, sigma, len(group))
            else:
                # Normal distribution for healthcare activities
                mu = (construction_config.minDurationHealth + construction_config.maxDurationHealth) / 2
                sigma = (construction_config.maxDurationHealth - construction_config.minDurationHealth) / 6
                duration = np.random.normal(mu, sigma, len(group))
            
            # Integers and clipping to ensure duration within limits from config files
            duration_clipped = np.clip(np.round(duration), construction_config.minDurationEquip, construction_config.maxDurationEquip) if activityType == 'E' else np.clip(np.round(duration), construction_config.minDurationHealth, construction_config.maxDurationHealth)
            
            df_activities.loc[group.index, 'duration'] = duration_clipped
        
        # TODO: Generate earliest and latest start times of activities
        for visitId, group in df_activities.groupby('visitId'):
            # Total duration of all activities for a given visitId
            visit_duration = group['duration'].sum()

            #Earliest and latest possible starting times within a day
            earliestStartTimeDay = 0
            latestStartTimeDay = 1400

            #Alle aktiviteter i samme visit skal ha samme earliest and latest start time
            #Den samla varigheten (total duration for alle aktiviteter med et og samme visitId) må være mindre eller lik differansen mellom tidligst og senest mulig starttid. 
            #OG passe på at earliestStartTime < latestStartTime

        #TODO: Generate precedence and same employee requirements
        #TODO: Generate sync
        #TODO: Generate Skill Requirement for activities. Remember to divide between Equipment and Healthcare activities        

        file_path = os.path.join(os.getcwd(), 'data', 'activities.csv')
        df_activities.to_csv(file_path, index=False)

    return df_activities


def patientEmployeeContextGenerator(df_patients, df_employees):
    #Koble ansatte og pasienter sammen
    #Employee restrictions
    #Employee history
    return df_patients

def autofillPatient():
    #Legge inn det som er generert i senere funksjoner hvis nødvendig for å få fyllt ut alle kolonner i df_patients
    return

#TESTING
df_patients = patientGenerator()
df_treatments = treatmentGenerator(df_patients)
df_visits = visitsGenerator(df_treatments)
activitiesGenerator(df_visits)
