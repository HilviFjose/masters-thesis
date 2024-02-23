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
        self.duration = df.loc[id]["duration"]
        self.skillReq = df.loc[id]["skillRequirement"]
        self.pickUpActivityID = df.loc[id]["sameEmployeeActivityId"]
        self.location = df.loc[id]["location"]
        self.employeeRestricions = df.loc[id]["employeeRestriction"]
        self.PrevNode, self.PrevNodeInTime= self.makePresNodes(df.loc[id]["prevPrece"])
        self.startTime = None
        self.newLatestStartTime = 1440
        self.newEeariestStartTime = 0
        self.employeeNotAllowedDueToPickUpDelivery = []
        self.possibleToInsert = True

    #make funskjonene setter parameterne til Acitivy objektet 
    
    def makeEmployeeRestriction(self, string): #Tror denne nå kan slettes - Guro
        if "," in string: 
            return string.split(",")
        try:
            return [int(string)]
        except: 
            return [] 
        
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
        
        # If input_data is a string, proceed with the original logic
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

    def setNewEarliestStartTime(self, newEarliestStartTime): 
        #earliest starttime endres dersom den er høyere enn nåværende latest startime
        if newEarliestStartTime > self.newEeariestStartTime: 
            self.newEeariestStartTime = newEarliestStartTime
        #Dersom eraliest startime er høyre enn lateststartime, settes begge til null fordi aktiviten er blitt umulig å gjennomføre
        if max(self.newEeariestStartTime, self.earliestStartTime) > min(self.latestStartTime, self.newLatestStartTime): 
            self.possibleToInsert = False

    def setNewLatestStartTime(self, newLatestStartTime): 
        #latest starttime endres dersom den er lavere enn nåværende latest startime
        if newLatestStartTime < self.newLatestStartTime: 
            self.newLatestStartTime = newLatestStartTime
        #Dersom eraliest startime er høyre enn lateststartime, settes begge til null fordi aktiviten er blitt umulig å gjennomføre
        if max(self.newEeariestStartTime, self.earliestStartTime) > min(self.latestStartTime, self.newLatestStartTime): 
            self.possibleToInsert = False 
            

    
    
    '''
    def setLatestStartTime(self, newLatestStartTime): 
        #latest starttime endres dersom den er lavere enn nåværende latest startime
        if newLatestStartTime< self.latestStartTime: 
            self.latestStartTime = newLatestStartTime
        #Dersom eraliest startime er høyre enn lateststartime, settes begge til null fordi aktiviten er blitt umulig å gjennomføre
        if self.earliestStartTime > newLatestStartTime: 
            self.earliestStartTime = 0
            self.latestStartTime = 0

    def setEarliestStartTime(self, newEarliestStartTime): 
        #earliest starttime endres dersom den er høyere enn nåværende latest startime
        if newEarliestStartTime > self.earliestStartTime: 
            self.earliestStartTime = newEarliestStartTime
        #Dersom eraliest startime er høyre enn lateststartime, settes begge til null fordi aktiviten er blitt umulig å gjennomføre
        if newEarliestStartTime > self.latestStartTime: 
            self.earliestStartTime = 0
            self.latestStartTime = 0
    '''

    def setemployeeNotAllowedDueToPickUpDelivery(self, list): 
        self.employeeNotAllowedDueToPickUpDelivery = list 

        


