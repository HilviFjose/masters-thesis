import os
import sys
import pandas as pd
import re
import json
from parameters import T_ij

# Set the path to include parent directory
sys.path.append(os.path.join(os.path.split(__file__)[0], '..'))

from config import main_config
from datageneration import distance_matrix

def read_travel_time(filepath):
    """Read and return the travel time from the results file."""
    with open(filepath, 'r') as file:
        text = file.read()
    run_time = int(re.search(r"Travel Time: (\d+)", text).group(1))
    return run_time

def extract_activity_ids(filepath):
    """Extract activity IDs from the results file based on the provided KPIs information."""
    with open(filepath, 'r') as file:
        text = file.read()
    activity_ids = re.findall(r"Activities: \[(.*?)\]", text)
    return list(map(int, activity_ids[0].split(','))) if activity_ids else []

def extract_patient_ids(filepath):
    """Extract patient IDs from the results file based on the provided KPIs information."""
    with open(filepath, 'r') as file:
        text = file.read()
    patient_ids = re.findall(r"Allocated patients: \[(.*?)\]", text)
    return list(map(int, patient_ids[0].split(','))) if patient_ids else []

#--------------IDLE TIME OG HEALTH TIME -----------------
def calculate_total_activity_duration(activities_filepath, activity_ids):
    """Calculate the total duration of filtered activities."""
    activities = pd.read_csv(activities_filepath)
    filtered_activities = activities[activities['activityId'].isin(activity_ids)]
    return filtered_activities['duration'].sum()

def calculate_total_health_activity_duration(activities_filepath, activity_ids):
    """Calculate the total duration of healthcare activities."""
    activities = pd.read_csv(activities_filepath)
    # Filter both on activity IDs and activity type 'H'
    filtered_activities = activities[(activities['activityId'].isin(activity_ids)) & (activities['activityType'] == 'H')]
    return filtered_activities['duration'].sum()

def logistic_employees_activities(results_filepath, logistic_employees_list):
    """Find the activities performed by logistic employees."""
    with open(results_filepath, 'r') as file:
        data = file.readlines()
    all_routes = []
    current_route = None
    capture = False
    for line in data:
        # Sjekk om linjen indikerer starten på en ny ansatt sin dag
        if 'ANSATT' in line:
            if capture and current_route is not None:
                # Legg til den fullførte ruten for forrige ansatt
                all_routes.append(current_route)
            employee_number = int(line.split()[3])  # Antagelse at formatet er "DAG X ANSATT Y"
            if employee_number in logistic_employees_list:
                capture = True  # Start opptak av aktiviteter
                current_route = []  # Start en ny rute for den ansatte
            else:
                capture = False  # Stopp opptak av aktiviteter
                current_route = None
        if capture and 'activity' in line:
            activity_id = int(line.split()[1])  # Antagelse at formatet er "activity Z start T"
            current_route.append(activity_id)
    # Legg til den siste ruten hvis det er en pågående rute
    if capture and current_route is not None:
        all_routes.append(current_route)
    return all_routes

def get_logistic_employees(employees_filepath):
    employees = pd.read_csv(employees_filepath)
    logistic_employees = employees[employees['professionalLevel'] == 1]
    return logistic_employees['employeeId'].tolist()

def count_unique_employees(employees_filepath):
    """Count the number of unique employees from the employees file."""
    employees = pd.read_csv(employees_filepath)
    return employees['employeeId'].nunique()

def partial_travel_time(activity_ids):
    from_act = 0 
    travel_time = 0 
    activity_ids.append(0)
    for actID in activity_ids: 
        travel_time +=  T_ij[from_act][actID]
        from_act = actID
    return travel_time

def calculate_idle_time(results_filepath, activities_filepath, employees_filepath):
    """Calculate the idle time based on travel time, total activity duration, and number of employees."""
    travel_time = read_travel_time(results_filepath)
    activity_ids = extract_activity_ids(results_filepath)
    total_activity_duration = calculate_total_activity_duration(activities_filepath, activity_ids)
    num_employees = count_unique_employees(employees_filepath)
    #print(f'travel time {travel_time}, duration {total_activity_duration}, working time {5*8*60*num_employees}')
    idle_time = (travel_time + total_activity_duration) / (5 * 8 * 60 * num_employees)
    print(f'num employees {num_employees}')
    return idle_time


