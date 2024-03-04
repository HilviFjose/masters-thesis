import pandas as pd

'''
Info:
For å opprette en aktivitet må dataframene som inneholder aktivitetne til ID-en sendes inn og selve ID-en
'''

class Activity:
    def __init__(self, df, id):
        self.id = id 
        self.latestStartTime = df.loc[id]["latestStartTime"]
        self.earliestStartTime = df.loc[id]["earliestStartTime"]
        self.duration = df.loc[id]["activityDuration"]
        self.skillReq = df.loc[id]["skillRequirement"]
        self.pickUpActivityID = int(df.loc[id]["sameEmployeeActivityID"])
        self.location = df.loc[id]["location"]
        self.employeeRestricions = self.makeEmployeeRestriction(df.loc[id]["employeeRestriction"].replace("(", "").replace(")", ""))
        self.PrevNode, self.PrevNodeInTime= self.makePresNodes(df.loc[id]["prevpresedence"])
        #TODO: Den gjensidige avhengigheten må legges inn i datagenereringen 
        self.NextNode, self.NextNodeInTime = self.makePresNodes(df.loc[id]["nextpresedence"])
        
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
    
    def makeEmployeeRestriction(self, string): 
        if "," in string: 
            return string.split(",")
        try:
            return [int(string)]
        except: 
            return [] 
    


    def makePresNodes(self, string): 
        '''
        Får inn dataen fra dataframen og returnerer to lister med presedens informasjonen 
        '''
        PrevNode = []
        PrevNodeInTime = []
        if "(" in string: 
            return PrevNode, PrevNodeInTime
        strList = string.split(",")
        for elem in strList: 
            if ":" in elem: 
                PrevNodeInTime.append(tuple(int(part.strip()) for part in elem.split(":")))
            else: 
                PrevNode.append(int(elem))
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


act70 = Activity( pd.read_csv("data/NodesNY.csv").set_index(["id"]) , 64)
print("earliestStartTime", act70.newEeariestStartTime)
print("newLatestStartTime", act70.newLatestStartTime)