import pandas as pd

class Acitivity:
    def __init__(self, df, id):
        self.key = df.iloc[id].keys()
        self.id = id 
        self.latestStartTime = df.iloc[id]["latestStartTime"]
        self.earliestStartTime = df.iloc[id]["earliestStartTime"]
        self.duration = df.iloc[id]["activityDuration"]
        self.skillReq = df.iloc[id]["skillRequirement"]
        self.sameEmployeeActivityID = df.iloc[id]["sameEmployeeActivityID"]
        self.location = df.iloc[id]["location"]
        self.employeeRestricion = df.iloc[id]["employeeRestriction"].replace("(", "").replace(")", "")
        self.startTime = None
    
    def getSkillreq(self): 
        return self.skillReq
    
    def setStartTime(self, startTime): 
        self.startTime = startTime

    def getStartTime(self):
        return self.startTime
    
    def getEmployeeRestriction(self): 
        try:
            return int(self.employeeRestricion)
        except: 
            return 0 

    def getEarliestStartTime(self): 
        return self.earliestStartTime
    
    def getLatestStartTime(self): 
        return self.latestStartTime
    
    def getDuration(self): 
        return self.duration
    
    def getID(self): 
        return self.id
    
'''
Sliter med å forstå hvordan aktivitenene skal henge sammen
De har jo egenskaper mellom hverandre som presedens og same employee ID
'''


df_activities  = pd.read_csv("data/NodesNY.csv").set_index(["id"]) 

act1 = Acitivity(df_activities, 5)
print(print(act1.getID()))
print("employeeRes",act1.getEmployeeRestriction())
print("----------")
print("earliest and latest")
print(act1.getEarliestStartTime())
print(act1.getLatestStartTime())


'''
Dette kan være bra fordi vi ikke skal opprette alle aktiviter med en gang
Hvis vi tar det pasienthvis så iterer vi først over alle de som er til en pasient 
Da lager vi ikke fisse objektene før ette en stund 
'''