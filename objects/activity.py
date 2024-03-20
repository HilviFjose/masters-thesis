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
        self.id = id 
        self.latestStartTime = df.loc[id]["latestStartTime"]
        self.earliestStartTime = df.loc[id]["earliestStartTime"]
        self.duration = df.loc[id]["duration"]
        self.skillReq = df.loc[id]["skillRequirement"]
        self.heaviness = df.loc[id]["heaviness"]
        self.pickUpActivityID = df.loc[id]["sameEmployeeActivityId"]
        self.location = df.loc[id]["location"]
        self.employeeRestrictions = df.loc[id]["employeeRestriction"]
        self.PrevNode, self.PrevNodeInTime= self.makePresNodes(df.loc[id]["prevPrece"])
        #TODO: Den gjensidige avhengigheten må legges inn i datagenereringen 
        self.NextNode, self.NextNodeInTime = self.makePresNodes(df.loc[id]["nextPrece"])
        self.patient = df.loc[id]["patientId"]
        self.suitability = df.loc[id]["utility"]
        self.startTime = None
        #self.newLatestStartTime = 1440
        #self.newEeariestStartTime = 0
        self.employeeNotAllowedDueToPickUpDelivery = []
        self.possibleToInsert = True

        #Lager dependent activities. Som er aktiviteter som denne noden påvirkes av 
        self.dependentActivities = self.PrevNode + self.NextNode 
        for elem in (self.PrevNodeInTime + self.NextNodeInTime): 
            self.dependentActivities.append(elem[0])

        self.newEarliestStartTime = dict.fromkeys(self.dependentActivities, 0)
        self.newLatestStartTime = dict.fromkeys(self.dependentActivities, 1440)
    
    def makeEmployeeRestriction(self, input_data): 
        restrictions = []  
        if isinstance(input_data, int):
            restrictions.append(input_data)
            return restrictions  
        else:
            return [input_data] 

    def makePresNodes(self, input_data):
        '''
        Receives data from the dataframe and returns two lists with the precedence information.
        This version is optimized for efficiency and can handle both strings and individual numbers.
        '''
        PrevNode = []
        PrevNodeInTime = []
        
        if not input_data or not isinstance(input_data, (int, str)):
            return PrevNode, PrevNodeInTime

        if isinstance(input_data, int):
            PrevNode.append(input_data)
        else:
            strList = input_data.split(",")
            for elem in strList:
                if ":" in elem:
                    parts = elem.split(":")
                    PrevNodeInTime.append(tuple(int(part.strip()) for part in parts))
                else:
                    PrevNode.append(int(elem.strip()))
        return PrevNode, PrevNodeInTime

    def setStartTime(self, startTime): 
        self.startTime = startTime

    def getNewEarliestStartTime(self): 
        return max(self.newEarliestStartTime.values(), default=0)
 
    def getNewLatestStartTime(self): 
        return min(self.newLatestStartTime.values(), default=1440)

    def checkActivityFeasibility(self):
        # Check if the activity can be scheduled within the updated time constraints.
        if max(self.getNewEarliestStartTime(), self.earliestStartTime) > min(self.latestStartTime, self.getNewLatestStartTime()):
            self.possibleToInsert = False
        else:
            self.possibleToInsert = True

    def setNewEarliestStartTime(self, newEarliestStartTimeFromDepAct, depAct): 
        # Update earliest start time if the new time is later than the current time.
        self.newEarliestStartTime[depAct] = newEarliestStartTimeFromDepAct
        self.checkActivityFeasibility()

    def setNewLatestStartTime(self, newLatestStartTimeFromDepAct, depAct): 
        # Update latest start time if the new time is earlier than the current time.
        self.newLatestStartTime[depAct] = newLatestStartTimeFromDepAct
        self.checkActivityFeasibility()
            
    def setemployeeNotAllowedDueToPickUpDelivery(self, list): 
        self.employeeNotAllowedDueToPickUpDelivery = list 

    def restartActivity(self): 
        self.startTime = None
        self.newEarliestStartTime = dict.fromkeys(self.dependentActivities, 0)
        self.newLatestStartTime = dict.fromkeys(self.dependentActivities, 1440)
        self.employeeNotAllowedDueToPickUpDelivery = []
        self.possibleToInsert = True

