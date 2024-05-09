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
    def __init__(self, activities_array, id):
        self.id = id 
        #activities_array[0] =  ['patientId', 'activityType', 'numActivitiesInVisit', 'earliestStartTime', 'latestStartTime', 'duration', 'synchronisation',
        #'skillRequirement', 'clinic', 'nextPrece', 'prevPrece', 'sameEmployeeActivityId', 'visitId', 'treatmentId', 'location', 'employeeRestriction', 
        #'heaviness', 'utility' 'allocation' 'patternType' 'employeeHistory' 'continuityGroup' 'specialisationPreferred' 'a_complexity' 'v_complexity' 'nActInTreat'
        #'t_complexity' 'nActInPatient']
        self.latestStartTime = activities_array[id][4]
        self.earliestStartTime = activities_array[id][3]
        self.duration = activities_array[id][5]
        self.skillReq = activities_array[id][7]
        self.heaviness = activities_array[id][16]
        self.sameEmployeeAcitivtyID = activities_array[id][11]
        self.location = self.makeLocationTuple(activities_array[id][14])  
        self.employeeRestricions = activities_array[id][15]
        self.continuityGroup = activities_array[id][21]
        self.employeeHistory = activities_array[id][20]
        self.PrevNode, self.PrevNodeInTime= self.makePresNodes(activities_array[id][10])
        #TODO: Den gjensidige avhengigheten må legges inn i datagenereringen 
        self.NextNode, self.NextNodeInTime = self.makePresNodes(activities_array[id][9])
        self.patient = activities_array[id][0]
        self.treatmentId = activities_array[id][13]
        self.nActInPatient = activities_array[id][27]
        self.nActInTreat = activities_array[id][25]
        self.nActInVisit = activities_array[id][2]
        self.suitability = activities_array[id][17]
        self.prefSpes = activities_array[id][22]
        self.visitId = activities_array[id][12]
        
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

    def getNewEarliestStartTime(self): 
        if len(self.newEeariestStartTime) == 0: 
            return 0
        return max(list(self.newEeariestStartTime.values()))
 
    
    def getNewLatestStartTime(self): 
        if len(self.newLatestStartTime) == 0: 
            return 1440
        return min(list(self.newLatestStartTime.values()))


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
            
 

 