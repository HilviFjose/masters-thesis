import pandas as pd

class Acitivity:
    def __init__(self, df, id):
        #self.key = df.iloc[id].key
        self.id = id 
        self.latestStartTime = df.loc[id]["latestStartTime"]
        self.earliestStartTime = df.loc[id]["earliestStartTime"]
        self.duration = df.loc[id]["activityDuration"]
        self.skillReq = df.loc[id]["skillRequirement"]
        self.sameEmployeeActivityID = int(df.loc[id]["sameEmployeeActivityID"])
        self.location = df.loc[id]["location"]
        self.employeeRestricions = self.makeEmployeeRestriction(df.loc[id]["employeeRestriction"].replace("(", "").replace(")", ""))
        self.PrevNode, self.PrevNodeInTime= self.makePresNodes(df.loc[id]["presedence"])
        self.startTime = None
    
    def getSkillreq(self): 
        return self.skillReq
    
    def setStartTime(self, startTime): 
        self.startTime = startTime

    def getStartTime(self):
        return self.startTime
    
    def makeEmployeeRestriction(self, string): 
        if "," in string: 
            return string.split(",")
        try:
            return [int(string)]
        except: 
            return [] 
        
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
    

    '''
    Hvordan skal det se ut. 
    PrevNodeInTime 
    PrevNode
    '''
    def makePresNodes(self, string): 
        PrevNode = []
        PrevNodeInTime = []
        if "(" in string: 
            return PrevNode, PrevNodeInTime
        strList = string.split(",")
        #print("strList", strList)
        for elem in strList: 
            #print("elem", elem)
            if ":" in elem: 
                PrevNodeInTime.append(tuple(int(part.strip()) for part in elem.split(":")))
            else: 
                #print("PrevNode1", PrevNode)
                PrevNode.append(int(elem))
                #print("PrevNode2", PrevNode)
       #print("returning ", PrevNode, PrevNodeInTime )
        return PrevNode, PrevNodeInTime

    def setLatestStartTime(self, newLatestStartTime): 
        if newLatestStartTime< self.latestStartTime: 
            self.latestStartTime = newLatestStartTime

    def setEarliestStartTime(self, newEarliestStartTime): 
        if newEarliestStartTime > self.earliestStartTime: 
            self.earliestStartTime = newEarliestStartTime
        if newEarliestStartTime > self.latestStartTime: 
            self.earliestStartTime = self.latestStartTime
    
    def updateEmployeeRes(self,unAllowedEmployee):
        try: 
            self.employeeRestricions += unAllowedEmployee
        except: 
            a = 0 

    def getSameEmployeeActID(self): 
        return self.sameEmployeeActivityID
    
    def getPrevNode(self):
        return self.PrevNode 
    
    
    def getPrevNodeInTime(self): 
        return self.PrevNodeInTime
#Dette skjer før vi setter starttidspunktet. 
#Vi setter ikke starttidspunktet


'''
Sliter med å forstå hvordan aktivitenene skal henge sammen
De har jo egenskaper mellom hverandre som presedens og same employee ID





df_activities  = pd.read_csv("data/NodesNY.csv").set_index(["id"]) 


act1 = Acitivity(df_activities, 15)
print(print(act1.getID()))
print("employeeRes",act1.getEmployeeRestriction())
act1.updateEmployeeRes([5])
print("employeeRes",act1.getEmployeeRestriction())
print("act.sameEmployeeActivityID", act1.sameEmployeeActivityID)
print("----------")
print("earliest and latest")
print(act1.getEarliestStartTime())
print(act1.getLatestStartTime())
print("act1.getDuration()",act1.getDuration())
print("act1.getPrevNodeInTime()", act1.getPrevNodeInTime())
print("act1.getPrevNode()", act1.getPrevNode())
print("act1.PrevNode", act1.PrevNode)
print("act1.PrevNodeInTime", act1.PrevNodeInTime)
#print(act1.key.astype(int))
#print(act1.key)
'''

'''
Det går ann å legge til employee restrictions så vi sjekker det først. 
Må ha same employee aktcity noden

Hvordan vil jeg at dataen skal se ut? 
Skal informasjonen være begge veier? Nå plasseres en først, også en annen.
Så i dette datasettet vil vi i den påfølgende lagre den første 
'''