def calculate_idle_time_for_profession_levels(results_filepath, activities_filepath, employees_filepath):
    
    activity_ids = extract_activity_ids(results_filepath)
    logistic_employees = get_logistic_employees(employees_filepath)
    activity_ids_logistic  = logistic_employees_activities(results_filepath, logistic_employees)
    flat_activity_ids_logistic = [item for sublist in activity_ids_logistic for item in sublist]
    activity_ids_health_workers_nurses = [item for item in activity_ids if item not in flat_activity_ids_logistic]
    
    travel_time_logistic = 0
    for list in activity_ids_logistic:
        travel_time_logistic += partial_travel_time(list) #Gitt at det bare er en logistikkansatt!
    travel_time_health = read_travel_time(results_filepath) - travel_time_logistic
    #print(f"travel time logistic {travel_time_logistic}, health {travel_time_health}, total {read_travel_time(results_filepath)}")
    
    duration_logistic = calculate_total_activity_duration(activities_filepath, flat_activity_ids_logistic)
    duration_health = calculate_total_activity_duration(activities_filepath, activity_ids_health_workers_nurses)
    #print(f"duration logistic {duration_logistic}, health {duration_health}, total {duration_health+duration_logistic}")

    idle_time_logistic = (travel_time_logistic + duration_logistic) / (5 * 8 * 60)
    num_health_employees = count_unique_employees(employees_filepath) - 1
    idle_time_health = (travel_time_health + duration_health) / (5 * 8 * 60 * num_health_employees)

    return idle_time_logistic, idle_time_health

def calculate_healthcare_time(results_filepath, activities_filepath, employees_filepath):
    """Calculate the healthcare time based on travel time, total activity duration, and total health activity duration."""
    all_activity_ids = extract_activity_ids(results_filepath)
    total_activity_duration = calculate_total_activity_duration(activities_filepath, all_activity_ids)

    logistic_employees = get_logistic_employees(employees_filepath)
    logistic_performed_activity_ids = logistic_employees_activities(results_filepath, logistic_employees)
    activity_duration_performed_by_logistic = 0
    for list in logistic_performed_activity_ids:
        activity_duration_performed_by_logistic += calculate_total_activity_duration(activities_filepath, list)
    activity_duration_performed_by_health = total_activity_duration - activity_duration_performed_by_logistic
    total_health_duration = calculate_total_health_activity_duration(activities_filepath, all_activity_ids)

    travel_time_by_logistic = 0
    for list in logistic_performed_activity_ids:
        travel_time_by_logistic += partial_travel_time(list) #Gitt at det bare er en logistikkansatt!

    total_travel_time = read_travel_time(results_filepath)  
    total_travel_time_by_health = total_travel_time - travel_time_by_logistic

    #print(f'total travel time {total_travel_time}, travel time health {total_travel_time_by_health}, duration activities performed by health personnel {activity_duration_performed_by_health}, duration health activities {total_health_duration}')
    if (activity_duration_performed_by_health + total_travel_time_by_health) == 0:
        return 0  # To avoid division by zero
    
    return total_health_duration / (activity_duration_performed_by_health + total_travel_time_by_health)


#-------------- EFFICIENCY OF ROUTES -----------------
def calculate_route_efficiency(results_filepath, activities_filepath):
    """Calculate the efficiency of routes based on on travel time and hypothetical travel time."""
    
    file_path_visits = os.path.join(os.getcwd(), folder_name, 'visits.pkl')
    df_visits = pd.read_pickle(file_path_visits)

    depot_row = pd.DataFrame({'visitId': [0], 'location': [main_config.depot]})
    depot_row = depot_row.set_index(['visitId'])
    df_visits_depot = pd.concat([depot_row, df_visits], axis=0)

    T_vw = distance_matrix.travel_matrix(df_visits_depot)

    travel_time_visits = 2* sum(T_vw[0]) #Frem og tilbake til sykehuset og visits
    travel_time = read_travel_time(results_filepath)  # assuming this function reads the travel time
    #print(f'original travel time {travel_time}, hypothetical travel time to visits {travel_time_visits}')
   
    return travel_time_visits/travel_time

