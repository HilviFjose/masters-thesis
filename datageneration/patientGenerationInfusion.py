import os
import pandas as pd
import numpy as np
import random 

import sys
sys.path.append(os.path.join(os.path.split(__file__)[0],'..') )  #include subfolders

from config import construction_config_infusion
from datageneration import employeeGenerationInfusion

def locationGenerator(locations, radius_km, num_points):
    """Forklaring fra chatten:
    For å generere et bestemt antall punkter innenfor arealet av en sirkel, kan vi tilpasse tilnærmingen ved 
    å bruke en metode som lar oss plassere punkter tilfeldig, men innenfor grensene av sirkelens radius. 
    Denne metoden involverer å generere tilfeldige vinkler og radiuser for hvert punkt, slik at de faller innenfor 
    den definerte sirkelen. Dette sikrer at punktene er jevnt fordelt over hele området, ikke bare langs kanten.
    Vi kan bruke polar koordinatsystemet hvor et punkt er definert av en radius fra sentrum og en vinkel i forhold 
    til en referanseakse. For å oppnå dette, genererer vi tilfeldige vinkler (i radianer) og tilfeldige radiuser 
    (som en brøkdel av den totale radiusen), og konverterer deretter disse polar koordinatene til kartesiske 
    koordinater (latitude og longitude) for å passe inn i vår geografiske kontekst"""

    points = []
    for _ in range(num_points):
        # Velger en tilfeldig lokasjon fra listen
        lat, lon = random.choice(locations)

        # Genererer en tilfeldig vinkel og radius
        angle = random.uniform(0, 2 * np.pi)
        r = radius_km * np.sqrt(random.uniform(0, 1))
        
        # Konverterer radius til radianer basert på jordens radius
        r_in_radians = r / 6371
        
        # Beregner delta for latitude og longitude
        dlat = np.sin(angle) * r_in_radians
        dlon = np.cos(angle) * r_in_radians / np.cos(np.radians(lat))
        
        # Legger til de nye punktene ved å justere fra sentralpunktet
        new_lat = round(lat + np.degrees(dlat),4)
        new_lon = round(lon + np.degrees(dlon),4)
        
        points.append((new_lat, new_lon))
        
    return points


#TODO: gå gjennom presedens, same employee, location på aktiviteter for alle casene
#TODO: overstyre preferred specialisation
#TODO: Legge inn riktig fordeling mellom klinikker og fordeling på terapier
#TODO: Legge inn distribusjoner på pasienter (continuity, heaviness, utility)
#TODO: Legge inn at noen pasienter har flere typer terapier (15 % eller noe)

