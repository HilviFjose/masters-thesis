import os
import pandas as pd
import numpy as np

import sys
sys.path.append('C:\\Users\\gurl\\masters-thesis')

from config import construction_config

print("FILSTI: ", os.getcwd()+'\data')

#Kan eventuelt legges i en klasse: DataGenerator
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

def employeeGenerator():
    df_employees = pd.DataFrame(columns=['employeeId', 'professionLevel', 'schedule'])
    levels = construction_config.professionLevels
    probabilities = construction_config.professionLevelsProb

    for e in range(1, construction_config.E_num + 1):
        professionLevel = np.random.choice(levels, p=probabilities)
        #Her må schedule inn... Må sørge for at det fordeles greit OG at det er en sykepleier på alle vakter. 

        schedule = 0
        df_employees = df_employees._append({'employeeId': e, 
                                            'professionLevel': professionLevel, 
                                            'schedule': schedule}, ignore_index=True)
        
    #file_path = os.getcwd() + '\\data\\employees.csv'
    file_path = os.path.join(os.getcwd(), 'data', 'employees.csv')
    df_employees.to_csv(file_path, index=False)

    return df_employees

def patientGenerator():
    df_patients = pd.DataFrame(columns=['patientId', 'treatments', 'visits', 'activities', 'utility','employeeRestrictions', 'continuityGroup', 'employeeHistory', 'heaviness'])
    #Legg også inn aggregert utility basert på antall visits pasienten gjennomgår. 
    #for i in range(construction_config.P_num):

def patientGenerator2(df_activities):
    df_patients = pd.DataFrame(columns=['patientId', 'treatments', 'visits', 'activities', 'utility','employeeRestrictions', 'continuityGroup', 'employeeHistory', 'heaviness'])
    
    patients = df_activities['patientId'].unique()

    for patient_id in patients:
        patient_activities = df_activities[df_activities['patientId'] == patient_id]
        num_activities = len(patient_activities)
        num_visits = len(patient_activities['visitId'].unique())
        num_treatments = len(patient_activities['treatmentId'].unique())

        # Finn unike ansattrestriksjoner for pasienten
        employee_restrictions = patient_activities['employeeRestrictions'].unique()

        # Legg til rad for den gjeldende pasienten i df_patients
        df_patients = df_patients.append({
            'patientId': patient_id,
            'employeeRestrictions': employee_restrictions,
            'treatments': num_treatments,
            'visits': num_visits,
            'activities': num_activities
        }, ignore_index=True)

    #generer en lokasjon til pasient her i stedet for at det gjøres til aktivitetene? 

    return df_patients

def patientEmployeeContextGenerator(df_patients, df_employees):
    #Koble ansatte og pasienter sammen
    #Employee restrictions
    #Employee history
    return df_patients

#TESTING
activitiesGenerator()
employeeGenerator()