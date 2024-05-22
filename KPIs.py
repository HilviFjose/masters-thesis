import os
import sys
import pandas as pd
import re
import json

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

def count_unique_employees(employees_filepath):
    """Count the number of unique employees from the employees file."""
    employees = pd.read_csv(employees_filepath)
    return employees['employeeId'].nunique()

def calculate_idle_time(results_filepath, activities_filepath, employees_filepath):
    """Calculate the idle time based on travel time, total activity duration, and number of employees."""
    travel_time = read_travel_time(results_filepath)
    activity_ids = extract_activity_ids(results_filepath)
    total_activity_duration = calculate_total_activity_duration(activities_filepath, activity_ids)
    num_employees = count_unique_employees(employees_filepath)
    print(f'travel time {travel_time}, duration {total_activity_duration}, working time {5*8*60*num_employees}')
    idle_time = (travel_time + total_activity_duration) / (5 * 8 * 60 * num_employees)
    return idle_time

def calculate_healthcare_time(results_filepath, activities_filepath):
    """Calculate the healthcare time based on travel time, total activity duration, and total health activity duration."""
    travel_time = read_travel_time(results_filepath)  # assuming this function reads the travel time
    activity_ids = extract_activity_ids(results_filepath)
    total_activity_duration = calculate_total_activity_duration(activities_filepath, activity_ids)
    total_health_duration = calculate_total_health_activity_duration(activities_filepath, activity_ids)
    print(f'travel time {travel_time}, duration activities {total_activity_duration}, duration health activities {total_health_duration}')
    if (total_activity_duration + travel_time) == 0:
        return 0  # To avoid division by zero
    health_time = (travel_time + total_health_duration) / (total_activity_duration + travel_time)
    return health_time

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
    print(f'original travel time {travel_time}, hypothetical travel time to visits {travel_time_visits}')
   
    return travel_time/travel_time_visits

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
def calculate_hospital_cost(results_filepath, bed_day_cost):
    num_allocated_patients = len(extract_patient_ids(results_filepath))
    return int(0.3 * bed_day_cost * num_allocated_patients)
    

# File paths
folder_name = 'data'
file_path_activities = "C:\\Users\\gurl\\masters-thesis\\data\\activitiesNewTimeWindows.csv"
file_path_employees = "C:\\Users\\gurl\\masters-thesis\\data\\employees.csv"
file_path_results = "C:\\Users\\gurl\\masters-thesis\\results\\results-2024-05-21_17-17-14\\final.txt"

#KPI-resultater
idle_time = calculate_idle_time(file_path_results, file_path_activities, file_path_employees)
print(f"Calculated Idle Time: {idle_time}")
health_time = calculate_healthcare_time(file_path_results, file_path_activities)
print(f"Calculated Healthcare Time: {health_time}")
route_efficiency = calculate_route_efficiency(file_path_results, file_path_activities)
print(f"Calculated Route Efficiency: {route_efficiency}")
patient_continuity = calculate_patient_continuity(file_path_results, folder_name)
print(f"OBS: Hent riktig objektiv i ruteplanen (blir feil på objective study)")
print(f"Calculated Patient Continuity: {patient_continuity}")
patient_utility = calculate_patient_utility(file_path_results, folder_name)
print(f"Calculated Patient Utility: {patient_utility}")
hc_cost = 10000
hospital_cost = calculate_hospital_cost(file_path_results, hc_cost)
print(f"Calculated Hospital Cost Effectiveness: {hospital_cost}, hc_cost: {hc_cost}")