def patientGenerator(df_employees):
    patientIds = list(range(1, construction_config_infusion.P_num + 1))
    
    # Generate random location for each patient
    locations = locationGenerator(construction_config_infusion.refLoc, construction_config_infusion.area, construction_config_infusion.P_num)
    
    # Distribution of number of treatments per patient
    nTreatments = 1 #TODO må legge inn mulighet for at noen pasienter har flere treatments igjen

    # Distribuiton of therapy types
    num_antibiotic = int(construction_config_infusion.P_num * construction_config_infusion.therapyDistribution[0])
    num_nutrition = int(construction_config_infusion.P_num * construction_config_infusion.therapyDistribution[1])
    num_advanced = construction_config_infusion.P_num - (num_antibiotic + num_nutrition)
    therapy = (['antibiotics'] * num_antibiotic) + (['nutrition'] * num_nutrition) + (['advanced'] * num_advanced)
    np.random.shuffle(therapy) 

    # Distribution of utility, patient allocation, continuity group and heaviness for patients
    utility = np.random.choice(range(1, 4), size=construction_config_infusion.P_num, p=construction_config_infusion.utilityDistribution)
    continuityGroup = np.random.choice(range(1, 4), size=construction_config_infusion.P_num, p=construction_config_infusion.continuityDistribution)
    heaviness = np.random.choice(range(1, 4), size=construction_config_infusion.P_num, p=construction_config_infusion.heavinessDistribution)
    if construction_config_infusion.P_num <= 5* construction_config_infusion.E_num:
        print('Number of patients <= 5* number of employees')
        allocation = [1] * round(construction_config_infusion.P_num * construction_config_infusion.allocation)
    else:
        print('Number of patients > 5* number of employees')
        allocation = [1] * round(construction_config_infusion.E_num * 0.75)
    allocation.extend([0] * (construction_config_infusion.P_num - len(allocation)))
    random.shuffle(allocation)

    # Distribution of patients between clinics based on therapy type
    clinic_counts = {i+1: 0 for i in range(len(construction_config_infusion.clinicDistribution))}     # Initialiser en tellevariabel for antall pasienter tildelt hver klinikk
    clinics = []
    for t in therapy:
        possible_clinics = []
        if t == 'nutrition':
            possible_clinics = [i+1 for i, available in enumerate(construction_config_infusion.clinicsWithNutrition) if available]
        elif t == 'advanced':
            possible_clinics = [i+1 for i, available in enumerate(construction_config_infusion.clinicsWithAdvanced) if available]
        else:
            possible_clinics = list(range(1, len(construction_config_infusion.clinicDistribution) + 1))
        
        # Juster vektingen for mulige klinikker basert på ønsket fordeling og nåværende tildeling
        weights = [construction_config_infusion.clinicDistribution[i-1] - (clinic_counts[i] / construction_config_infusion.P_num) for i in possible_clinics]
        weights = [w if w > 0 else 0 for w in weights]  # Sørger for at vekter ikke blir negative
        if sum(weights) > 0:
            weights = [w / sum(weights) for w in weights]  # Normaliserer vekter
            chosen_clinic = np.random.choice(possible_clinics, p=weights)
        else:
            chosen_clinic = np.random.choice(possible_clinics)
        
        clinics.append(chosen_clinic)
        clinic_counts[chosen_clinic] += 1

    # Prepare DataFrame
    df_patients = pd.DataFrame({
        'patientId': patientIds,
        'therapy': therapy,
        'clinic': clinics,
        'nTreatments': nTreatments,
        'utility': utility,
        'allocation': allocation,
        'employeeRestriction': None,  
        'continuityGroup': continuityGroup,
        'employeeHistory': None,  
        'heaviness': heaviness,
        'location': locations,
        'specialisationPreferred': None,
        'extraSupport': 'no'
    })

    # Update preferred specialisations for some of the patients
    for clinic, group in df_patients.groupby('clinic'):
        if clinic == 1: 
            # Finn indeksene til pasientene i denne klinikken
            indexes = group.index
            # Beregn antallet pasienter som skal få oppdatert deres specialisationPreferred og extraSupport
            numSpecialisationPreferred = int(len(indexes) * construction_config_infusion.specialisationDistribution[0]) 
            numExtraSupport = int(len(indexes) * construction_config_infusion.patientExtraSupport[0])
            # Velg tilfeldige pasienter fra disse gruppene for oppdatering
            selectedSpecialisationPreferred = np.random.choice(indexes, size=numSpecialisationPreferred, replace=False)
            selectedExtraSupport = np.random.choice(indexes, size = numExtraSupport, replace=False)
            # Oppdater kun de valgte pasientene
            df_patients.loc[selectedSpecialisationPreferred, 'specialisationPreferred'] = 1
            df_patients.loc[selectedExtraSupport, 'extraSupport'] = 'yes'
        elif clinic == 2: 
            indexes = group.index
            numSpecialisationPreferred = int(len(indexes) * construction_config_infusion.specialisationDistribution[1]) 
            numExtraSupport = int(len(indexes) * construction_config_infusion.patientExtraSupport[1])
            selectedSpecialisationPreferred = np.random.choice(indexes, size=numSpecialisationPreferred, replace=False)   
            selectedExtraSupport = np.random.choice(indexes, size = numExtraSupport, replace=False)
            df_patients.loc[selectedSpecialisationPreferred, 'specialisationPreferred'] = 2
            df_patients.loc[selectedExtraSupport, 'extraSupport'] = 'yes'
        elif clinic == 3: 
            indexes = group.index
            numSpecialisationPreferred = int(len(indexes) * construction_config_infusion.specialisationDistribution[2]) 
            numExtraSupport = int(len(indexes) * construction_config_infusion.patientExtraSupport[2])
            selectedSpecialisationPreferred = np.random.choice(indexes, size=numSpecialisationPreferred, replace=False)
            selectedExtraSupport = np.random.choice(indexes, size = numExtraSupport, replace=False)
            df_patients.loc[selectedSpecialisationPreferred, 'specialisationPreferred'] = 3
            df_patients.loc[selectedExtraSupport, 'extraSupport'] = 'yes'
        elif clinic == 4: 
            indexes = group.index
            numSpecialisationPreferred = int(len(indexes) * construction_config_infusion.specialisationDistribution[3])
            numExtraSupport = int(len(indexes) * construction_config_infusion.patientExtraSupport[3]) 
            selectedSpecialisationPreferred = np.random.choice(indexes, size=numSpecialisationPreferred, replace=False)
            selectedExtraSupport = np.random.choice(indexes, size = numExtraSupport, replace=False)
            df_patients.loc[selectedSpecialisationPreferred, 'specialisationPreferred'] = 4
            df_patients.loc[selectedExtraSupport, 'extraSupport'] = 'yes'

        
    # Employee Restrictions
    num_restricted_patients = int(len(df_patients) * construction_config_infusion.employeeRestrict)      # 5 % of the patients have a restriction against an employee
    restricted_patient_indices = np.random.choice(df_patients.index, size=num_restricted_patients, replace=False) # Random patients get employee restrictions
    
    for index in restricted_patient_indices:
        random_employee_id = np.random.choice(df_employees['employeeId'])   # Random employees 
        list_employees = []
        list_employees.append(random_employee_id)
        df_patients.at[index, 'employeeRestriction'] = list_employees

    # Employee history  
    # Forhåndsinitialiserer employeeHistory for hver pasient basert på deres continuity_group
    for index, row in df_patients.iterrows():
        continuity_group = row['continuityGroup']
        if continuity_group == 1:
            continuity_score = construction_config_infusion.continuityScore[0]
        elif continuity_group == 2:
            continuity_score = construction_config_infusion.continuityScore[1]
        else:  # continuity_group == 3
            continuity_score = construction_config_infusion.continuityScore[2]
        
        df_patients.at[index, 'employeeHistory'] = {continuity_score: []}

    # Tilfeldig utvalg av pasienter får ansatthistorikk med faktiske ansatte #TODO: Sjekk ut hva som må gjøres her
    num_history_patients = int(len(df_patients) * construction_config_infusion.employeeHistory)
    history_patient_indices = np.random.choice(df_patients.index, size=num_history_patients, replace=False)

    for index in history_patient_indices:
        max_employees = 0
        continuity_group = df_patients.at[index, 'continuityGroup']
        if continuity_group == 1:
            max_employees = construction_config_infusion.preferredEmployees[0]
        elif continuity_group == 2:
            max_employees = construction_config_infusion.preferredEmployees[1]
        else:  # continuity_group == 3
            max_employees = construction_config_infusion.preferredEmployees[2]
        continuity_score, employeeIds = next(iter(df_patients.at[index, 'employeeHistory'].items()))

        #num_employees = np.random.randint(1, max_employees + 1)  # Tillater et antall ansatte i ansatthistorikken basert på continuity group
        random_employee_ids = np.random.choice(df_employees['employeeId'], size=max_employees, replace=False).tolist()
        
        # Siden employeeHistory allerede er initialisert, legger vi bare til de tilfeldige ansattes ID-er
        df_patients.at[index, 'employeeHistory'][continuity_score].extend(random_employee_ids)

    file_path = os.path.join(os.getcwd(), 'data', 'patients.csv')
    df_patients.to_csv(file_path, index=False)

    return df_patients

