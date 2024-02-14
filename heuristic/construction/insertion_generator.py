import numpy as np 
import sys
sys.path.append("C:\\Users\\agnesost\\masters-thesis")
from objects.patterns import pattern
from objects.actitivites import Acitivity
import copy

'''
Info: PatientInsertor prøver å legge til en pasient i ruteplanen som sendes inn
TODO: Skrive mer utfyllende her
'''

class PatientInsertor:
    def __init__(self, route_plan, patients_df, treatment_df, visit_df, activities_df):
        self.treatment_df = treatment_df
        self.route_plan = route_plan
        self.activites_df = activities_df
        self.visit_df = visit_df
        self.patients_df = patients_df

        self.treatments = self.getIntList(patients_df["treatment"])
        self.rev = False

    def generate_insertions(self):
        #TODO: Her skal treaments sorteres slik at man vet hvilke som er mest. 
        #Nå itereres den over i rekkefølge 
        
        for treatment in self.treatments: 
            treatStat = False
            #Inne i en behandling, har hentet alle visits til den 
            strVis = self.treatment_df.loc[treatment, 'visit']
             
        
            visitList = self.getIntList(strVis)
            #TODO: Hente ut sett av mulig patterns som kan fungere
    
            #print("tester litt")
            #print(pattern[self.treatment_df.loc[treatment, 'pattern']])
            count_patterns = 0
            old_route_plan = copy.deepcopy(self.route_plan)


            if self.rev == True:
                patterns =  reversed(pattern[self.treatment_df.loc[treatment, 'pattern']])
                self.rev = False
            else: 
                patterns = pattern[self.treatment_df.loc[treatment, 'pattern']]
                self.rev = True


            for treatPat in patterns:
                count_patterns +=1  
                insertState = self.insert_visit_with_pattern(visitList, treatPat) 
                if insertState == True:
                   treatStat = True
                   break
                self.route_plan = copy.deepcopy(old_route_plan)
                #Hvis ikke den første fungerer så vil den bare returnere false
                #Dette er det samme problemet som det andre. Return False skal være
                #Hvis det er siste mulige pattern så blir det false 
            if treatStat == False: 
                #Hvis den er false så må self.route_plan settes tilbake til det den var
                return False
        
        return True
    
    #Denne må returnere False med en gang en ikke fungerer 
    #Det virker som at denne altid returnerer True 
    def insert_visit_with_pattern(self, visits, pattern):
        #print("Her printes visits ",visits)
        #print(pattern)
        visit_count = 0
        for day_index in range(len(pattern)): 
            if pattern[day_index] == 1: 
                state = self.insert_visit_on_day(visits[visit_count], day_index+1) 
                if state == False: 
                    return False
                visit_count += 1 
        return True   
                

    #Denne funksjonen oppdatere route_self helt til det ikke går lenger
    def insert_visit_on_day(self, visit, day):  
        strAct = self.visit_df.loc[visit, 'nodes']
        activites = self.getIntList(strAct)
        for act in activites: 
            #TODO: Her må det lages en aktivitet objekt 
            acitvity = Acitivity(self.activites_df, act)
            if acitvity.getSameEmployeeActID() != 0 and acitvity.getSameEmployeeActID() < act: 
                emplForAct = self.route_plan.getEmployeeAllocatedForActivity(acitvity.getSameEmployeeActID(), day)
                otherEmplOnDay = self.route_plan.getOtherEmplOnDay(emplForAct, day)
                acitvity.updateEmployeeRes(otherEmplOnDay) 
                
            for prevNode in acitvity.getPrevNode(): 
                prevNodeAct = self.route_plan.getActivity(prevNode, day)
                acitvity.setEarliestStartTime(prevNodeAct.getStartTime()+prevNodeAct.getDuration())

            
            for PrevNodeInTime in acitvity.getPrevNodeInTime(): 
                prevNodeAct = self.route_plan.getActivity(PrevNodeInTime[0], day)
                acitvity.setLatestStartTime(prevNodeAct.getStartTime()+PrevNodeInTime[1])
            

            state = self.route_plan.addNodeOnDay(acitvity, day)
            if state == False: 
                return False
        return True
    
    def getIntList(self, string):
        if type(string) == str and "," in string: 
            stringList = string.split(',')
        else: 
            stringList = [string]
        return  [int(x) for x in stringList]
       

    