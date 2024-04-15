import re
from collections import Counter
import ast
import os
import sys
sys.path.append( os.path.join(os.path.split(__file__)[0],'..'))  # Include subfolders
from config.main_config import *
import parameters
import pandas as pd

df_employees = parameters.df_employees
df_patients = parameters.df_patients
df_treatments = parameters.df_treatments
df_visits = parameters.df_visits
df_activities = parameters.df_activities

def extract_activities(file_path):
    """Extract activity numbers from a given file and identify duplicates."""
    activities = []
    with open(file_path, 'r') as file:
        for line in file:
            match = re.search(r'activity (\d+)', line)
            if match:
                activities.append(int(match.group(1)))

    # Identify duplicates by counting occurrences and filtering those with count > 1
    duplicates = [item for item, count in Counter(activities).items() if count > 1]
    return set(activities), duplicates

def extract_activities_with_start_time(file_path):
    """Extract activity numbers from a given file and identify duplicates."""
    activity_tuples = []
    pattern = re.compile(r"activity (\d+) start (\d+\.?\d*)")
    with open(file_path, 'r') as file:
        for line in file:
            match = pattern.search(line)
            if match:
                activity = int(match.group(1))
                start = float(match.group(2))
                activity_tuples.append((activity, start))
    return activity_tuples

def extract_dictionary(file_path, str_item):
    dict_name = str_item
    specific_dict = None
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith(dict_name):
                dict_content = line[len(dict_name):].strip()
                specific_dict = ast.literal_eval(dict_content)
                break
    values_list = []
    keys_list = []
    for value in specific_dict.values():
        if isinstance(value, list): 
            values_list.extend(value) 
        else:
            values_list.append(value) 
    for key in specific_dict.keys():
        if isinstance(key, list): 
            keys_list.extend(key) 
        else:
            keys_list.append(key) 
    return keys_list, values_list

def get_dictionary(file_path, str_item):
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith(str_item):
                dict_content = line[len(str_item):].strip()
                specific_dict = ast.literal_eval(dict_content)
                return specific_dict  # Return the dictionary directly
    return {}

def extract_list(file_path, str_item):
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith(str_item):
                start_index = line.find('[')
                if start_index != -1:
                    list_str = line[start_index:]
                    try:
                        # Converting the string representation of the list to an actual list
                        # ast.literal_eval safely evaluates an expression node or a string containing a Python literal
                        extracted_list = ast.literal_eval(list_str)
                        if isinstance(extracted_list, list):
                            return extracted_list
                    except (ValueError, SyntaxError):
                        # In case of a parsing error, return an empty list or handle the error as needed
                        print("Error parsing the list from the file.")
                        return []
    # Return an empty list if the specified string item is not found
    return []

def compare_missing_elements(list1, list2):
    set1 = set(list1)
    set2 = set(list2)
    missing1 = False
    missing2 = False
    missing_in_list1 = set2.difference(set1)
    missing_in_list2 = set1.difference(set2)
    if missing_in_list1:
        missing1 = True
    if missing_in_list2:
        missing2 = True
    return missing1, missing_in_list1, missing2, missing_in_list2

def compare_files(file_path_1, file_path_2):
    """Compare two files, print added/removed activities, and check for duplicates."""
    activities_1, duplicates_1 = extract_activities(file_path_1)
    activities_2, duplicates_2 = extract_activities(file_path_2)

    removed_activities = activities_1 - activities_2
    added_activities = activities_2 - activities_1

    if removed_activities:
        print(f"Removed activities: {sorted(removed_activities)}")
    else:
        print("No activities were removed.")

    if added_activities:
        print(f"Added activities: {sorted(added_activities)}")
    else:
        print("No activities were added.")

    if duplicates_1:
        print(f"Duplicate activities in the first file: {duplicates_1}")
    else:
        print("No duplicate activities in the first file.")

    if duplicates_2:
        print(f"Duplicate activities in the second file: {duplicates_2}")
    else:
        print("No duplicate activities in the second file.")

def compare_dictionary_with_candidate(candidate):
    status = True
    activities, duplicates = extract_activities(candidate)
    keys1, dictionary = extract_dictionary(candidate, 'visits')
    missing_act, missing_in_act, missing_dict, missing_in_dict = compare_missing_elements(activities, dictionary)
    if not (missing_act == False and missing_dict == False): 
        status = False
        print("ERROR: Candidate activities NOT similar to activities in visit dictionary")
        if missing_act:
            print("Elements present in dictionary but missing in candidate:", missing_in_act)
        if missing_dict:
            print("Elements present in candidate but missing in dictionary:", missing_in_dict)
    return status