def treatmentGenerator(df_patients):
    df_treatments = pd.DataFrame(columns=['treatmentId', 'patientId', 'therapy', 'clinic', 'patternType','pattern','visits', 'location', 'employeeRestriction','heaviness','utility', 'pattern_complexity', 'nActInTreat'])

    # Generate rows for each treatment with the patientId
    expanded_rows = df_patients.loc[df_patients.index.repeat(df_patients['nTreatments'])].reset_index(drop=False)
    expanded_rows['treatmentId'] = range(1, len(expanded_rows) + 1)
    
    df_treatments['treatmentId'] = expanded_rows['treatmentId']
    df_treatments['patientId'] = expanded_rows['patientId']
    df_treatments['therapy'] = expanded_rows['therapy']
    df_treatments['clinic'] = expanded_rows['clinic']
    df_treatments['location'] = expanded_rows['location']
    df_treatments['employeeRestriction'] = expanded_rows['employeeRestriction']
    df_treatments['heaviness'] = expanded_rows['heaviness']
    df_treatments['utility'] = expanded_rows['utility']
    df_treatments['allocation'] = expanded_rows['allocation'] #Lagt til for Gurobi
    df_treatments['employeeHistory'] = expanded_rows['employeeHistory'] #Lagt til for Gurobi
    df_treatments['continuityGroup'] = expanded_rows['continuityGroup'] #Lagt til for Gurobi
    df_treatments['clinic'] = expanded_rows['clinic']
    df_treatments['specialisationPreferred'] = expanded_rows['specialisationPreferred']
    df_treatments['extraSupport'] = expanded_rows['extraSupport']

    # Generate pattern type for each treatment. Will decide the number of visits per treatment.
    for therapy, group in df_treatments.groupby('therapy'):
        if therapy == 'antibiotics':
            for idx, row in group.iterrows():
                if row['extraSupport'] == 'yes':
                    df_treatments.loc[idx, 'patternType'] = 1                       # Five days a week 
                else:
                    df_treatments.loc[idx, 'patternType'] = 4                       # Two days spread throughout the week
        if therapy == 'nutrition':
            for idx, row in group.iterrows():
                if row['extraSupport'] == 'yes':
                    patternType_choice = np.random.choice([1, 3], p=[0.5, 0.5])     # Five days a week or three days spread throughout the week 
                    df_treatments.loc[idx, 'patternType'] = patternType_choice
                else:
                    df_treatments.loc[idx, 'patternType'] = 6                       # One day a week
        else: #advanced 
            for idx, row in group.iterrows():
                patternType_choice = np.random.choice([5, 6], p=[0.5, 0.5])         # Two consecutive days or one day a week
                df_treatments.loc[idx, 'patternType'] = patternType_choice

    for index, row in df_treatments.iterrows():
        if row['patternType'] == 1:
            df_treatments.at[index, 'pattern'] = construction_config_infusion.patterns_5days
            df_treatments.at[index, 'visits'] = 5
            df_treatments.at[index, 'pattern_complexity'] = 1
        elif row['patternType'] == 3:
            df_treatments.at[index, 'pattern'] = construction_config_infusion.patterns_3days
            df_treatments.at[index, 'visits'] = 3
            df_treatments.at[index, 'pattern_complexity'] = 2
        elif row['patternType'] == 4:
            df_treatments.at[index, 'pattern'] = construction_config_infusion.pattern_2daysspread
            df_treatments.at[index, 'visits'] = 2
            df_treatments.at[index, 'pattern_complexity'] = 4
        elif row['patternType'] == 5:
            df_treatments.at[index, 'pattern'] = construction_config_infusion.patterns_2daysfollowing
            df_treatments.at[index, 'visits'] = 2
            df_treatments.at[index, 'pattern_complexity'] = 4
        else: #patternType 6
            df_treatments.at[index, 'pattern'] = construction_config_infusion.patterns_1day
            df_treatments.at[index, 'visits'] = 1
            df_treatments.at[index, 'pattern_complexity'] = 5

    file_path = os.path.join(os.getcwd(), 'data', 'treatments.csv')
    df_treatments.to_csv(file_path, index=False)

    return df_treatments

def visitsGenerator(df_treatments):
    df_visits = pd.DataFrame(columns=['visitId', 'treatmentId', 'patientId', 'therapy','activities', 'clinic', 'specialisationPreferred', 'location'])

    # Generate rows for each visit with the treatmentId and patientId
    expanded_rows = df_treatments.loc[df_treatments.index.repeat(df_treatments['visits'])].reset_index(drop=False)
    expanded_rows['visitId'] = range(1, len(expanded_rows) + 1)

    df_visits = expanded_rows[['visitId', 'treatmentId', 'patientId', 'therapy', 'clinic', 'specialisationPreferred','location']].copy()
    df_visits[['employeeRestriction', 'heaviness', 'utility', 'allocation', 'patternType', 'employeeHistory', 'continuityGroup']] = expanded_rows[['employeeRestriction', 'heaviness', 'utility', 'allocation', 'patternType', 'employeeHistory', 'continuityGroup']]
  
    # Distribution of number of activities per visit
    for treatmentId, group in df_visits.groupby('treatmentId'):
        visit_ids = group['visitId'].values
        # ANTIBIOTICS
        if group['therapy'].iloc[0] == 'antibiotics':
            if len(group) == 2:
                df_visits.loc[df_visits['visitId'].isin(visit_ids), 'activities'] = 5
            elif len(group) == 5:
                # Randomly choose the distribution of number of activities within the visits
                distributionOfActs = np.random.choice([1, 2, 3])
                if distributionOfActs == 1:
                    # Visit 1 and 4 have 5 activities
                    df_visits.loc[df_visits['visitId'].isin([visit_ids[0], visit_ids[3]]), 'activities'] = 5
                    df_visits.loc[df_visits['visitId'].isin([visit_ids[1], visit_ids[2], visit_ids[4]]), 'activities'] = 1
                elif distributionOfActs == 2:
                    # Visit 2 and 5 have 5 activities
                    df_visits.loc[df_visits['visitId'].isin([visit_ids[1], visit_ids[4]]), 'activities'] = 5
                    df_visits.loc[df_visits['visitId'].isin([visit_ids[0], visit_ids[2], visit_ids[3]]), 'activities'] = 1
                elif distributionOfActs == 3:
                    # Visit 1 and 5 have 5 activities
                    df_visits.loc[df_visits['visitId'].isin([visit_ids[0], visit_ids[4]]), 'activities'] = 5
                    df_visits.loc[df_visits['visitId'].isin([visit_ids[1], visit_ids[2], visit_ids[3]]), 'activities'] = 1
        
        # NUTRITION AND FLUIDS
        elif group['therapy'].iloc[0] == 'nutrition':
            df_visits.loc[df_visits['visitId'].isin(visit_ids), 'activities'] = 3
        
        # ADVANCED
        else:
            df_visits.loc[df_visits['visitId'].isin(visit_ids), 'activities'] = 3
    
    file_path = os.path.join(os.getcwd(), 'data', 'visits.csv')
    df_visits.to_csv(file_path, index=False)

    return df_visits

