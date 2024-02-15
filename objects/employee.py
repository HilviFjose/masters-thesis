import pandas as pd

days = 5 

class Employee:
    def __init__(self, df, id):
        self.skillLevel = df.loc[id]["SkillLevel"]
        self.shifts = self.getShifts(df.loc[id]["Schedule"])
        self.id = id
    
    #TODO: Denne er veldig midlertidig håndtert. Må endres slik at den tar inn de faktiske skiftene.
    #Den henter ut skiftene nå også sette rtidspunktene basert pådet. Men burde endres på kanskje 
    def getShifts(self, shiftString): 
        employeeShift = {day: {"startShift": 0, "endShift" : 0 } for day in range(1,days+1)} 
        listOfShifts = shiftString.replace("(", "").replace(")", "").split(", ")
        for shift in listOfShifts: 
            d = int(shift) // 3 
            time = int(shift) % 3 
            if time == 0: 
                employeeShift[d+1]["startShift"] =  960 
                employeeShift[d+1]["endShift"] = 1440  
            if time == 1: 
                employeeShift[d+1]["startShift"] =  0
                employeeShift[d+1]["endShift"] =  480
            if time == 2: 
                employeeShift[d+1]["startShift"] =  480 
                employeeShift[d+1]["endShift"] =  960
        return employeeShift

    def getShiftStart(self, day): 
        return self.shifts[day]["startShift"] 
    
    def getShiftEnd(self, day):  
        return self.shifts[day]["endShift"]
    
    def getSkillLevel(self): 
        return self.skillLevel
    
    def getID(self): 
        return self.id
