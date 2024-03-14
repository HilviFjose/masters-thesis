import re
from collections import Counter

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

# Example usage
file_path_1 = 'c:\\Users\\agnesost\\masters-thesis\\results\\initial.txt'  # Replace with the actual path to your first file
file_path_2 = 'c:\\Users\\agneost\\masters-thesis\\results\\final.txt'  # Replace with the actual path to your second file
compare_files(file_path_1, file_path_2)
