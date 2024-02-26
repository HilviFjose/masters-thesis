from datageneration import employeeGeneration
from datageneration import patientGeneration 
from datageneration import distance_matrix

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

T_ij = distance_matrix.travel_matrix(df_activities)