def activitiesGenerator(df_visits):
    df_activities = pd.DataFrame(columns=['activityId', 'patientId', 'activityType','numActivitiesInVisit','earliestStartTime', 'latestStartTime', 
                                          'duration', 'synchronisation', 'skillRequirement', 'clinic', 'nextPrece', 'prevPrece', 
                                          'sameEmployeeActivityId', 'visitId', 'treatmentId', 'location'])

    # Generate rows for each activity with the visitId, treatmentId and patientId
    expanded_rows = df_visits.loc[df_visits.index.repeat(df_visits['activities'])].reset_index(drop=False)
    expanded_rows['activityId'] = range(1, len(expanded_rows) + 1)

    df_activities['activityId'] = expanded_rows['activityId']
    df_activities['visitId'] = expanded_rows['visitId']
    df_activities['treatmentId'] = expanded_rows['treatmentId']
    df_activities['patientId'] = expanded_rows['patientId']
    df_activities['therapy'] = expanded_rows['therapy']
    df_activities['numActivitiesInVisit'] = expanded_rows['activities']
    df_activities['clinic'] = expanded_rows['clinic']
    df_activities['location'] = expanded_rows['location']
    df_activities['employeeRestriction'] = expanded_rows['employeeRestriction']
    df_activities['heaviness'] = expanded_rows['heaviness']
    df_activities['utility'] = expanded_rows['utility']
    df_activities['allocation'] = expanded_rows['allocation'] #Lagt til for Gurobi
    df_activities['patternType'] = expanded_rows['patternType'] #Lagt til for Gurobi
    df_activities['employeeHistory'] = expanded_rows['employeeHistory'] #Lagt til for Gurobi
    df_activities['continuityGroup'] = expanded_rows['continuityGroup'] #Lagt til for Gurobi
    df_activities['specialisationPreferred'] = expanded_rows['specialisationPreferred']

    # Distribute activities between healthcare activities 'H' and equipment activities 'E'
    # Generate precedence, same employee requirements and change location for pick-up and delivery at the hospital
    # Generate synchronised activities (for visits with 4 or 6 activities)     
    for treatId, groupT in df_activities['treatmentId']:
        # ANTIBIOTICS
        if groupT['therapy'].iloc[0] == 'antibiotics':
            for visitId, groupV in groupT.groupby('visitId'):
                if groupV['numActivitiesInVisit'].iloc[0] == 1:
                    activity_ids = groupV['activityId'].tolist()
                    df_activities.loc[df_activities['activityId'] == activity_ids[0], 'activityType'] = 'H'
                    df_activities.loc[df_activities['activityId'] == activity_ids[0], 'duration'] = 40         # Health
                    df_activities.loc[df_activities['activityId'] == activity_ids[0], 'skillRequirement'] = 2  

                elif groupV['numActivitiesInVisit'].iloc[0] == 3:
                    # For 3 activities with structure HEE 
                    highest_indices = groupV.sort_values(by='activityId', ascending=False).index[:2]     # The two activities with the highest id
                    df_activities.loc[highest_indices, 'activityType'] = 'E'
                    remaining_indices = groupV.index.difference(highest_indices)
                    df_activities.loc[remaining_indices, 'activityType'] = 'H'

                    # Precedence and time limit for pick-up and delivery at the start of the visit
                    activity_ids = groupV['activityId'].tolist()
                    pd_time = 90
                    df_activities.loc[df_activities['activityId'] == activity_ids[1], 'prevPrece'] = f"{activity_ids[-3]}: {pd_time}"
                    df_activities.loc[df_activities['activityId'] == activity_ids[2], 'prevPrece'] = f"{activity_ids[-2]}: {pd_time}, {activity_ids[0]}: {pd_time}"
                    df_activities.loc[df_activities['activityId'] == activity_ids[0], 'nextPrece'] = f"{activity_ids[-2]}: {pd_time}, {activity_ids[-1]}: {pd_time}"    # Pick-up and delivery at the end
                    df_activities.loc[df_activities['activityId'] == activity_ids[1], 'nextPrece'] = f"{activity_ids[-1]}: {pd_time}"                                   # Pick-up and delivery at the end
                    
                    # Same Employee Requirement for pick-up and delivery activities
                    df_activities.loc[df_activities['activityId'] == activity_ids[1], 'sameEmployeeActivityId'] = activity_ids[2]          # Start of the visit
                    df_activities.loc[df_activities['activityId'] == activity_ids[2], 'sameEmployeeActivityId'] = activity_ids[1]          # Start of the visit

                    # Overwrite location of the first activity (pick-up at the hospital)
                    df_activities.loc[df_activities['activityId'] == activity_ids[2], 'location'] = f'{construction_config_infusion.depot}' 

                    # Generate duration for the activities #TODO: Tenke hvordan disse skal settes
                    df_activities.loc[(df_activities['patternType'] == 1) & (df_activities['activityId'] == activity_ids[0]), 'duration'] = 90  # Health, for high demand patients
                    df_activities.loc[(df_activities['patternType'] == 4) & (df_activities['activityId'] == activity_ids[0]), 'duration'] = 60  # Health, for low demand patients
                    df_activities.loc[df_activities['activityId'] == activity_ids[1], 'duration'] = 10  # Equip
                    df_activities.loc[df_activities['activityId'] == activity_ids[2], 'duration'] = 10  # Equip

                    # Generate Skill Requirement for activities. Remember to divide between Equipment and Healthcare activities        
                    for activityType, groupA in df_activities.groupby('activityType'):
                        if activityType == 'H':
                            df_activities.loc[groupA.index, 'skillRequirement'] = 2

                else:
                    # For more than 5 activities - 'E' to the two last and two first activities (pick-up and delivery)
                    lowest_indices = groupV.sort_values(by='activityId').index[:2]                       # The two activities with the lowest id
                    highest_indices = groupV.sort_values(by='activityId', ascending=False).index[:2]     # The two activities with the highest id
                    df_activities.loc[lowest_indices, 'activityType'] = 'E'
                    df_activities.loc[highest_indices, 'activityType'] = 'E'
                    remaining_indices = groupV.index.difference(lowest_indices.union(highest_indices))
                    df_activities.loc[remaining_indices, 'activityType'] = 'H'  
                    
                    # Precedence and time limits for pick-up and delivery
                    activity_ids = groupV['activityId'].tolist()
                    pd_time1 = 120
                    pd_time2 = 90
                    df_activities.loc[df_activities['activityId'] == activity_ids[1], 'prevPrece'] = f"{activity_ids[0]}: {pd_time1}"                                           # Pick-up and delivery at the start
                    df_activities.loc[df_activities['activityId'] == activity_ids[2], 'prevPrece'] = f"{activity_ids[1]}: {pd_time1}, {activity_ids[0]}: {pd_time1}"       # Pick-up and delivery at the start
                    df_activities.loc[df_activities['activityId'] == activity_ids[-2], 'prevPrece'] = f"{activity_ids[-3]}: {pd_time2}, {activity_ids[1]}, {activity_ids[0]}"                                         # Pick-up and delivery at the end
                    df_activities.loc[df_activities['activityId'] == activity_ids[-1], 'prevPrece'] = f"{activity_ids[-2]}: {pd_time2}, {activity_ids[-3]}: {pd_time2}, {activity_ids[1]}, {activity_ids[0]}"    # Pick-up and delivery at the end

                    df_activities.loc[df_activities['activityId'] == activity_ids[0], 'nextPrece'] = f"{activity_ids[1]}: {pd_time1}, {activity_ids[2]}: {pd_time1}, {activity_ids[3]}, {activity_ids[4]}"       # Pick-up and delivery at the start
                    df_activities.loc[df_activities['activityId'] == activity_ids[1], 'nextPrece'] = f"{activity_ids[2]}: {pd_time1}, {activity_ids[3]}, {activity_ids[4]}"                                           # Pick-up and delivery at the start
                    df_activities.loc[df_activities['activityId'] == activity_ids[-3], 'nextPrece'] = f"{activity_ids[-2]}: {pd_time2}, {activity_ids[-1]}: {pd_time2}"    # Pick-up and delivery at the end
                    df_activities.loc[df_activities['activityId'] == activity_ids[-2], 'nextPrece'] = f"{activity_ids[-1]}: {pd_time2}"                                         # Pick-up and delivery at the end

                    # Same Employee Requirement for åick-up and delivery activities 
                    df_activities.loc[df_activities['activityId'] == activity_ids[0], 'sameEmployeeActivityId'] = activity_ids[1]      # The two first activities 
                    df_activities.loc[df_activities['activityId'] == activity_ids[1], 'sameEmployeeActivityId'] = activity_ids[0]
                    df_activities.loc[df_activities['activityId'] == activity_ids[-1], 'sameEmployeeActivityId'] = activity_ids[-2]    # The two last activities
                    df_activities.loc[df_activities['activityId'] == activity_ids[-2], 'sameEmployeeActivityId'] = activity_ids[-1]
                    
                    # Overwrite location of the first and last activity (pick-up and delivery at the hospital)
                    df_activities.loc[df_activities['activityId'] == activity_ids[0], 'location'] = f'{construction_config_infusion.depot}'     # Pick-up
                    df_activities.loc[df_activities['activityId'] == activity_ids[-1], 'location'] = f'{construction_config_infusion.depot}'    # Delivery
                
                    # Generate duration for the activities #TODO: Tenke hvordan disse skal settes
                    df_activities.loc[df_activities['activityId'] == activity_ids[0], 'duration'] = 10      # Equip
                    df_activities.loc[df_activities['activityId'] == activity_ids[1], 'duration'] = 10      # Equip
                    df_activities.loc[(df_activities['patternType'] == 1) & (df_activities['activityId'] == activity_ids[2]), 'duration'] = 60  # Health, for high demand patients
                    df_activities.loc[(df_activities['patternType'] == 4) & (df_activities['activityId'] == activity_ids[2]), 'duration'] = 40  # Health, for low demand patients
                    df_activities.loc[df_activities['activityId'] == activity_ids[3], 'duration'] = 10      # Equip
                    df_activities.loc[df_activities['activityId'] == activity_ids[4], 'duration'] = 10      # Equip

                    # Generate Skill Requirement for activities. Remember to divide between Equipment and Healthcare activities        
                    for activityType, groupA in df_activities.groupby('activityType'):
                        if activityType == 'H':
                            df_activities.loc[groupA.index, 'skillRequirement'] = 3

        # NUTRITION AND FLUIDS
        elif groupT['therapy'].iloc[0] == 'nutrition':
            for visitId, groupV in groupT.groupby('visitId'):
                # For 3 activities with structure EEH
                sorted_indices = group.sort_values(by='activityId').index[:2]  # The two activities with the lowest id
                df_activities.loc[sorted_indices, 'activityType'] = 'E'
                remaining_indices = group.index.difference(sorted_indices)
                df_activities.loc[remaining_indices, 'activityType'] = 'H'

                # Precedence and time limit for pick-up and delivery at the start of the visit
                activity_ids = groupV['activityId'].tolist()
                pd_time = 120
                df_activities.loc[df_activities['activityId'] == activity_ids[1], 'prevPrece'] = f"{activity_ids[0]}: {pd_time}"
                df_activities.loc[df_activities['activityId'] == activity_ids[2], 'prevPrece'] = f"{activity_ids[1]}: {pd_time}, {activity_ids[0]}: {pd_time}"
                df_activities.loc[df_activities['activityId'] == activity_ids[-2], 'nextPrece'] = f"{activity_ids[-1]}: {pd_time}"
                df_activities.loc[df_activities['activityId'] == activity_ids[0], 'nextPrece'] = f"{activity_ids[-2]}: {pd_time}, {activity_ids[-1]}: {pd_time}"
                
                # Same Employee Requirement for pick-up and delivery activities
                df_activities.loc[df_activities['activityId'] == activity_ids[0], 'sameEmployeeActivityId'] = activity_ids[1]          # Start of the visit
                df_activities.loc[df_activities['activityId'] == activity_ids[1], 'sameEmployeeActivityId'] = activity_ids[0]          # Start of the visit

                # Overwrite location of the first activity (pick-up at the hospital)
                df_activities.loc[df_activities['activityId'] == activity_ids[0], 'location'] = f'{construction_config_infusion.depot}' 
                    
                # Standard duration (overwritten for the healthcare activitiy within 1 of the visits within each treatment) 
                df_activities.loc[df_activities['activityId'] == activity_ids[0], 'duration'] = 10         # Equip
                df_activities.loc[df_activities['activityId'] == activity_ids[1], 'duration'] = 10         # Equip
                df_activities.loc[df_activities['activityId'] == activity_ids[2], 'duration'] = 40         # Health

                # Generate Skill Requirement for activities (overwritten for the healthcare activitiy within 1 of the visits within each treatment)     
                for activityType, groupA in df_activities.groupby('activityType'):
                    if activityType == 'H':
                        df_activities.loc[groupA.index, 'skillRequirement'] = 2

            # Overskrive noen parametere for 1 av visitene
            if groupT['patternType'].iloc[0] == 6:   # One day
                #Visit structure: EEH included cleaning
                activity_ids = groupV['activityId'].tolist()
                df_activities.loc[df_activities['activityId'] == activity_ids[2], 'duration'] = 60         # Health
                df_activities.loc[df_activities['activityId'] == activity_ids[2], 'skillRequirement'] = 3 

            elif (groupT['patternType'].iloc[0] == 3) or (groupT['patternType'].iloc[0] == 1): # Three days and five days
                #Visit structure: EEH included cleaning
                visit_ids = groupT['visitId'].unique()
                random_visit_id = np.random.choice(visit_ids)
                # Den siste raden som har dette 'visitId' tilsvarer helseaktiviteten
                specific_row = groupT[groupT['visitId'] == random_visit_id].iloc[-1]
                df_activities.loc[specific_row.name, 'duration'] = 60
                df_activities.loc[specific_row.name, 'skillRequirement'] = 3

        # ADVANCED
        else: 
            if groupT['patternType'].iloc[0] == 6:   # One day
                #Visit structure: EEH
                sorted_indices = groupT.sort_values(by='activityId').index[:2]  # The two activities with the lowest id
                df_activities.loc[sorted_indices, 'activityType'] = 'E'
                remaining_indices = groupT.index.difference(sorted_indices)
                df_activities.loc[remaining_indices, 'activityType'] = 'H'

                # Precedence and time limit for pick-up and delivery at the start of the visit
                activity_ids = groupT['activityId'].tolist()
                pd_time = 90
                df_activities.loc[df_activities['activityId'] == activity_ids[1], 'prevPrece'] = f"{activity_ids[0]}: {pd_time}"
                df_activities.loc[df_activities['activityId'] == activity_ids[2], 'prevPrece'] = f"{activity_ids[1]}: {pd_time}, {activity_ids[0]}: {pd_time}"
                df_activities.loc[df_activities['activityId'] == activity_ids[-2], 'nextPrece'] = f"{activity_ids[-1]}: {pd_time}"
                df_activities.loc[df_activities['activityId'] == activity_ids[0], 'nextPrece'] = f"{activity_ids[-2]}: {pd_time}, {activity_ids[-1]}: {pd_time}"
                
                # Same Employee Requirement for pick-up and delivery activities
                df_activities.loc[df_activities['activityId'] == activity_ids[0], 'sameEmployeeActivityId'] = activity_ids[1]          # Start of the visit
                df_activities.loc[df_activities['activityId'] == activity_ids[1], 'sameEmployeeActivityId'] = activity_ids[0]          # Start of the visit

                # Overwrite location of the first activity (pick-up at the hospital)
                df_activities.loc[df_activities['activityId'] == activity_ids[0], 'location'] = f'{construction_config_infusion.depot}' 
                    
                # Standard duration 
                df_activities.loc[df_activities['activityId'] == activity_ids[0], 'duration'] = 10         # Equip
                df_activities.loc[df_activities['activityId'] == activity_ids[1], 'duration'] = 10         # Equip
                df_activities.loc[df_activities['activityId'] == activity_ids[2], 'duration'] = 60         # Health

                # Generate Skill Requirement for activities      
                for activityType, groupA in df_activities.groupby('activityType'):
                    if activityType == 'H':
                        df_activities.loc[groupA.index, 'skillRequirement'] = 3
                
            elif groupT['patternType'].iloc[0] == 5: # Two consecutive days
                #Visit structure: First HEE, second EEH
                visit_ids = groupT['visitId'].unique()
                first_visit_id = visit_ids[0]
                second_visit_id = visit_ids[1]

                # First visit: HEE
                first_visit_activities = groupT[groupT['visitId'] == first_visit_id]
                sorted_indices_first = first_visit_activities.sort_values(by='activityId').index
                df_activities.loc[sorted_indices_first[0], 'activityType'] = 'H'
                df_activities.loc[sorted_indices_first[1:], 'activityType'] = 'E'
                
                # Correct activity_ids for first visit
                activity_ids = first_visit_activities['activityId'].tolist()  # Ensure this is for the first visit
                
                # Implementing the logic for the first visit
                pd_time = 120  # Precedence time for first visit
                df_activities.loc[df_activities['activityId'].isin([activity_ids[1]]), 'prevPrece'] = f"{activity_ids[0]}: {pd_time}"
                df_activities.loc[df_activities['activityId'].isin([activity_ids[2]]), 'prevPrece'] = f"{activity_ids[1]}: {pd_time}, {activity_ids[0]}: {pd_time}"
                df_activities.loc[df_activities['activityId'].isin([activity_ids[-2]]), 'nextPrece'] = f"{activity_ids[-1]}: {pd_time}"
                df_activities.loc[df_activities['activityId'].isin([activity_ids[0]]), 'nextPrece'] = f"{activity_ids[-2]}: {pd_time}, {activity_ids[-1]}: {pd_time}"
                
                # Same Employee Requirement for pick-up and delivery activities for first visit
                df_activities.loc[df_activities['activityId'].isin([activity_ids[1]]), 'sameEmployeeActivityId'] = activity_ids[2]
                df_activities.loc[df_activities['activityId'].isin([activity_ids[2]]), 'sameEmployeeActivityId'] = activity_ids[1]
                
                # Overwrite location and other properties for first visit
                df_activities.loc[df_activities['activityId'].isin([activity_ids[2]]), 'location'] = f'{construction_config_infusion.depot}'
                df_activities.loc[df_activities['activityId'].isin([activity_ids[0]]), 'duration'] = 30
                df_activities.loc[df_activities['activityId'].isin([activity_ids[1]]), 'duration'] = 10
                df_activities.loc[df_activities['activityId'].isin([activity_ids[2]]), 'duration'] = 10
                
                # Generate Skill Requirement for activities for first visit
                for activityType, groupA in df_activities.groupby('activityType'):
                    if activityType == 'H':
                        df_activities.loc[groupA.index, 'skillRequirement'] = 2

                # Second visit: EEH
                second_visit_activities = groupT[groupT['visitId'] == second_visit_id]
                sorted_indices_second = second_visit_activities.sort_values(by='activityId').index[:2]  # The two activities with the lowest id
                df_activities.loc[sorted_indices_second, 'activityType'] = 'E'
                remaining_indices_second = second_visit_activities.index.difference(sorted_indices_second)
                df_activities.loc[remaining_indices_second, 'activityType'] = 'H'
                
                # Correct activity_ids for second visit
                activity_ids = second_visit_activities['activityId'].tolist()  # Ensure this is for the second visit
                
                # Implementing the logic for the second visit
                pd_time = 90  # Precedence time for second visit
                df_activities.loc[df_activities['activityId'].isin([activity_ids[1]]), 'prevPrece'] = f"{activity_ids[0]}: {pd_time}"
                df_activities.loc[df_activities['activityId'].isin([activity_ids[2]]), 'prevPrece'] = f"{activity_ids[1]}: {pd_time}, {activity_ids[0]}: {pd_time}"
                df_activities.loc[df_activities['activityId'].isin([activity_ids[-2]]), 'nextPrece'] = f"{activity_ids[-1]}: {pd_time}"
                df_activities.loc[df_activities['activityId'].isin([activity_ids[0]]), 'nextPrece'] = f"{activity_ids[-2]}: {pd_time}, {activity_ids[-1]}: {pd_time}"
                
                # Same Employee Requirement for pick-up and delivery activities for second visit
                df_activities.loc[df_activities['activityId'].isin([activity_ids[0]]), 'sameEmployeeActivityId'] = activity_ids[1]
                df_activities.loc[df_activities['activityId'].isin([activity_ids[1]]), 'sameEmployeeActivityId'] = activity_ids[0]
                
                # Overwrite location and other properties for second visit
                df_activities.loc[df_activities['activityId'].isin([activity_ids[0]]), 'location'] = f'{construction_config_infusion.depot}'
                df_activities.loc[df_activities['activityId'].isin([activity_ids[0]]), 'duration'] = 10
                df_activities.loc[df_activities['activityId'].isin([activity_ids[1]]), 'duration'] = 10
                df_activities.loc[df_activities['activityId'].isin([activity_ids[2]]), 'duration'] = 60
                
                # Generate Skill Requirement for activities for second visit
                for activityType, groupA in df_activities.groupby('activityType'):
                    if activityType == 'H':
                        df_activities.loc[groupA.index, 'skillRequirement'] = 3

    # Overwrite heaviness, utility, continuity level and employee history for Equipment activities
    df_activities.loc[df_activities['activityTyoe'] == 'E', 'skillRequirement'] = 1
    df_activities.loc[df_activities['activityType'] == 'E', 'heaviness'] = 1
    df_activities.loc[df_activities['activityType'] == 'E', 'utility'] = 0
    df_activities.loc[df_activities['activityType'] == 'E', 'continuityGroup'] = 3
    df_activities.loc[df_activities['activityType'] == 'E', 'specialisationPreferred'] = None
    df_activities.loc[df_activities['activityType'] == 'E', 'employeeHistory'] = df_activities.loc[df_activities['activityType'] == 'E', 'employeeHistory'].apply(lambda x: {0: []})

    # Generate earliest and latest start times of activities
    for visitId, group in df_activities.groupby('visitId'):
        patternType = group['patternType'].iloc[0]  
        startDay = construction_config_infusion.startday / 60         # Tilsvarer klokka 8
        endDay = construction_config_infusion.endday / 60             # Tilsvarer klokka 16
        
        if patternType == 1:
            # Generer earliest start time som er på hel eller halv time mellom startDay og 2 timer før endDay
            startTimes = np.arange(startDay, endDay-2, 0.5)
            earliestStartTime = np.random.choice(startTimes)

            # Latest start time later 
            possibleLatestStartTimes = startTimes[startTimes > earliestStartTime]  # Sluttider etter valgt starttid
            if len(possibleLatestStartTimes) > 0: 
                latestStartTime = np.random.choice(possibleLatestStartTimes) 
            else:  
                latestStartTime = endDay 

            # For hvert starttidspunkt, generer et tilhørende tidsvindu på mellom 2 og 4 timer som også passer innenfor arbeidsdagen
            timeWindows = [(start, endDay) for start in startTimes for duration in np.arange(2, 4.5, 0.5) if start + duration <= endDay]
            chosenWindow = np.random.choice(range(len(timeWindows)))  # Velg et tilfeldig tidsvindu
            earliestStartTime, latestStartTime = timeWindows[chosenWindow]
        elif patternType == 4:
            # Bestem tidsvindu basert på fordelingen
            windowType = np.random.choice(['full', 'morning', 'afternoon'], p=[0.8, 0.1, 0.1])
            if windowType == 'full':
                earliestStartTime, latestStartTime = startDay, endDay
            elif windowType == 'morning':
                earliestStartTime, latestStartTime = startDay, startDay + 4  # 8-12
            else:  # afternoon
                earliestStartTime, latestStartTime = endDay - 4, endDay  # 12-16

        # Oppdater df_activities med de genererte tidene (konverter til minutter igjen)
        df_activities.loc[group.index, 'earliestStartTime'] = earliestStartTime * 60
        df_activities.loc[group.index, 'latestStartTime'] = latestStartTime * 60 
     
    #TODO: Finne ut hvordan dette skal være for antibiotica case
    # Generate complexity for treatments, visits and activities
    # Activity complexity - only based on duration and time windows
    #df_activities['a_complexity'] = round((df_activities['latestStartTime'] - df_activities['earliestStartTime']) / df_activities['duration'])
    #df_activities['a_complexity'] = ((df_activities['latestStartTime'] - df_activities['earliestStartTime']) / df_activities['duration']).round()
    df_activities['a_complexity'] = (df_activities['latestStartTime'] - df_activities['earliestStartTime']) / df_activities['duration']
    
    for treatmentId, treatment_group in df_activities.groupby('treatmentId'):       
        treatmentDuration = 0
        treatmentTimeWindow = 0
               
        for visitId, visit_group in treatment_group.groupby('visitId'):
            # Precedence visit
            v_preceRatio = 0
            if visit_group['nextPrece'].notna().sum() > 0:
                v_preceRatio = len(visit_group) / visit_group['nextPrece'].notna().sum()
            
            # Duration and time windows ratio - Visit
            visit_duration = visit_group['duration'].sum()
            treatmentDuration += visit_duration
            visitTimeWindow = visit_group['latestStartTime'].max() - visit_group['earliestStartTime'].min()
            treatmentTimeWindow += visitTimeWindow
            v_timeRatio = round(treatmentTimeWindow / treatmentDuration, 1)

            # Visit complexity
            v_complexity = len(visit_group) + v_timeRatio + v_preceRatio #TODO: Finne en måte å regne ut denne på
            df_activities.loc[df_activities['visitId'] == visitId, 'v_complexity'] = v_complexity

        # Duration and time windows ratio - Treatment
        t_timeRatio = round(treatmentTimeWindow / treatmentDuration, 1)

        # Precedence treatment
        numActInTreat = len(treatment_group)
        numActWithPrece = treatment_group['nextPrece'].notna().sum()
        t_preceRatio = 0
        if numActWithPrece > 0:     
            t_preceRatio = numActInTreat / numActWithPrece 

        # Treatment complexity
        t_complexity = int(numActInTreat + t_preceRatio + t_timeRatio) #TODO: Finne en måte å regne ut denne på
        df_activities.loc[df_activities['treatmentId'] == treatmentId, 'nActInTreat'] = numActInTreat
        #df_activities.loc[df_activities['treatmentId'] == treatmentId, 't_preceRatio'] = t_preceRatio
        #df_activities.loc[df_activities['treatmentId'] == treatmentId, 't_timeRatio'] = t_timeRatio
        df_activities.loc[df_activities['treatmentId'] == treatmentId, 't_complexity'] = t_complexity

    for patientId, patient_group in df_activities.groupby('patientId'):
        numActInPatient = len(patient_group)
        df_activities.loc[df_activities['patientId'] == patientId, 'nActInPatient'] = numActInPatient

    file_path = os.path.join(os.getcwd(), 'data', 'activities.csv')
    df_activities.to_csv(file_path, index=False)

    return df_activities

