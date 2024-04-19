import pandas as pd
import os

from datageneration import employeeGeneration
from datageneration import patientGeneration 
from datageneration import distance_matrix
from config import construction_config


# DATA GENERATION

"""
#df_employees = employeeGeneration.employeeGenerator()          # For Night, Day and Evening shifts
df_employees = employeeGeneration.employeeGeneratorOnlyDay()    # For day shifts
df_patients_not_complete = patientGeneration.patientGenerator(df_employees)
df_treatments_not_complete = patientGeneration.treatmentGenerator(df_patients_not_complete)
df_visits_not_complete = patientGeneration.visitsGenerator(df_treatments_not_complete)
df_activities = patientGeneration.activitiesGenerator(df_visits_not_complete)
df_visits = patientGeneration.autofillVisit(df_visits_not_complete, df_activities)
df_treatments = patientGeneration.autofillTreatment(df_treatments_not_complete, df_visits, df_activities)
df_patients = patientGeneration.autofillPatient(df_patients_not_complete, df_treatments, df_activities)

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

'''
#TEST DATA - not randomly generated
df_activities  = pd.read_csv("data/test/ActivitiesNY.csv").set_index(["activityId"]) 
df_employees = pd.read_csv("data/test/EmployeesNY.csv").set_index(["employeeId"])
df_patients = pd.read_csv("data/test/PatientsNY.csv").set_index(["patientId"])
df_treatments = pd.read_csv("data/test/TreatmentsNY.csv").set_index(["treatmentId"])
df_visits = pd.read_csv("data/test/VisitsNY.csv").set_index(["visitId"])
'''
#GENERATING DISTANCE MATRIX
depot_row = pd.DataFrame({'activityId': [0], 'location': [construction_config.depot]})
depot_row = depot_row.set_index(['activityId'])
# Legger til depot_row i begynnelsen av df_activities
df_activities_depot = pd.concat([depot_row, df_activities], axis=0)

T_ij = distance_matrix.travel_matrix(df_activities_depot)

#ADDING TRAVEL DISTANCE TO TIME WINDOWS
#Update earliest and latest start times of activities to make sure it is possible to travel between activities and the depot if there is a pick-up and delivery
df_activities = patientGeneration.TimeWindowsWithTravel(df_activities, T_ij)


