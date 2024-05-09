import pandas as pd
import os
import pickle

#ANTIBIOTICS CASE

antibiotics_data = True 
generate_new_data = False 
folder_name = 'data'

if antibiotics_data:
    print("ANTIBIOTICS DATA")
    from datageneration.employeeGenerationAntibiotics import *
    from datageneration.patientGenerationAntibiotics import *
    from config.construction_config_antibiotics import *

else: 
    #TODO: Complexity er ikke dobbeltsjekket i infusion casen, så dobbelt sjekk at denne gir comlexity verdier som virker troverdige
    #INFUSION THERAPY CASE
    print("INFUSION DATA")
    from datageneration.employeeGenerationInfusion import *
    from datageneration.patientGenerationInfusion import *
    from config.construction_config_infusion import *

from datageneration import distance_matrix

   # Function to load list from pickle
def load_array_from_pickle(filepath):
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
        if isinstance(data, pd.DataFrame):
            # If data is a DataFrame, convert it to a 2D array
            header = data.columns.values
            data_array = np.vstack([header, data.values])
            return data_array
        elif isinstance(data, np.ndarray):
            # If data is already an array, return it as is
            return data



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

     #ARRAYS FOR MORE EFFICIENT INFORMATION FETCHING
    employees_information_array = load_array_from_pickle(file_path_employees) #['professionalLevel' 'clinic' 'schedule']
    patients_information_array = load_array_from_pickle(file_path_patients) #['nTreatments' 'utility' 'allocation' 'employeeRestriction' 'continuityGroup' 'employeeHistory' 'heaviness' 'location' 'clinic' 'specialisationPreferred' 'extraSupport' 'treatmentsIds' 'nVisits' 'aggUtility' 'p_complexity' 'nActivities']
    treatments_information_array = load_array_from_pickle(file_path_treatments) #['patientId' 'patternType' 'pattern' 'visits' 'location' 'employeeRestriction' 'heaviness' 'utility' 'pattern_complexity' 'nActInTreat' 'allocation' 'employeeHistory' 'continuityGroup' 'clinic' 'specialisationPreferred' 'extraSupport' 't_complexity' 'complexity' 'visitsIds' 'nActivities' 'activitiesIds']
    visits_information_array = load_array_from_pickle(file_path_visits) #['treatmentId' 'patientId' 'clinic' 'specialisationPreferred' 'location' 'employeeRestriction' 'heaviness' 'utility' 'allocation' 'patternType' 'employeeHistory' 'continuityGroup' 'activities' 'v_complexity' 'activitiesIds']
    activities_information_array = load_array_from_pickle(file_path_activities)