def compare_allocated_dictionaries(file):
    status = True
    visit_keys, visit_values = extract_dictionary(file, 'visits')
    treatment_keys, treatment_values = extract_dictionary(file, 'treatments')
    patient_keys, patient_values = extract_dictionary(file, 'allocated patients')
    missing_visitkeys, missing_in_visitkeys, missing_treatmentval, missing_in_treatmentval = compare_missing_elements(visit_keys, treatment_values)
    missing_treatmentkeys, missing_in_treatmentkeys, missing_patientval, missing_in_patientval = compare_missing_elements(treatment_keys, patient_values)
    if not (missing_visitkeys == False and missing_treatmentval == False):
        print("ERROR: Visits dictionary NOT similar to treatment dictionary")
        status = False
        if missing_visitkeys:
            print("Elements present in treatment dictionary but missing in visit dictionary:", missing_in_visitkeys)
        if missing_treatmentval:
            print("Elements present in visit dictionary but missing in treatment dictionary:", missing_in_treatmentval)
    if not (missing_treatmentkeys == False and missing_patientval == False): 
        status = False
        print("ERROR:Treatment dictionary NOT similar to patient dictionary")
        if missing_treatmentkeys:
            print("Elements present in patient dictionary but missing in treatment dictionary:", missing_in_treatmentkeys)
        if missing_patientval:
            print("Elements present in treatment dictionary but missing in patient dictionary:", missing_in_patientval)
    return status

def check_consistency(file):
    for i in range(df_patients.shape[0]):
        patientID = df_patients.index[i]
        allocated_patient_dict = get_dictionary(file, 'allocated patients')
        not_allocated_patient = extract_list(file, 'not allocated')
        if patientID in not_allocated_patient: 
            break 
        if patientID not in allocated_patient_dict.keys(): 
            print("ERROR: patient ", patientID, "er hverken i not allocated eller i allocated dict")
        for treatmentID in df_patients.loc[patientID, "treatmentsIds"]:
            treatment_dict = get_dictionary(file, 'treatments')
            illegal_treatments = extract_list(file, 'illegalNotAllocatedTreatments')
            if treatmentID in illegal_treatments:
                break
            if treatmentID not in treatment_dict.keys():
                print("ERROR: treatment ", treatmentID, "for pasient", patientID, "er hverken i not allocated eller i allocatd dict")
            for visitID in df_treatments.loc[treatmentID, "visitsIds"]:
                visit_dict = get_dictionary(file, 'visits')
                illegal_visitlist = list(get_dictionary(file, "illegalNotAllocatedVisits").keys())
                if visitID in illegal_visitlist:
                    break
                if visitID not in visit_dict.keys():
                    print("ERROR: visit ", visitID, "in treatment ", treatmentID, "for patient ", patientID, "er hverken i allocated eller not allocated dict")
                for activityID in df_visits.loc[visitID, "activitiesIds"]:
                    illegal_activity_list = list(get_dictionary(file, "illegalNotAllocatedActivities").keys())
                    if (activityID not in [item for sublist in visit_dict.values() for item in sublist]) and activityID not in illegal_activity_list: 
                        print("ERROR: activity ", activityID, "in visit ", visitID, "in treatment ", treatmentID, "for patient ", patientID, "er borte!!!!")

def check_objective(file_path):
    status = True
    aggregated_utility = 0
    activities_in_candidate, duplicates = extract_activities(file_path)
    utility = list(df_activities['utility'])

    # Find current first objective
    with open(file_path, 'r') as file:
        for line in file:
            match = re.search(r'primary objective without penalty  (\d+)', line)
            if match:
                objective_value = int(match.group(1))
        
    # Calculate aggregated utility in route plan
    for act in activities_in_candidate:
        index = act - 1
        aggregated_utility += utility[index]

    # Check if objective is similar
    if not objective_value == int(float(aggregated_utility)):
        print("ERROR - Aggregated calculated objective ", aggregated_utility, " is not same as objective in candidate", first_objective_value)
        status = False
    return status



