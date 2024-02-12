import os
import pandas as pd
import numpy as np
import random 

import sys

sys.path.append( os.path.join(os.path.split(__file__)[0],'..') )  #include subfolders

#sys.path.append('C:\\Users\\gurol\\masters-thesis')

from config import construction_config

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

def generate_profession_levels(E_num, professionLevels, professionLevelsProb):
    pattern = []
    for index, level in enumerate(professionLevels):
        pattern.append(int(level*professionLevelsProb[index]*10))
    full_pattern = pattern * (E_num // len(pattern)) + pattern[:E_num % len(pattern)]
    return full_pattern


def assign_shifts(employees):
    shifts = {'night': [], 'day': [], 'evening': []} 
    level_3 = [e for e in employees if e[1] == 3]
    level_2 = [e for e in employees if e[1] == 2]
    level_1 = [e for e in employees if e[1] == 1]
    
    #All shifts have an employee with profession level 3
    shifts['day'].append(level_3.pop(0))
    shifts['night'].append(level_3.pop(0))
    shifts['evening'].append(level_3.pop(0))
    #All day shifts have at least one employee with profession level 2
    shifts['day'].append(level_2.pop(0))

    #Assigning all logistics employees to the day shift
    shifts['day'].extend(level_1)
        
    #Randomly distribute the remaining employees to shifts based on the distribution [0.1, 0.7, 0.2]
    remaining_employees = level_2 + level_3
    total_slots = len(remaining_employees)
    night_slots = round(total_slots * construction_config.E_num_night)
    day_slots = round(total_slots * construction_config.E_num_day) - len(shifts['day'])  # Adjusting for already assigned
    evening_slots = round(total_slots * construction_config.E_num_evening)

    #Shuffle the remaining employees for random assignment
    random.shuffle(remaining_employees)

    # Assign the remaining employees to shifts according to calculated slots
    shifts['night'].extend(remaining_employees[:night_slots])
    shifts['day'].extend(remaining_employees[night_slots:night_slots + day_slots])
    shifts['evening'].extend(remaining_employees[night_slots + day_slots:])

    return shifts


def employeeGeneratorNY():
    df_employees = pd.DataFrame(columns=['employeeId', 'professionLevel', 'schedule'])

    total_employees = construction_config.E_num
    levels = construction_config.professionLevels
    probabilities = construction_config.professionLevelsProb
    profession_levels = generate_profession_levels(total_employees, levels, probabilities)

    # Assigning shifts for 1 day
    employees = []
    for index, level in enumerate(profession_levels): 
        employees.append([index+1, level])

    shifts_assignment = assign_shifts(employees) #dette er for 1 dag

    for e in employees: 
        schedule = []
    
        df_employees = df_employees._append({
            'employeeId': e,
            'professionLevel': profession_levels[e],
            'schedule': schedule
        })
    
    file_path = os.path.join(os.getcwd(), 'data', 'employees.csv')
    df_employees.to_csv(file_path, index=False)
    
    return df_employees



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
        
    file_path = os.path.join(os.getcwd(), 'data', 'employees.csv')
    df_employees.to_csv(file_path, index=False)

    return df_employees

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
employeeGeneratorNY()
#patientGenerator()