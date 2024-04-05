import re
from collections import Counter
import ast
import os
import sys
sys.path.append( os.path.join(os.path.split(__file__)[0],'..'))  # Include subfolders
from config.main_config import *
import parameters

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


    
# Example usage
username = 'hilvif'
file_path_1 = 'c:\\Users\\'+username+'\\masters-thesis\\results\\initial.txt'  # Replace with the actual path to your first file
file_path_2 = 'c:\\Users\\'+username+'\\masters-thesis\\results\\final.txt'  # Replace with the actual path to your second file
#cand = 3
#file_path_candidate = 'c:\\Users\\'+username+'\\masters-thesis\\results\\candidate'+str(cand)+'.txt'  
#file_path_dict = 'c:\\Users\\'+username+'\\masters-thesis\\results\\candidate'+str(cand)+'dict.txt'  

file_name_list = ["_before_destroy", "_after_destroy", "_after_repair", "_final"]

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

