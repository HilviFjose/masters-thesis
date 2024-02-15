import pandas as pd

'''
Info:
For å opprette en aktivitet må dataframene som inneholder aktivitetne til ID-en sendes inn og selve ID-en
'''

class Acitivity:
    def __init__(self, df, id):
        self.id = id 
        self.latestStartTime = df.loc[id]["latestStartTime"]
        self.earliestStartTime = df.loc[id]["earliestStartTime"]
        self.duration = df.loc[id]["activityDuration"]
        self.skillReq = df.loc[id]["skillRequirement"]
        self.pickUpActivityID = int(df.loc[id]["sameEmployeeActivityID"])
        self.location = df.loc[id]["location"]
        self.employeeRestricions = self.makeEmployeeRestriction(df.loc[id]["employeeRestriction"].replace("(", "").replace(")", ""))
        self.PrevNode, self.PrevNodeInTime= self.makePresNodes(df.loc[id]["presedence"])
        self.startTime = None

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

    def getEarliestStartTime(self): 
        return self.earliestStartTime
    
    def getLatestStartTime(self): 
        return self.latestStartTime
    
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

    def setLatestStartTime(self, newLatestStartTime): 
        if newLatestStartTime< self.latestStartTime: 
            self.latestStartTime = newLatestStartTime

    def setEarliestStartTime(self, newEarliestStartTime): 
        if newEarliestStartTime > self.earliestStartTime: 
            self.earliestStartTime = newEarliestStartTime
        if newEarliestStartTime > self.latestStartTime: 
            self.earliestStartTime = self.latestStartTime
    
    def addEmployeeRes(self, unAllowedEmployees):
        self.employeeRestricions += unAllowedEmployees
        


