import pandas as pd

class Acitivity:
    def __init__(self, df, id):
        self.id = df.iloc[id].keys()
        self.latestStartTime = df.iloc[id]["latestStartTime"]
        self.duation = df.iloc[id]["activityDuration"]
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

'''
Sliter med å forstå hvordan aktivitenene skal henge sammen
De har jo egenskaper mellom hverandre som presedens og same employee ID
'''


df_activities  = pd.read_csv("data/NodesNY.csv").set_index(["id"]) 

act1 = Acitivity(df_activities, 5)
print(act1.getEmployeeRestriction())


'''
Dette kan være bra fordi vi ikke skal opprette alle aktiviter med en gang
Hvis vi tar det pasienthvis så iterer vi først over alle de som er til en pasient 
Da lager vi ikke fisse objektene før ette en stund 
'''