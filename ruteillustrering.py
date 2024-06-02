import pandas as pd
import os

def parse_location(location):
    """ Parse a location which might be a string formatted as '(lat, long)' or a direct tuple (lat, long). """
    if isinstance(location, str):
        if location.startswith('(') and location.endswith(')'):
            location = location[1:-1]  # Remove parentheses
        lat, long = location.split(',')
    elif isinstance(location, tuple):
        lat, long = location  # Unpack tuple directly
    else:
        raise ValueError("Unsupported location format")
    return lat.strip(), long.strip()

def get_locations_for_activities(activities_df, activity_list):
    """ Extract locations from activities DataFrame based on a list of activity IDs. """
    locations = activities_df.loc[activities_df.index.isin(activity_list), 'location']
    parsed_locations = [parse_location(loc) for loc in locations]
    return parsed_locations

# Define the path to the activities DataFrame stored in a pickle file
folder_name = 'data'
file_path_activities = os.path.join(os.getcwd(), folder_name, 'activities.pkl')

# Load the DataFrame from the pickle file
df_activities = pd.read_pickle(file_path_activities)

# Define the activities for each employee
employee_activities = {
    "Ansatt 1": [162, 191, 192, 163, 482, 483, 38, 39, 122, 123, 125, 126],
    "Ansatt 2": [597, 355, 356, 598, 150, 151, 152, 580, 534, 521, 135, 20, 21, 136],
    "Ansatt 3": [370, 371, 372, 277, 572, 519, 308, 520, 309, 413, 339, 340],
    "Ansatt 4": [159, 160, 619, 229, 230, 231, 426, 427, 245, 476, 469, 338],
    "Ansatt 5": [617, 618, 381, 161, 37, 467, 468, 246, 247, 84, 85, 137],
    "Ansatt 6": [379, 380, 227, 188, 228, 189, 190, 493, 568, 14, 325, 124],
    "Ansatt 7": [275, 276, 578, 579, 49, 50, 411, 336, 477, 412, 337, 478],
    "Ansatt 8": [631, 600, 601, 35, 323, 36, 48, 269, 324, 83, 22],
    "Ansatt 9": [629, 630, 599, 491, 492, 573, 574, 81, 484, 82, 270, 271, 326, 310, 327],
    "Ansatt 10": [243, 357, 244, 566, 567, 428, 299, 300, 256, 15, 16, 301]
}

# Retrieve locations for each employee's activities
employee_locations = {employee: get_locations_for_activities(df_activities, activities)
                      for employee, activities in employee_activities.items()}

# Save the results to CSV files:
for employee, locations in employee_locations.items():
    # Create a DataFrame from the locations
    df_to_save = pd.DataFrame(locations, columns=['Latitude', 'Longitude'])
    # Define a filename for the CSV
    filename = f"{employee}_locations.csv"
    # Save to CSV without the index
    df_to_save.to_csv(filename, index=False)
    print(f"Lokasjoner for {employee} lagret til {filename}")
