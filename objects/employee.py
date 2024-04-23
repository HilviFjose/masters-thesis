import pandas as pd

import os
import sys
sys.path.append( os.path.join(os.path.split(__file__)[0],'..') )  # Include subfolders
from datageneration import employeeGeneration 
from config import construction_config

days = construction_config.days

class Employee:
    def __init__(self, df, id):
        self.skillLevel = df.loc[id]["professionalLevel"]
        self.shifts = self.getShifts(df.loc[id]["schedule"])
        self.id = id

    def getShifts(self, schedule):
        # Initialize shifts for each day with default times
        employeeShift = {day: {"startShift": 0, "endShift": 0} for day in range(1, days + 1)}

        # Define shift times based on the 'time' variable
        shift_times = {
            0: {"startShift": 0, "endShift": 480},
            1: {"startShift": 480, "endShift": 960},
            2: {"startShift": 960, "endShift": 1440}
        }

        for shift in schedule:
            day = (int(shift) - 1) // 3 + 1
            time = (int(shift) - 1) % 3
            if day > days:  # Ensure the day is within the valid range
                continue
            # Assign the shift times directly from the predefined 'shift_times' dictionary
            employeeShift[day].update(shift_times[time])

        return employeeShift



