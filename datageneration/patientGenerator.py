import os
import pandas as pd
import numpy as np
import random 

import sys
sys.path.append( os.path.join(os.path.split(__file__)[0],'..') )  #include subfolders

from config import construction_config

def activitiesGenerator():
    #Opprinnelige kolonner fra i høst
    df_activities_prosjektoppgave = pd.DataFrame(columns=['activityId', 'patientId', 'earliestStartTime', 'latestStartTime', 
                                          'duration', 'synchronisation', 'skillRequirement', 'precedence', 
                                          'sameEmployeeActivityId', 'visitId', 'treatmentId', 
                                          'possiblePatterns', 'patternType', 'numOfVisits', 
                                          'utility', 'location', 'continuityGroup', 'heaviness'])
    
    #Noen av disse kolonnene skal ikke fylles med data i denne funksjonen, men i senere funksjoner: 
    #continuitygroup, heaviness (logistikkoppgaver må håndteres...), (location, om det ikke er henting/levering av utstyr på sykehus), utility (halveres for synch-aktiviteter)

    df_activities = pd.DataFrame(columns=['activityId', 'patientId', 'earliestStartTime', 'latestStartTime', 
                                          'duration', 'synchronisation', 'skillRequirement', 'precedence', 
                                          'sameEmployeeActivityId', 'visitId', 'treatmentId', 
                                          'possiblePatterns', 'patternType', 'numOfVisits'])

    
    #file_path = os.getcwd() +'\\data\\activities.csv'
    file_path = os.path.join(os.getcwd(), 'data', 'activities.csv')
    df_activities.to_csv(file_path, index=False)

    #for i in range(1, construction_config.P_num + 1):


    return df_activities

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
        #visits = [] #or number of visits for the patient
        visits = np.random.poisson(lam=construction_config.visitsPerTreatment, size=construction_config.P_num) #noe feil her
        utility.append(np.random.choice([j+1 for j in range(5)]))
        agg_utility.append(visits[i]*utility[i-1]) 
        continuityGroup.append(np.random.choice([j+1 for j in range(3)], p=construction_config.continuityDistribution))
        heaviness.append(np.random.choice([i+1 for i in range(5)], p=construction_config.heavinessDistribution))
        
        df_patients = df_patients._append({
                'patientId': i+1,
                'treatments': treatments[i],
                'visits': visits[i], #Dette skal endres
                'utility': utility[i],
                'agg_utility': agg_utility[i],
                'continuityGroup': continuityGroup[i],
                'heaviness': heaviness[i]
            }, ignore_index=True)

    file_path = os.path.join(os.getcwd(), 'data', 'patients.csv')
    df_patients.to_csv(file_path, index=False)

    return df_patients

def patientEmployeeContextGenerator(df_patients, df_employees):
    #Koble ansatte og pasienter sammen
    #Employee restrictions
    #Employee history
    return df_patients

#TESTING
#activitiesGenerator()
#patientGenerator()