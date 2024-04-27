import pandas as pd

import os
import sys
sys.path.append( os.path.join(os.path.split(__file__)[0],'..') )  # Include subfolders
#from datageneration import employeeGenerationAntibiotics
#from datageneration import patientGenerationAntibiotics
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
        self.location = self.makeLocationTuple(df.loc[id]["location"])   #Endret på denne for å få til lokasjon 
        self.employeeRestricions = df.loc[id]["employeeRestriction"]
        self.continuityGroup = df.loc[id]["continuityGroup"]
        self.employeeHistory = df.loc[id]["employeeHistory"]
        self.PrevNode, self.PrevNodeInTime= self.makePresNodes(df.loc[id]["prevPrece"])
        #TODO: Den gjensidige avhengigheten må legges inn i datagenereringen 
        self.NextNode, self.NextNodeInTime = self.makePresNodes(df.loc[id]["nextPrece"])
        self.patient = df.loc[id]["patientId"]
        self.treatmentId = df.loc[id]["treatmentId"]

        self.nActInPatient = df.loc[id]["nActInPatient"]
        self.nActInTreat = df.loc[id]["nActInTreat"]
        self.nActInVisit = df.loc[id]["numActivitiesInVisit"]

        self.suitability = df.loc[id]["utility"]

        self.prefSpes = df.loc[id]["specialisationPreferred"]
        
        self.startTime = None
        #self.newLatestStartTime = 1440
        #self.newEeariestStartTime = 0
        self.employeeNotAllowedDueToPickUpDelivery = []
        self.possibleToInsert = True

        #Lager dependent activities. Som er aktiviteter som denne noden påvirkes av 
        self.dependentActivities = self.PrevNode + self.NextNode 
        for elem in (self.PrevNodeInTime + self.NextNodeInTime): 
            self.dependentActivities.append(elem[0])

        self.newEeariestStartTime = dict.fromkeys(self.dependentActivities, 0)
        self.newLatestStartTime = dict.fromkeys(self.dependentActivities, 1440)

        self.sameEmployeeAcitivtyID = df.loc[id]["sameEmployeeActivityId"]
        
    #make funskjonene setter parameterne til Acitivy objektet 
    
    def makeLocationTuple(self, coordinate_string): 
        coordinate_string = "(59.8703, 10.8382)"

        # Strip the parentheses
        stripped_string = coordinate_string.strip("()")

        # Split the string by comma
        split_strings = stripped_string.split(", ")

        # Convert the split strings into floats and create a tuple
        return tuple(float(num) for num in split_strings)
    '''
    def makeEmployeeRestriction(self, string): #Tror denne nå kan slettes - Guro
        if "," in string: 
            return string.split(",")
        try:
            return [int(string)]
        except: 
            return [] 
    '''
    
    def makeEmployeeRestriction(self, input_data): 
        list = []
        if isinstance(input_data, int):
            return list.append(input_data)
        return input_data

        
    '''
    def makePresNodes(self, string): 
        #Får inn dataen fra dataframen og returnerer to lister med presedens informasjonen 
        PrevNode = []
        PrevNodeInTime = []
        if not string: 
            return PrevNode, PrevNodeInTime
        strList = string.split(",")
        for elem in strList: 
            if ":" in elem: 
                PrevNodeInTime.append(tuple(int(part.strip()) for part in elem.split(":")))
            else: 
                PrevNode.append(int(elem))
        return PrevNode, PrevNodeInTime
    '''
    
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
    def getSkillreq(self): 
        return self.skillReq
    
    def setStartTime(self, startTime): 
        self.startTime = startTime

    def getStartTime(self):
        return self.startTime
        
    def getEmployeeRestriction(self): 
        return self.employeeRestricions

    def getNewEarliestStartTime(self): 
        if len(self.newEeariestStartTime) == 0: 
            return 0
        return max(list(self.newEeariestStartTime.values()))
 
    
    def getNewLatestStartTime(self): 
        if len(self.newLatestStartTime) == 0: 
            return 1440
        return min(list(self.newLatestStartTime.values()))
    
    def getDuration(self): 
        return self.duration
    
    def getID(self): 
        return self.id
    
    def getPickUpActivityID(self): 
        return self.pickUpActivityID
    
    def getPrevNode(self):
        return self.PrevNode 
    
    def getPrevNodeInTime(self): 
        return self.PrevNodeInTime
    
    def getHeaviness(self):
        return self.heaviness
    #set og add funsksjonene oppdatere aktivtetens parametere

    def setNewEarliestStartTime(self, newEarliestStartTimeFromDepAct, depAct): 
        #earliest starttime endres dersom den er høyere enn nåværende latest startime
        self.newEeariestStartTime[depAct] = newEarliestStartTimeFromDepAct
        #Dersom eraliest startime er høyre enn lateststartime, settes begge til null fordi aktiviten er blitt umulig å gjennomføre
        if max(self.getNewEarliestStartTime(), self.earliestStartTime) > min(self.latestStartTime, self.getNewLatestStartTime()): 
            self.possibleToInsert = False
        else: 
            self.possibleToInsert = True

    def setNewLatestStartTime(self, newLatestStartTimeFromDepAct, depAct): 
        #latest starttime endres dersom den er lavere enn nåværende latest startime
        self.newLatestStartTime[depAct] = newLatestStartTimeFromDepAct
        #Dersom eraliest startime er høyre enn lateststartime, settes begge til null fordi aktiviten er blitt umulig å gjennomføre
        if max(self.getNewEarliestStartTime(), self.earliestStartTime) > min(self.latestStartTime, self.getNewLatestStartTime()): 
            self.possibleToInsert = False
        else: 
            self.possibleToInsert = True
            
    


    def setemployeeNotAllowedDueToPickUpDelivery(self, list): 
        self.employeeNotAllowedDueToPickUpDelivery = list 


    def restartActivity(self): 
        self.startTime = None
        self.newEeariestStartTime = dict.fromkeys(self.dependentActivities, 0)
        self.newLatestStartTime = dict.fromkeys(self.dependentActivities, 1440)
        self.employeeNotAllowedDueToPickUpDelivery = []
        self.possibleToInsert = True

    def updateEmployeeHistory(self, employeeId):
        continuity_score, employeeIds = next(iter(self.employeeHistory.items()))
        employeeIds.append(employeeId)  
        self.employeeHistory[continuity_score] = employeeIds
        
#act70 = Activity( pd.read_csv("data/NodesNY.csv").set_index(["id"]) , 64)
#print("earliestStartTime", act70.newEeariestStartTime)
#print("newLatestStartTime", act70.newLatestStartTime)