def check_precedence_within_file(file):
    status1 = True
    status2 = True
    status3 = True

    # Create the lists needed
    activities_in_candidate = extract_activities_with_start_time(file)
    cand_dict = dict(activities_in_candidate)
    earliestStart = list(df_activities['earliestStartTime'])
    latestStart = list(df_activities['latestStartTime'])
    nextPrece = list(df_activities['nextPrece'])
    duration = list(df_activities['duration'])
    prec_act_list = [None] * len(nextPrece)
    prec_times_list = [None] * len(nextPrece)
    pattern = re.compile(r'(\d+): (\d+)')
    for idx, item in enumerate(nextPrece):
        if pd.notna(item) and isinstance(item, str):  
            matches = pattern.findall(item)
            if matches:
                keys, values = zip(*[(int(k), int(v)) for k, v in matches])
                prec_act_list[idx] = keys
                prec_times_list[idx] = values
        if isinstance(item, int):
            prec_act_list[idx] = item


    # 1 - Checking if start times are within time windows
    for (activity_id, start_time) in activities_in_candidate:
        index = activity_id - 1  
        if not (earliestStart[index] <= start_time <= latestStart[index]):
            #print("activity_id", activity_id, "earliestStart", earliestStart[index] )
            #print("latestStart[index]", latestStart[index])
            print("ERROR - START TIME NOT IN TIME WINDOW: activity", activity_id, "with start time", start_time)
            status1 = False


    # 2 - Checking if start times are correct in terms of which order they have to happen in
    for activity_id, following in enumerate(prec_act_list, start=1):
        if following is None:
            continue
        following_activities = (following,) if isinstance(following, int) else following
        current_start_time = cand_dict.get(activity_id)
        if current_start_time is None:
            continue
        for following_act_id in following_activities:
            following_start_time = cand_dict.get(following_act_id)
            if following_start_time is None: 
                continue
            if following_start_time <= current_start_time:
                print(f"ERROR - FOLLOWING ACTIVITY STARTING EARLIER THAN CURRENT: Activity {following_act_id} starting at {following_start_time}, starts before activity {activity_id} starting at {current_start_time}.")
                status2 = False

    # 3 - Check if the start times that do not have an error over here are withing the time frames in nexttimes
    for activity_id, following in enumerate(prec_act_list, start=1):
        if following is None or prec_times_list[activity_id - 1] is None:
            continue
        following_activities = (following,) if isinstance(following, int) else following
        timing_constraints = prec_times_list[activity_id - 1]
        current_start_time = cand_dict.get(activity_id)
        if current_start_time is None:
            continue 
        current_end_time = current_start_time + int(duration[activity_id-1])
        for i, following_act_id in enumerate(following_activities):
            following_start_time = cand_dict.get(following_act_id)
            if following_start_time is None:
                continue 
            max_allowed_start_time_after = timing_constraints[i] if isinstance(timing_constraints, tuple) else timing_constraints
            start_time_difference = following_start_time - current_end_time 
            if start_time_difference > max_allowed_start_time_after:
                print(f"ERROR - FOLLOWING ACTIVITY DOES NOT START WITHIN THE PRECEDENCE REQUIREMENT: Activity {following_act_id} starting at {following_start_time} starts more than {max_allowed_start_time_after} time units after activity {activity_id} starting at {current_start_time}.")
                status3 = False
    return status1, status2, status3

# Example usage
username = 'agnesost'
file_path_1 = 'c:\\Users\\'+username+'\\masters-thesis\\results\\initial.txt'  # Replace with the actual path to your first file
#file_path_2 = 'c:\\Users\\'+username+'\\masters-thesis\\results\\initialLS.txt'  # Replace with the actual path to your first file
#file_path_3 = 'c:\\Users\\'+username+'\\masters-thesis\\results\\0before_iteration.txt'  # Replace with the actual path to your first file
#file_path_4 = 'c:\\Users\\'+username+'\\masters-thesis\\results\\final.txt'  # Replace with the actual path to your second file
file_name_list = ["_before_destroy", "_after_destroy", "_after_repair", "_after_local_search"]


status = compare_dictionary_with_candidate(file_path_1)
if status == False:
    print("Something wrong in INITIAL")
    print("---------------------------")

"""
status = compare_dictionary_with_candidate(file_path_4)
if status == False:
    print("Something wrong in FINAL")
    print("---------------------------")
"""

for cand in range(1, iterations+1): 
    for file_name in file_name_list: 
        file_path_candidate = 'c:\\Users\\'+username+'\\masters-thesis\\results\\'+str(cand)+'candidate'+file_name+'.txt'  
        
        status1 = compare_dictionary_with_candidate(file_path_candidate)
        if status1 == False:
            print("HAPPENED IN ROUND ", cand, "IN STEP", file_name)
            print("---------------------------")

        status2 = compare_allocated_dictionaries(file_path_candidate)
        if status2 == False: 
            print("HAPPENED IN ROUND ", cand, "IN STEP", file_name)
            print("---------------------------")
        
        status3, status4, status5 = check_precedence_within_file(file_path_candidate)
        if status3 == False or status4 == False or status5 == False:
            print("HAPPENED IN ROUND ", cand, "IN STEP", file_name)
            print("---------------------------") 
        
        status6 = check_objective(file_path_candidate)
        if status6 == False: 
            print("HAPPENED IN ROUND ", cand, "IN STEP", file_name)
            print("---------------------------")