def calculate_route_efficiency_number_of_tasks(results_filepath):
    travel_time = read_travel_time(results_filepath)
    num_activities = len(extract_activity_ids(results_filepath))
    
    return travel_time / num_activities


#-------------- PATIENT CONVENIENCE -----------------
def read_patient_continuity_obj(filepath):
    """Read and return the travel time from the results file."""
    with open(filepath, 'r') as file:
        text = file.read()
    patient_continuity_obj = int(re.search(r"Patient continuity: -(\d+)", text).group(1))
    return patient_continuity_obj

def calculate_possible_patient_continuity(folder_name, activity_ids):
    """Calculate possible patient continuity from activity data."""
    file_path_activities = os.path.join(os.getcwd(), folder_name, 'activities.pkl')
    df_activities = pd.read_pickle(file_path_activities)
    
    # Filtrer aktiviteter basert på at activityId er index
    filtered_activities = df_activities.loc[df_activities.index.isin(activity_ids)]
    
    # Summer alle keys i hver 'employeeHistory' dictionary
    possible_continuity = sum(sum(history.keys()) for history in filtered_activities['employeeHistory'])
    
    return possible_continuity

def calculate_patient_continuity(results_filepath, folder_name):
    patient_continuity_obj = read_patient_continuity_obj(results_filepath)
    activity_ids = extract_activity_ids(results_filepath)
    possible_patient_continuity = calculate_possible_patient_continuity(folder_name, activity_ids)
    if possible_patient_continuity == 0:
        return 0  # To avoid division by zero
    return patient_continuity_obj / possible_patient_continuity

def patients_highest_utility(folder_name):
    """Return a list of patient IDs from the top 20% of patients sorted by aggregate utility."""
    file_path_patients = os.path.join(os.getcwd(), folder_name, 'patients.pkl')
    df_patients = pd.read_pickle(file_path_patients)
    df_patients_sorted = df_patients.sort_values(by='aggUtility', ascending=False)
    top_20_percent_cutoff = int(len(df_patients_sorted) * 0.2)
    top_20_percent_patients = df_patients_sorted.iloc[:top_20_percent_cutoff]
    
    patient_ids_list = top_20_percent_patients.index.tolist()
    
    return patient_ids_list, df_patients


def calculate_patient_utility(results_filepath, folder_name):
    high_utility_patient_ids_list, df_patients = patients_highest_utility(folder_name)
    allocated_patients = extract_patient_ids(results_filepath)
    
    # Identifying high utility patients that are allocated
    high_utility_allocated_patients = [patient for patient in allocated_patients if patient in high_utility_patient_ids_list]
    
    # Calculating the sum of aggUtility for high utility allocated and all high utility patients
    sum_allocated = df_patients.loc[df_patients.index.isin(high_utility_allocated_patients), 'aggUtility'].sum()
    sum_all = df_patients.loc[df_patients.index.isin(high_utility_patient_ids_list), 'aggUtility'].sum()
    
    return sum_allocated / sum_all if sum_all != 0 else 0
    
#-------------- HOSPITAL COST -----------------
def calculate_hospital_cost(results_filepath):
    num_allocated_patients = len(extract_patient_ids(results_filepath))
    #gammel = int(0.3 * bed_day_cost * num_allocated_patients)
    return num_allocated_patients
    

#-------------- PATIENT CONTINUITY COUNTER -----------------
def extract_employee_assignments(filepath):
    """ Extract employee assignments from the results file. """
    with open(filepath, 'r') as file:
        data = file.read()
    # Finn alle aktivitetsblokkene for hver ansatt
    assignments = {}
    activities_blocks = re.findall(r"DAG \d+ ANSATT (\d+)(.*?)(?=DAG \d+ ANSATT|\Z)", data, re.DOTALL)
    for employee, block in activities_blocks:
        # Finn alle aktivitets-IDer i hver blokk
        activity_ids = re.findall(r"activity (\d+)", block)
        for activity_id in activity_ids:
            assignments[int(activity_id)] = int(employee)
    
    return assignments


