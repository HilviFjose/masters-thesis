import pandas as pd
import os
import pickle
import numpy as np

#ANTIBIOTICS CASE
print("ANTIBIOTICS DATA")
from datageneration.employeeGenerationAntibiotics import *
from datageneration.patientGenerationAntibiotics import *
from config.construction_config_antibiotics import *
'''
#INFUSION THERAPY CASE
print("INFUSION DATA")
from datageneration.employeeGenerationInfusion import *
from datageneration.patientGenerationInfusion import *
from config.construction_config_infusion import *
'''
from datageneration import distance_matrix

data_folder = 'data'
employee_path = os.path.join(data_folder, 'employees.pkl')
patient_path = os.path.join(data_folder, 'patients.pkl')
treatment_path = os.path.join(data_folder, 'treatments.pkl')
visit_path = os.path.join(data_folder, 'visits.pkl')
activity_path = os.path.join(data_folder, 'activities.pkl')

list_paths = {
    'employees': os.path.join(data_folder, 'employees_list.pkl'),
    'patients': os.path.join(data_folder, 'patients_list.pkl'),
    'treatments': os.path.join(data_folder, 'treatments_list.pkl'),
    'visits': os.path.join(data_folder, 'visits_list.pkl'),
    'activities': os.path.join(data_folder, 'activities_list.pkl')
}

# Function to convert DataFrame to array
def dataframe_to_array(df):
    header = df.columns.values
    data = df.values
    return np.vstack([header, data])

# Function to save DataFrame as array
def save_df_as_array(df, filename):
    array_data = dataframe_to_array(df)
    with open(filename, 'wb') as f:
        pickle.dump(array_data, f)

# Function to load DataFrame from pickle
def load_df_from_pickle(filepath):
    return pd.read_pickle(filepath)

# Function to load list from pickle
def load_array_from_pickle(filepath):
    with open(filepath, 'rb') as f:
        return pickle.load(f)


# DATA GENERATION
"""
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
df_employees.to_pickle(os.path.join(os.getcwd(), 'data', 'employees.pkl'))
df_patients.to_pickle(os.path.join(os.getcwd(), 'data', 'patients.pkl'))
df_treatments.to_pickle(os.path.join(os.getcwd(), 'data', 'treatments.pkl'))
df_visits.to_pickle(os.path.join(os.getcwd(), 'data', 'visits.pkl'))
df_activities.to_pickle(os.path.join(os.getcwd(), 'data', 'activities.pkl'))

# Convert and save as lists
save_df_as_array(df_employees, list_paths['employees'])
save_df_as_array(df_patients, list_paths['patients'])
save_df_as_array(df_treatments, list_paths['treatments'])
save_df_as_array(df_visits, list_paths['visits'])
save_df_as_array(df_activities, list_paths['activities'])

"""
#RE-USE GENERATED DATA
file_path_employees = os.path.join(os.getcwd(), 'data', 'employees.pkl')
df_employees = pd.read_pickle(file_path_employees)
file_path_patients = os.path.join(os.getcwd(), 'data', 'patients.pkl')
df_patients = pd.read_pickle(file_path_patients)
file_path_treatments = os.path.join(os.getcwd(), 'data', 'treatments.pkl')
df_treatments = pd.read_pickle(file_path_treatments)
file_path_visits = os.path.join(os.getcwd(), 'data', 'visits.pkl')
df_visits = pd.read_pickle(file_path_visits)
file_path_activities = os.path.join(os.getcwd(), 'data', 'activities.pkl')
df_activities = pd.read_pickle(file_path_activities)

#ARRAYS FOR MORE EFFICIENT INFORMATION FETCHING
employees__information_array = load_array_from_pickle(list_paths['employees'])
patients_information_array = load_array_from_pickle(list_paths['patients'])
treatments_information_array = load_array_from_pickle(list_paths['treatments'])
visits_information_array = load_array_from_pickle(list_paths['visits'])
activities_information_array = load_array_from_pickle(list_paths['activities'])

#GENERATING DISTANCE MATRIX
depot_row = pd.DataFrame({'activityId': [0], 'location': [construction_config_antibiotics.depot]})
depot_row = depot_row.set_index(['activityId'])
# Legger til depot_row i begynnelsen av df_activities
df_activities_depot = pd.concat([depot_row, df_activities], axis=0)

T_ij = distance_matrix.travel_matrix(df_activities_depot)

#ADDING TRAVEL DISTANCE TO TIME WINDOWS
#Update earliest and latest start times of activities to make sure it is possible to travel between activities and the depot if there is a pick-up and delivery
df_activities = TimeWindowsWithTravel(df_activities, T_ij)