def autofillVisit(df_visits, df_activities):
    # Adding complexity to df_treatments calculated in df_activities
    v_complexity = df_activities[['visitId', 'v_complexity']].drop_duplicates()
    df_visits_merged = pd.merge(df_visits, v_complexity, on='visitId', how='left')

    #Adding acitivity ids
    activities_grouped = df_activities.groupby('visitId')['activityId'].apply(list).reset_index(name='activitiesIds')
    df_visits_merged = pd.merge(df_visits_merged, activities_grouped, on='visitId', how='left')

    file_path = os.path.join(os.getcwd(), 'data', 'visits.csv')
    df_visits_merged.to_csv(file_path, index=False)
    return df_visits_merged

def autofillTreatment(df_treatments, df_visits, df_activities):
    # Adding complexity to df_treatments calculated in df_activities
    t_complexity = df_activities[['treatmentId', 't_complexity']].drop_duplicates()
    df_treatments_merged = pd.merge(df_treatments, t_complexity, on='treatmentId', how='left')

    # Calculating complexity based on complexity in df_activities and df_treatments
    df_treatments_merged['complexity'] = df_treatments_merged['pattern_complexity'] + df_treatments_merged['t_complexity']

    # Adding visits Ids to df_treatments
    visits_grouped = df_visits.groupby('treatmentId')['visitId'].apply(list).reset_index(name='visitsIds')
    df_treatments_merged = pd.merge(df_treatments_merged, visits_grouped, on='treatmentId', how='left')

    #Adding number of activities per patient
    nActivities = df_activities.groupby('treatmentId').size().reset_index(name='nActivities')
    df_treatments_merged = pd.merge(df_treatments_merged, nActivities, on='treatmentId', how='left')

    # Adding list of activities for each treatment
    activities_list = df_activities.groupby('treatmentId')['activityId'].agg(list).reset_index(name='activitiesIds')
    df_treatments_merged = pd.merge(df_treatments_merged, activities_list, on='treatmentId', how='left')

    file_path = os.path.join(os.getcwd(), 'data', 'treatments.csv')
    df_treatments_merged.to_csv(file_path, index=False)
    
    return df_treatments_merged