def calculate_patient_continuity_counter(assignments, folder_name):
    file_path_activities = os.path.join(os.getcwd(), folder_name, 'activities.pkl')
    df_activities = pd.read_pickle(file_path_activities)
    results = []

    # Bruker sett for å holde styr på unike pasienter som møter kontinuitetskravene
    unique_patients_continuity1 = set()
    unique_patients_continuity2 = set()
    activities_continuity1 = set()
    activities_continuity2 = set()

    # Gjennomgå hver aktivitet og beregn poeng basert på preferanser
    for activity_id, assigned_employee in assignments.items():
        if activity_id in df_activities.index:
            patient_id = df_activities.at[activity_id, 'patientId']
            preferences = df_activities.at[activity_id, 'employeeHistory']
            score = 0
            if 1 in preferences and assigned_employee in preferences[1]:
                activities_continuity1.add(activity_id)
                if patient_id not in unique_patients_continuity1:
                    unique_patients_continuity1.add(patient_id)
                    score += 1
                    #print(f"Match found for activity {activity_id} with employee {assigned_employee} for preference 1, patient {patient_id}")
            if 2 in preferences and assigned_employee in preferences[2]:
                activities_continuity2.add(activity_id)
                if patient_id not in unique_patients_continuity2:
                    unique_patients_continuity2.add(patient_id)
                    score += 2
                    #print(f"Match found for activity {activity_id} with employee {assigned_employee} for preference 2, patient {patient_id}")
            results.append({'activityId': activity_id, 'score': score})
    
    df_scores = pd.DataFrame(results)
    total_score = df_scores['score'].sum()

    return total_score, len(unique_patients_continuity1), len(unique_patients_continuity2), len(activities_continuity1), len(activities_continuity2)

def count_unique_patients_in_solution(file_path_results, folder_name):
    activity_ids = extract_activity_ids(file_path_results)  # Anta at denne funksjonen returnerer en liste med aktivitets-IDer

    file_path_activities = os.path.join(os.getcwd(), folder_name, 'activities.pkl')
    df_activities = pd.read_pickle(file_path_activities)

    filtered_activities = df_activities.loc[df_activities.index.isin(activity_ids)]

    patientsInSolutionContinuity1 = 0
    patientsInSolutionContinuity2 = 0
    patientsInSolutionContinuity3 = 0

    seen_patients1 = set()
    seen_patients2 = set()

    # Grupper etter patientId og sjekk preferanser
    for patientId, group in filtered_activities.groupby('patientId'):
        # Anta at 'employeeHistory' for hver aktivitet er et dictionary som kan ha keys 1 og 2
        hasContinuity1 = any(1 in act.employeeHistory for act in group.itertuples())
        hasContinuity2 = any(2 in act.employeeHistory for act in group.itertuples())
        
        if hasContinuity1 and patientId not in seen_patients1:
            patientsInSolutionContinuity1 += 1
            seen_patients1.add(patientId)
        
        elif hasContinuity2 and patientId not in seen_patients2:
            patientsInSolutionContinuity2 += 1
            seen_patients2.add(patientId)

        else:
            patientsInSolutionContinuity3 += 1

    return patientsInSolutionContinuity1, patientsInSolutionContinuity2, patientsInSolutionContinuity3

