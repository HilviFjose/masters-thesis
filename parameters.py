import pandas as pd
import os

#ANTIBIOTICS CASE

antibiotics_data = True
generate_new_data = False
folder_name = 'data'

if antibiotics_data:
    #print("ANTIBIOTICS DATA")
    from datageneration.employeeGenerationAntibiotics import *
    from datageneration.patientGenerationAntibiotics import *
    from config.construction_config_antibiotics import *

else: 
    #TODO: Complexity er ikke dobbeltsjekket i infusion casen, så dobbelt sjekk at denne gir comlexity verdier som virker troverdige
    #INFUSION THERAPY CASE
    #print("INFUSION DATA")
    from datageneration.employeeGenerationInfusion import *
    from datageneration.patientGenerationInfusion import *
    from config.construction_config_infusion import *

from datageneration import distance_matrix

# DATA GENERATION
if generate_new_data: 
    #df_employees = employeeGeneration.employeeGenerator()      # For Night, Day and Evening shifts
    df_employees = employeeGeneratorOnlyDay()                   # For day shifts
    df_patients_not_complete = patientGenerator(df_employees)
    df_treatments_not_complete = treatmentGenerator(df_patients_not_complete)
    df_visits_not_complete = visitsGenerator(df_treatments_not_complete)
    df_activities = activitiesGenerator(df_visits_not_complete)
    df_visits = autofillVisit(df_visits_not_complete, df_activities)
    df_treatments = autofillTreatment(df_treatments_not_complete, df_visits, df_activities)
    df_patients = autofillPatient(df_patients_not_complete, df_treatments, df_activities)

    #correcting index to start at id 1
    df_patients = df_patients.set_index(["patientId"])
    df_treatments = df_treatments.set_index(["treatmentId"])
    df_visits = df_visits.set_index(["visitId"])
    df_activities = df_activities.set_index(["activityId"])  
    df_employees = df_employees.set_index(["employeeId"])

    #SAVE DATA GENERATED
    df_employees.to_pickle(os.path.join(os.getcwd(), folder_name, 'employees.pkl'))
    df_patients.to_pickle(os.path.join(os.getcwd(), folder_name, 'patients.pkl'))
    df_treatments.to_pickle(os.path.join(os.getcwd(), folder_name, 'treatments.pkl'))
    df_visits.to_pickle(os.path.join(os.getcwd(), folder_name, 'visits.pkl'))
    df_activities.to_pickle(os.path.join(os.getcwd(), folder_name, 'activities.pkl'))




else: 
    #RE-USE GENERATED DATA
    file_path_employees = os.path.join(os.getcwd(), folder_name, 'employees.pkl')
    df_employees = pd.read_pickle(file_path_employees)
    file_path_patients = os.path.join(os.getcwd(), folder_name, 'patients.pkl')
    df_patients = pd.read_pickle(file_path_patients)
    file_path_treatments = os.path.join(os.getcwd(), folder_name, 'treatments.pkl')
    df_treatments = pd.read_pickle(file_path_treatments)
    file_path_visits = os.path.join(os.getcwd(), folder_name, 'visits.pkl')
    df_visits = pd.read_pickle(file_path_visits)
    file_path_activities = os.path.join(os.getcwd(), folder_name, 'activities.pkl')
    df_activities = pd.read_pickle(file_path_activities)



#GENERATING DISTANCE MATRIX
if antibiotics_data: 
    depot_row = pd.DataFrame({'activityId': [0], 'location': [construction_config_antibiotics.depot]})
else: 
    depot_row = pd.DataFrame({'activityId': [0], 'location': [construction_config_infusion.depot]})

depot_row = depot_row.set_index(['activityId'])
# Legger til depot_row i begynnelsen av df_activities
df_activities_depot = pd.concat([depot_row, df_activities], axis=0)

T_ij = distance_matrix.travel_matrix(df_activities_depot)

#ADDING TRAVEL DISTANCE TO TIME WINDOWS
#Update earliest and latest start times of activities to make sure it is possible to travel between activities and the depot if there is a pick-up and delivery
df_activities = TimeWindowsWithTravel(df_activities, T_ij)