def autofillPatient(df_patients, df_treatments, df_activities):
    #Treatment IDs
    treatments_grouped = df_treatments.groupby('patientId')['treatmentId'].apply(list).reset_index(name='treatmentsIds')

    # Beregner summen av 'visits' for hver 'patientID' i df_treatments
    visits_sum = df_treatments.groupby('patientId')['visits'].sum().reset_index(name='nVisits')

    # Slår sammen behandlings-IDer og totalt antall visits med df_patients
    df_patients_merged = pd.merge(df_patients, treatments_grouped, on='patientId', how='left')
    df_patients_merged = pd.merge(df_patients_merged, visits_sum, on='patientId', how='left')

    #Aggregated Utility - patient utility times the number of visits per patient
    df_patients_merged['aggUtility'] = df_patients_merged['nVisits'] * df_patients_merged['utility']

    # Adding complexity to df_patients as the complexity in sum of the complexity of all treatments per patient
    p_complexity = df_treatments.groupby('patientId')['complexity'].sum().reset_index(name='p_complexity')
    df_patients_merged = pd.merge(df_patients_merged, p_complexity, on='patientId', how='left')

    #Adding number of activities per patient
    nActivities = df_activities.groupby('patientId').size().reset_index(name='nActivities')
    df_patients_merged = pd.merge(df_patients_merged, nActivities, on='patientId', how='left')
    
    file_path = os.path.join(os.getcwd(), 'data', 'patients.csv')
    df_patients_merged.to_csv(file_path, index=False)

    return df_patients_merged

