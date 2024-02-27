import pandas as pd

from datageneration import employeeGeneration
from datageneration import patientGeneration 
from datageneration import distance_matrix

# DATA GENERATION
df_employees = employeeGeneration.employeeGenerator() 
df_patients = patientGeneration.patientGenerator(df_employees)
df_treatments = patientGeneration.treatmentGenerator(df_patients)
df_visits = patientGeneration.visitsGenerator(df_treatments)
df_activities = patientGeneration.activitiesGenerator(df_visits)
df_patients_filled = patientGeneration.autofillPatient(df_patients, df_treatments).set_index(["patientId"])
df_treatments_filled = patientGeneration.autofillTreatment(df_treatments, df_visits).set_index(["treatmentId"])
df_visits_filled = patientGeneration.autofillVisit(df_visits, df_activities).set_index(["visitId"])  
df_activities = df_activities.set_index(["activityId"])  
df_employees = df_employees.set_index(["employeeId"])

# Generating distance matrix
depot_row = pd.DataFrame({'activityId': [0], 'location': [(59.9365, 10.7396)]})
depot_row = depot_row.set_index(['activityId'])
# Legger til depot_row i begynnelsen av df_activities
df_activities_depot = pd.concat([depot_row, df_activities], axis=0)

# Viser de første radene i den nye DataFrame for å bekrefte at depotet er lagt til
T_ij = distance_matrix.travel_matrix(df_activities_depot)
print(df_activities_depot.head())
#print("T_ij Lengde: ",len(T_ij))
