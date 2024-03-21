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

def extract_visit_dictionary(file_path):
    dict_name = "visit" 
    specific_dict = None
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith(dict_name):
                dict_content = line[len(dict_name):].strip()
                specific_dict = ast.literal_eval(dict_content)
                break
    values_list = []
    for value in specific_dict.values():
        if isinstance(value, list): 
            values_list.extend(value) 
        else:
            values_list.append(value) 
    return values_list
    

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

def compare_dictionaries_with_candidate(candidate, dict1, dict2):
    activities, duplicates = extract_activities(candidate)
    dictionary_1 = extract_visit_dictionary(dict1)
    dictionary_2 = extract_visit_dictionary(dict2)
    act_equal_dict1 = sorted(list(activities)) == sorted(dictionary_1)
    act_equal_dict2 = sorted(list(activities)) == sorted(dictionary_2)
    dict1_equal_dict2 = sorted(dictionary_1) == sorted(dictionary_2)
    #print("act", list(activities))
    #print("dict1", dictionary_1)
    #print("dict2", dictionary_2)
    set_act = set(activities)
    set_dict1 = set(dictionary_1)
    set_dict2 = set(dictionary_2)
    if act_equal_dict1:
        print("YEY! Candidate activities similar to activities in visit dictionary before LS")
    else: 
        print("ERROR: Candidate activities NOT similar to activities in visit dictionary before LS")
        different_elements = set_act.symmetric_difference(set_dict1)
        print("Elements that are different in the two lists:", different_elements)
    if act_equal_dict2:
        print("YEY! Candidate activities similar to activities in visit dictionary after LS")
    else: 
        print("ERROR: Candidate activities NOT similar to activities in visit dictionary after LS")
        different_elements = set_act.symmetric_difference(set_dict2)
        print("Elements that are different in the two lists:", different_elements)
    if dict1_equal_dict2:
        print("YEY! Activities in visit dictionary before LS similar to activities in visit dictionary after LS")
    else: 
        print("ERROR: Activities in visit dictionary before LS NOT similar to activities in visit dictionary after LS")
        different_elements = set_dict1.symmetric_difference(set_dict2)
        print("Elements that are different in the two lists:", different_elements)


    
# Example usage
file_path_1 = 'c:\\Users\\agnesost\\masters-thesis\\results\\initial.txt'  # Replace with the actual path to your first file
file_path_2 = 'c:\\Users\\agnesost\\masters-thesis\\results\\final.txt'  # Replace with the actual path to your second file
cand = 3
file_path_candidate = 'c:\\Users\\agnesost\\masters-thesis\\results\\candidate'+str(cand)+'.txt'  
file_path_dict1 = 'c:\\Users\\agnesost\\masters-thesis\\results\\candidate'+str(cand)+'dict1.txt'  
file_path_dict2 = 'c:\\Users\\agnesost\\masters-thesis\\results\\candidate'+str(cand)+'dict2.txt'  

print("Comparing candidate files")
print("---------------------------")
compare_files(file_path_1, file_path_2)

print("Comparing dictionaries with candidate")
print("---------------------------")
compare_dictionaries_with_candidate(file_path_candidate, file_path_dict1, file_path_dict2)