#TODO: Denne er ikke helt riktig nå, må ta hensyn til startDay!
def TimeWindowsWithTravel(df_activities, T_ij):
    T_ij_max = round(max([max(row) for row in T_ij]))          # Max travel distance between two activities
    print(f'T_ij_max: {T_ij_max} minutes')
    T_ij_max_depot = round(max(row[0] for row in T_ij))        # Max travel distance from the depot to an activity
    print(f'T_ij_max_depot: {T_ij_max_depot} minutes') 
    
    for visitId, group in df_activities.groupby('visitId'):
        # Total duration of all activities for a given visitId
        visit_duration = int(group['duration'].sum())

        #Earliest and latest possible starting times within a day
        startDay = construction_config_infusion.startday
        endDay = construction_config_infusion.endday
        latestPossible = endDay - visit_duration

        #Generated values without travel distances
        earliestStartTime = df_activities.loc[df_activities['visitId'] == visitId, 'earliestStartTime'] 
        latestStartTime = df_activities.loc[df_activities['visitId'] == visitId, 'latestStartTime'] 
        # TODO: Se på hvor mye slingringsmonn det er ønsket på tidsvinduer - Hvor stramme tidsvinduer skal vi tillate
        if group['numActivitiesInVisit'].iloc[0] >= 3 and group['numActivitiesInVisit'].iloc[0] <= 4:
            if (latestStartTime - earliestStartTime < (visit_duration + T_ij_max_depot)*1.5).any():     # Krever noe slingringsmonn 
                if (earliestStartTime > T_ij_max_depot).any() and (endDay - latestStartTime > T_ij_max_depot).any():
                    df_activities.loc[df_activities['visitId'] == visitId, 'earliestStartTime'] -= round(T_ij_max_depot/2)
                    df_activities.loc[df_activities['visitId'] == visitId, 'latestStartTime'] += round(T_ij_max_depot/2)
                elif (earliestStartTime < T_ij_max_depot).any():
                    df_activities.loc[df_activities['visitId'] == visitId, 'latestStartTime'] += T_ij_max_depot
                elif (endDay - latestStartTime < T_ij_max_depot).any():
                    df_activities.loc[df_activities['visitId'] == visitId, 'earliestStartTime'] -= T_ij_max_depot
        if group['numActivitiesInVisit'].iloc[0] >= 5:
            if (latestStartTime - earliestStartTime < (visit_duration + T_ij_max_depot*2)*1.5).any():   # Krever noe slingringsmonn 
                if (earliestStartTime > T_ij_max_depot).any() and (endDay - latestStartTime > T_ij_max_depot).any():
                    df_activities.loc[df_activities['visitId'] == visitId, 'earliestStartTime'] -= T_ij_max_depot
                    df_activities.loc[df_activities['visitId'] == visitId, 'latestStartTime'] += T_ij_max_depot
                elif (earliestStartTime < T_ij_max_depot*2).any():
                    df_activities.loc[df_activities['visitId'] == visitId, 'latestStartTime'] += T_ij_max_depot*2
                elif (endDay - latestStartTime < T_ij_max_depot*2).any():
                    df_activities.loc[df_activities['visitId'] == visitId, 'earliestStartTime'] -= T_ij_max_depot*2
        
        file_path = os.path.join(os.getcwd(), 'data', 'activitiesNewTimeWindows.csv')
        (df_activities.reset_index()).to_csv(file_path, index=False)
    return df_activities

def updateActivities(df_activities):

    #Update precedence

    #Update pickup and delivery times

    #Update duration
    #df_activities.loc[df_activities['activityType'] == 'E', 'duration'] = 5  
    #df_activities.loc[df_activities['activityType'] == 'H', 'duration'] = 20 

    #Updated csv-files
    file_path = os.path.join(os.getcwd(), 'data', 'activitiesUpdated.csv')
    (df_activities.reset_index()).to_csv(file_path, index=False)
    

    return df_activities

#TESTING

'''
df_employees = employeeGeneration.employeeGenerator()
df_patients = patientGenerator(df_employees)
df_treatments = treatmentGenerator(df_patients)
df_visits = visitsGenerator(df_treatments)
df_activities = activitiesGenerator(df_visits)
df_patients_filled = autofillPatient(df_patients, df_treatments)
df_treatments_filled = autofillTreatment(df_treatments, df_visits)
df_visits_filled = autofillVisit(df_visits, df_activities)
'''



