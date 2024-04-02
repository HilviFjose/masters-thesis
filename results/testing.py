import re
from collections import Counter
import ast

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

def compare_dictionary_with_candidate(candidate, dict):
    activities, duplicates = extract_activities(candidate)
    keys1, dictionary = extract_dictionary(dict, 'visits')
    missing_act, missing_in_act, missing_dict, missing_in_dict = compare_missing_elements(activities, dictionary)
    #print("act", list(activities))
    #print("dict1", dictionary_1)
    if missing_act == False and missing_dict == False:
        print("YEY! Candidate activities similar to activities in visit dictionary")
    else: 
        print("ERROR: Candidate activities NOT similar to activities in visit dictionary")
        if missing_act:
            print("Elements present in dictionary but missing in candidate:", missing_in_act)
        if missing_dict:
            print("Elements present in candidate but missing in dictionary:", missing_in_dict)


def compare_dictionaries(file):
    visit_keys, visit_values = extract_dictionary(file, 'visits')
    treatment_keys, treatment_values = extract_dictionary(file, 'treatments')
    patient_keys, patient_values = extract_dictionary(file, 'allocated patients')
    missing_visitkeys, missing_in_visitkeys, missing_treatmentval, missing_in_treatmentval = compare_missing_elements(visit_keys, treatment_values)
    missing_treatmentkeys, missing_in_treatmentkeys, missing_patientval, missing_in_patientval = compare_missing_elements(treatment_keys, patient_values)
    if missing_visitkeys == False and missing_treatmentval == False:
        print("YEY! Visits dictionary similar to treatment dictionary")
    else: 
        print("ERROR: Visits dictionary NOT similar to treatment dictionary")
        if missing_visitkeys:
            print("Elements present in treatment dictionary but missing in visit dictionary:", missing_in_visitkeys)
        if missing_treatmentval:
            print("Elements present in visit dictionary but missing in treatment dictionary:", missing_in_treatmentval)
    if missing_treatmentkeys == False and missing_patientval == False:
        print("YEY! Treatment dictionary similar to patient dictionary")
    else: 
        print("ERROR:Treatment dictionary NOT similar to patient dictionary")
        if missing_treatmentkeys:
            print("Elements present in patient dictionary but missing in treatment dictionary:", missing_in_treatmentkeys)
        if missing_patientval:
            print("Elements present in treatment dictionary but missing in patient dictionary:", missing_in_patientval)

    
# Example usage
username = 'hilvif'
file_path_1 = 'c:\\Users\\'+username+'\\masters-thesis\\results\\initial.txt'  # Replace with the actual path to your first file
file_path_2 = 'c:\\Users\\'+username+'\\masters-thesis\\results\\final.txt'  # Replace with the actual path to your second file
cand = 2
file_path_candidate = 'c:\\Users\\'+username+'\\masters-thesis\\results\\candidate'+str(cand)+'.txt'  
file_path_dict = 'c:\\Users\\'+username+'\\masters-thesis\\results\\candidate'+str(cand)+'dict.txt'  

print("COMPARING CANDIDATE FILES")
compare_files(file_path_1, file_path_2)
print("---------------------------")

print("COMPARING DICTIONARIES WITH CANDIDATE")
compare_dictionary_with_candidate(file_path_candidate, file_path_dict)
print("---------------------------")

print("COMPARING THE DIFFERENT DICTIONARIES")
compare_dictionaries(file_path_dict)
print("---------------------------")