#TILDELE KLINIKKER TIL ANTIBIOTIKA-ANSATTE
'''
def update_clinic_assignments(df_employees, clinic_distribution):
    # Filtrere ut ansatte med profesjon 1 og de med profesjon > 1
    df_profession_1 = df_employees[df_employees['professionalLevel'] == 1]
    df_others = df_employees[df_employees['professionalLevel'] > 1]

    num_others = len(df_others)
    
    # Opprette en eksakt liste over klinikker basert på den forhåndsbestemte fordelingen
    total_clinics_needed = num_others
    clinics = []
    for i, fraction in enumerate(clinic_distribution):
        clinics += [i + 1] * int(round(fraction * total_clinics_needed))  # i+1 fordi klinikk indekser starter fra 1

    # Tilpasse til nøyaktig antall ansatte med profesjon > 1 hvis det er behov
    discrepancy = len(clinics) - total_clinics_needed
    if discrepancy > 0:
        clinics = clinics[:-discrepancy]  # Fjerne ekstra elementer fra slutten
    elif discrepancy < 0:
        additional_clinics = [-discrepancy * [i + 1] for i in range(len(clinic_distribution))]
        clinics += sum(additional_clinics, [])[:abs(discrepancy)]  # Legge til manglende elementer

    np.random.shuffle(clinics)  # Blande klinikker for å tildele tilfeldig

    # Oppdatere klinikk-kolonnen for ansatte med profesjon > 1
    df_others['clinic'] = clinics

    # Samle sammen de oppdaterte ansatte til en DataFrame
    df_updated = pd.concat([df_profession_1, df_others]).sort_index()

    # Lagre til CSV, inkludert index
    file_path = os.path.join(os.getcwd(), 'data', 'employees.csv')
    df_updated.to_csv(file_path, index=True)  # Her angir vi index=True for å inkludere index-kolonnen

    return df_updated

df_employees = update_clinic_assignments(df_employees, construction_config_antibiotics.clinicDistribution)
df_employees.to_pickle(os.path.join(os.getcwd(), folder_name, 'employees.pkl'))
print(df_employees)
'''
#SILO-BASED - DATASETS
'''
df_employees['clinic'] = df_employees['clinic'].replace(0, 2)
def find_employees_not_in_clinic(activity_clinic, employee_df):
    # Finn ansatte som ikke er i den samme klinikken som aktiviteten
    return employee_df[employee_df['clinic'] != activity_clinic].index.tolist()

# Oppdaterer df_activities uten å overskrive eksisterende restriksjoner
for idx, row in df_activities.iterrows():
    # Finn ansatte som ikke jobber i samme klinikk som aktiviteten
    restricted_employees = find_employees_not_in_clinic(row['clinic'], df_employees)
    
    # Sjekk om det allerede er en liste i 'employeeRestriction'
    if pd.isna(row['employeeRestriction']):
        df_activities.at[idx, 'employeeRestriction'] = restricted_employees
    else:
        # Slår sammen eksisterende liste med nye ansatteIDer, unngår duplikater
        existing_list = row['employeeRestriction']
        updated_list = list(set(existing_list + restricted_employees))
        df_activities.at[idx, 'employeeRestriction'] = updated_list

#selected_columns = df_activities[['clinic', 'employeeRestriction']]
#print(selected_columns)
#print(df_employees)
'''
#SILO-BASED WITH LOGISTIC EMPLOYEES WORKING CROSS-CLINIC - DATASETS
def find_employees_not_in_clinic(activity_clinic, employee_df):
    # Finn ansatte som ikke er i den samme klinikk som aktiviteten og som ikke har professionLevel = 1
    return employee_df[(employee_df['clinic'] != activity_clinic) & (employee_df['professionalLevel'] != 1)].index.tolist()

# Oppdaterer df_activities uten å overskrive eksisterende restriksjoner
for idx, row in df_activities.iterrows():
    # Finn ansatte som ikke jobber i samme klinikk som aktiviteten og som ikke har klinikk 0
    restricted_employees = find_employees_not_in_clinic(row['clinic'], df_employees)
    
    # Sjekk om det allerede er en liste i 'employeeRestriction'
    if pd.isna(row['employeeRestriction']):
        df_activities.at[idx, 'employeeRestriction'] = restricted_employees
    else:
        # Slår sammen eksisterende liste med nye ansatteIDer, unngår duplikater
        existing_list = row['employeeRestriction']
        updated_list = list(set(existing_list + restricted_employees))
        df_activities.at[idx, 'employeeRestriction'] = updated_list

selected_columns = df_activities[['clinic', 'employeeRestriction']]
print(selected_columns)
print(df_employees)