def count_unique_patients_in_solution2(file_path_results, folder_name):
    activity_ids = extract_activity_ids(file_path_results)  
    file_path_activities = os.path.join(os.getcwd(), folder_name, 'activities.pkl')
    df_activities = pd.read_pickle(file_path_activities)

    filtered_activities = df_activities.loc[df_activities.index.isin(activity_ids)]

    # Initialisere tellere for pasienter og aktiviteter
    patientsInSolutionContinuity1 = 0
    activitiesInSolutionContinuity1 = 0
    patientsInSolutionContinuity2 = 0
    activitiesInSolutionContinuity2 = 0
    patientsInSolutionContinuity3 = 0
    activitiesInSolutionContinuity3 = 0

    seen_patients1 = set()
    seen_patients2 = set()

    # Grupper etter patientId og sjekk preferanser
    for patientId, group in filtered_activities.groupby('patientId'):
        groupContinuity1 = False
        groupContinuity2 = False

        # Sjekk preferanser for hver aktivitet i gruppen
        for act in group.itertuples():
            if 1 in act.employeeHistory:
                activitiesInSolutionContinuity1 += 1
                groupContinuity1 = True
            elif 2 in act.employeeHistory:
                activitiesInSolutionContinuity2 += 1
                groupContinuity2 = True

        # Oppdater unike pasienttallere basert på gruppeinformasjon
        if groupContinuity1 and patientId not in seen_patients1:
            patientsInSolutionContinuity1 += 1
            seen_patients1.add(patientId)

        if groupContinuity2 and patientId not in seen_patients2:
            patientsInSolutionContinuity2 += 1
            seen_patients2.add(patientId)

        if not groupContinuity1 and not groupContinuity2:
            patientsInSolutionContinuity3 += 1
            activitiesInSolutionContinuity3 += len(group)  # Anta alle aktiviteter ikke oppfyller noen preferanser

    return (patientsInSolutionContinuity1, activitiesInSolutionContinuity1,
            patientsInSolutionContinuity2, activitiesInSolutionContinuity2,
            patientsInSolutionContinuity3, activitiesInSolutionContinuity3)   

# File paths
folder_name = 'data'
file_path_activities = "C:\\Users\\gurl\\masters-thesis\\data\\activitiesNewTimeWindows.csv"
file_path_employees = "C:\\Users\\gurl\\masters-thesis\\data\\employees.csv"
file_path_results = "C:\\Users\\gurl\\masters-thesis\\results\\results-2024-05-29_10-25-05\\final.txt"

#KPI-resultater
idle_time = round(calculate_idle_time(file_path_results, file_path_activities, file_path_employees),2)
print(f"Calculated Idle Time: {idle_time}\n")
idle_time_logistic, idle_time_health_employees = calculate_idle_time_for_profession_levels(file_path_results, file_path_activities, file_path_employees)
print(f"Calculated Idle Time for logistics employees {round(idle_time_logistic,2)} and health workers/nurses {round(idle_time_health_employees,2)}\n")
health_time = calculate_healthcare_time(file_path_results, file_path_activities, file_path_employees)
print(f"Calculated Healthcare Time: {round(health_time,2)}\n")
route_efficiency = calculate_route_efficiency(file_path_results, file_path_activities)
#print(f"Calculated Route Efficiency: {route_efficiency}")
route_efficiency2 = calculate_route_efficiency_number_of_tasks(file_path_results)
print(f"Calculated Route Efficiency based on number of tasks conducted: {round(route_efficiency2,2)}\n")
patient_continuity = calculate_patient_continuity(file_path_results, folder_name)
print(f"Calculated Patient Continuity: {round(patient_continuity,2)}\n")
patient_utility = calculate_patient_utility(file_path_results, folder_name)
print(f"Calculated Patient Utility: {round(patient_utility,2)}\n")
hospital_cost = calculate_hospital_cost(file_path_results)
print(f"Calculated Hospital Cost Effectiveness: {hospital_cost}\n")
activity_assignments = extract_employee_assignments(file_path_results)
total_score, patients_continuity1, patients_continuity2, activities_continuity1, activities_continuity2 = calculate_patient_continuity_counter(activity_assignments, folder_name)
#patientsInSolutionContinuity1,patientsInSolutionContinuity2, patientsInSolutionContinuity3 = count_unique_patients_in_solution(file_path_results, folder_name)

results = count_unique_patients_in_solution2(file_path_results, folder_name)
print(f"Continuity 1 - Patients: {results[0]}, Activities: {results[1]}")
print(f"Continuity 2 - Patients: {results[2]}, Activities: {results[3]}")
print(f"No Continuity - Patients: {results[4]}, Activities: {results[5]}")

print(f"Total patient continuity score: {total_score}")
print(f"Number of unique patients for continuity 2 matches: activities {activities_continuity1} of {results[1]}, patients {patients_continuity1} of {results[0]}") #Koden og overleaf gjør det motsatt på continuity level ser det ut som
print(f"Number of unique patients for continuity 1 matches: activities {activities_continuity2} of {results[3]}, patients {patients_continuity2} of {results[2]}")
print(f"Number of unique patients for continuity 3: activities {results[5]}, patients {results[4]}\n")
