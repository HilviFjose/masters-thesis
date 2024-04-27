import pandas as pd

import os
import sys
sys.path.append( os.path.join(os.path.split(__file__)[0],'..') )  # Include subfolders
from datageneration import employeeGenerationInfusion 
from config import main_config
# employeeId,professionalLevel,clinic,schedule

days = main_config.days

class Employee:
    def __init__(self, employee_array, id):
        self.skillLevel = employee_array[0] # profession level is first element in two-dimensional information list
        self.shifts = self.getShifts(employee_array[2])
        self.id = id
        self.clinic = df.loc[id]["clinic"]
    
    #TODO: Denne er veldig midlertidig håndtert. Må endres slik at den tar inn de faktiske skiftene.
    #Den henter ut skiftene nå også sette rtidspunktene basert pådet. Men burde endres på kanskje 
    def getShifts(self, schedule): 
        employeeShift = {day: {"startShift": 0, "endShift" : 0 } for day in range(1,days+1)} 
        #listOfShifts = shiftString.replace("(", "").replace(")", "").split(", ")
        for shift in schedule: 
            d = (int(shift) - 1) // 3 + 1 
            time = (int(shift) -1) % 3
            if d > days:  # Skip shifts that map to a day outside the valid range
                continue
            if time == 0: 
                employeeShift[d]["startShift"] =  0 
                employeeShift[d]["endShift"] = 480  
            if time == 1: 
                employeeShift[d]["startShift"] =  480
                employeeShift[d]["endShift"] =  960
            if time == 2: 
                employeeShift[d]["startShift"] =  960 
                employeeShift[d]["endShift"] =  1440

        #print(employeeShift) #TODO: Her skjer det noe rart. Alle ansatte med kveldsskift: de ansatte får ikke jobb tildelt mandag 
        return employeeShift

    def getShiftStart(self, day): 
        return self.shifts[day]["startShift"] 
    
    def getShiftEnd(self, day):  
        return self.shifts[day]["endShift"]
    
    def getSkillLevel(self): 
        return self.skillLevel
    
    def getID(self): 
        return self.id


