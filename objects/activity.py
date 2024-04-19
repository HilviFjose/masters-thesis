import pandas as pd

import os
import sys
sys.path.append( os.path.join(os.path.split(__file__)[0],'..') )  # Include subfolders
from datageneration.employeeGeneration import *
from datageneration.patientGeneration import *
'''
Info:
For å opprette en aktivitet må dataframene som inneholder aktivitetne til ID-en sendes inn og selve ID-en
'''
class Activity:
    def __init__(self, df, id):
        # Fetch the row once and reuse it to access all required fields
        row = df.loc[id]
        self.id = id 
        self.latestStartTime = row["latestStartTime"]
        self.earliestStartTime = row["earliestStartTime"]
        self.duration = row["duration"]
        self.skillReq = row["skillRequirement"]
        self.heaviness = row["heaviness"]
        self.pickUpActivityID = row["sameEmployeeActivityId"]
        self.location = self.makeLocationTuple(row["location"])  # Assume input is correct, no need for hardcoded string
        self.employeeRestricions = row["employeeRestriction"]
        self.continuityGroup = row["continuityGroup"]
        self.employeeHistory = row["employeeHistory"]

        # Using the refactored method to avoid redundancy
        self.PrevNode, self.PrevNodeInTime = self.makePresNodes(row["prevPrece"])
        self.NextNode, self.NextNodeInTime = self.makePresNodes(row["nextPrece"])
        
        self.patient = row["patientId"]
        self.treatmentId = row["treatmentId"]
        self.nActInPatient = row["nActInPatient"]
        self.nActInTreat = row["nActInTreat"]
        self.nActInVisit = row["numActivitiesInVisit"]
        self.suitability = row["utility"]
        self.startTime = None  # Initial start time is None

        # Initializing dependent activities list based on precedence nodes
        self.dependentActivities = self.PrevNode + self.NextNode + [elem[0] for elem in (self.PrevNodeInTime + self.NextNodeInTime)]
        self.newEarliestStartTime = dict.fromkeys(self.dependentActivities, 0)
        self.newLatestStartTime = dict.fromkeys(self.dependentActivities, 1440)
        
        self.sameEmployeeActivityID = row["sameEmployeeActivityId"]
        self.employeeNotAllowedDueToPickUpDelivery = []
        self.possibleToInsert = True

    def makeLocationTuple(self, coordinate_input):
        # Check if the input is already a tuple of two floats
        if isinstance(coordinate_input, tuple) and len(coordinate_input) == 2 and all(isinstance(num, float) for num in coordinate_input):
            return coordinate_input  # Return the tuple directly if it's correctly formatted
        
       
        # Remove parentheses and split by comma
        stripped_string = coordinate_input.strip("()")
        split_strings = stripped_string.split(", ")
        # Convert each part to float and form a tuple
        return tuple(float(num) for num in split_strings)
          
        
    def makePresNodes(self, input_data): 
        '''
        Receives data from the dataframe and returns two lists with the precedence information.
        This version can handle both strings and individual numbers.
        '''
        PrevNode = []
        PrevNodeInTime = []
        # If input_data is directly an integer, process it accordingly
        if isinstance(input_data, int):
            PrevNode.append(input_data)
        elif isinstance(input_data, str) and input_data:  # If input_data is a non-empty string
            strList = input_data.split(",")
            for elem in strList:
                if ":" in elem:
                    PrevNodeInTime.append(tuple(int(part.strip()) for part in elem.split(":")))
                else:
                    PrevNode.append(int(elem))
        return PrevNode, PrevNodeInTime
 
    def makeEmployeeRestriction(self, input_data): 
        list = []
        if isinstance(input_data, int):
            return list.append(input_data)
        return input_data

    
    def makePresNodes(self, input_data): #TODO: AGNES: Ny funksjon her til fordel for den over. Stemmer det at det er dette det den skal gjøre, Agnes?
        '''
        Receives data from the dataframe and returns two lists with the precedence information.
        This version can handle both strings and individual numbers.
        '''
        PrevNode = []
        PrevNodeInTime = []
        
        # If input_data is directly an integer, process it accordingly
        if isinstance(input_data, int):
            PrevNode.append(input_data)
            return PrevNode, PrevNodeInTime
        
        # If input_data is a string
        elif isinstance(input_data, str) and input_data:
            strList = input_data.split(",")
            for elem in strList:
                if ":" in elem:
                    PrevNodeInTime.append(tuple(int(part.strip()) for part in elem.split(":")))
                else:
                    PrevNode.append(int(elem))
            return PrevNode, PrevNodeInTime
        
        # If input_data is neither an int nor a non-empty string, return empty lists
        else:
            return PrevNode, PrevNodeInTime

    #get funksjonene henter ut Acitivy variablene og parameterne 

    def getNewEarliestStartTime(self): 
    # Directly use max on dictionary values, with a default return value of 0 if dictionary is empty
        return max(self.newEarliestStartTime.values(), default=0)
    
    def getNewLatestStartTime(self): 
    # Directly use min on dictionary values, with a default return value of 1440 if dictionary is empty
        return min(self.newLatestStartTime.values(), default=1440)

    def setNewEarliestStartTime(self, newEarliestStartTimeFromDepAct, depAct): 
        self.newEarliestStartTime[depAct] = newEarliestStartTimeFromDepAct
        # Calculate once and reuse
        newEarliest = self.getNewEarliestStartTime()
        newLatest = self.getNewLatestStartTime()
        # Simplified conditional logic
        self.possibleToInsert = not (max(newEarliest, self.earliestStartTime) > min(self.latestStartTime, newLatest))

    def setNewLatestStartTime(self, newLatestStartTimeFromDepAct, depAct): 
        self.newLatestStartTime[depAct] = newLatestStartTimeFromDepAct
        # Calculate once and reuse
        newEarliest = self.getNewEarliestStartTime()
        newLatest = self.getNewLatestStartTime()
        # Simplified conditional logic
        self.possibleToInsert = not (max(newEarliest, self.earliestStartTime) > min(self.latestStartTime, newLatest))
    

    #TODO: Slette denne? 
    '''
    def updateEmployeeHistory(self, employeeId):
        continuity_score, employeeIds = next(iter(self.employeeHistory.items()))
        employeeIds.append(employeeId)  
        self.employeeHistory[continuity_score] = employeeIds
    '''   
