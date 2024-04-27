import numpy as np
import pandas as pd
import sys
import os
sys.path.append( os.path.join(os.path.split(__file__)[0],'..') )  # Include subfolders
from objects.employee import Employee
from objects.activity import Activity
#from objects.distances import T_ij
from parameters import T_ij
import math
import copy 
from config.main_config import depot

class Route:
    def __init__(self, day, employee):
        self.employee = employee
        self.start_time = employee.getShiftStart(day) 
        self.end_time = employee.getShiftEnd(day)
        self.route = np.empty(0, dtype=object)
        self.skillLev = employee.skillLevel
        self.day = day
        self.travel_time = 0
        self.aggSkillDiff = 0 
        self.totalHeaviness = 0        
        self.suitability = 0
        #TODO: Må finne ut hvordan man vil ha det med depoet. Nå vil depoet fortrekkes ovenfor en aktivitet som allerde har noen ute. 
        #Men det er vel kanskje fint for å få moblisert de som ikke har fått noen enda 
        self.locations = []
        self.averageLocation = depot


    '''
    Ønsker å sortere rutene etter den som har best lokasjon i forhold til aktiviteten som skal legges inn.
    Hvordan skal det sees i sammenheng med hvordan det velges nå. Må vel fortsatt kunn være på skill? 

    TODO: Oppdater gjennomsnittslokasjonen når nye aktiviteter puttes inn. 
    Dersom den får noen andre aktiviter enn depoet, så settes den 
    '''

    def checkTrueFalse(self, activity): 
        if  self.employee.id == activity.employeeRestricions or (
            self.employee.id in activity.employeeNotAllowedDueToPickUpDelivery) or (
                activity.skillReq > self.skillLev) or (activity.possibleToInsert == False): 
            return False
        
        return True 


#TODO: Denne klassen kan omstrukturers slik at addActivity bruker add activity on index. Slik at det blir færre funskjoner
    def addActivity(self, activity_in):
        activity = copy.deepcopy(activity_in)
        #Kan ikke restarte den her når den muligens skal legges inn basert på infoen før 
        #activity.restartActivity()
        '''
        Funkjsonenen sjekker først om aktivitetnen oppfyller krav for å være i ruten
        Funkjsonen itererer vi over alle mellomrom mellom aktivitene som ligger i ruten. 
        Ugangspunktet er altså at ruten går fra i til j, og det skal byttes ut med å gå fra i til a og a til j 

        Arg: 
        activity (Activity) aktivitetsobjektet som skal legges til i ruten 

        Return: 
        True/False på om aktiviteten er blitt lagt til i ruten 
        '''

        if  self.employee.id == activity.employeeRestricions or (
            self.employee.id in activity.employeeNotAllowedDueToPickUpDelivery) or (
                activity.skillReq > self.skillLev) or (activity.possibleToInsert == False): 
            return False

        S_i = self.start_time
        T_ia = math.ceil(T_ij[0][activity.id])
        D_i = 0 
        index_count = 0 
        i = None

        for j in self.route: 
            self.makeSpaceForIndex(index_count)
            #Beg: Activites grenser i ruten må oppdateres etter at Makespace flytter på startTidspunkter
            self.updateActivityBasedOnDependenciesInRoute(activity) 

           
            if (activity.possibleToInsert == True) and (
                S_i + D_i + T_ia <= max(activity.earliestStartTime, activity.getNewEarliestStartTime())) and (
                max(activity.earliestStartTime, activity.getNewEarliestStartTime()) + activity.duration + math.ceil(T_ij[activity.id][j.id]) <= j.startTime):  
                activity.startTime = max(activity.earliestStartTime, activity.getNewEarliestStartTime())
                self.route = np.insert(self.route, index_count, activity)
                if activity.location != depot: 
                    self.locations.append(activity.location)
                    self.averageLocation = (sum(x[0] for x in self.locations) / len(self.locations), sum(x[1] for x in self.locations) / len(self.locations))
                return True
         
            
            if (activity.possibleToInsert == True) and (
                min(activity.latestStartTime, activity.getNewLatestStartTime()) >= S_i + D_i + T_ia) and (
                S_i + D_i + T_ia >= max(activity.earliestStartTime, activity.getNewEarliestStartTime())) and  (
                S_i + D_i + T_ia + activity.duration + math.ceil(T_ij[activity.id][j.id]) <= j.startTime): 
                activity.startTime = S_i + D_i + math.ceil(T_ia)
                self.route = np.insert(self.route, index_count, activity)
                if activity.location != depot: 
                    self.locations.append(activity.location)
                    self.averageLocation = (sum(x[0] for x in self.locations) / len(self.locations), sum(x[1] for x in self.locations) / len(self.locations))
      
                return True
            S_i = j.startTime
            T_ia = math.ceil(T_ij[j.id][activity.id])
            D_i = j.duration
            i = j 
            index_count +=1

        
        self.makeSpaceForIndex(index_count)
        #Beg: Activites grenser i ruten må oppdateres etter at Makespace flytter på startTidspunkter
        self.updateActivityBasedOnDependenciesInRoute(activity)
        if S_i != self.start_time:
            S_i = i.startTime
       
                
        if (activity.possibleToInsert == True) and (
            S_i + D_i + T_ia <= max(activity.earliestStartTime, activity.getNewEarliestStartTime())) and (
            max(activity.earliestStartTime, activity.getNewEarliestStartTime())+ activity.duration + math.ceil(T_ij[activity.id][0]) <= self.end_time): 
            activity.startTime = max(activity.earliestStartTime, activity.getNewEarliestStartTime())
            self.route = np.insert(self.route, index_count, activity)
            if activity.location != depot: 
                self.locations.append(activity.location)
                self.averageLocation = (sum(x[0] for x in self.locations) / len(self.locations), sum(x[1] for x in self.locations) / len(self.locations))
    
            return True
   
        if (activity.possibleToInsert == True) and (
            min(activity.latestStartTime, activity.getNewLatestStartTime()) >= S_i + D_i + T_ia) and (
            S_i + D_i + T_ia >= max(activity.earliestStartTime, activity.getNewEarliestStartTime())) and (
            S_i + D_i + T_ia + activity.duration + math.ceil(T_ij[activity.id][0]) <= self.end_time): 
            activity.startTime = S_i + D_i + math.ceil(T_ia)
            self.route = np.insert(self.route, index_count, activity)
            if activity.location != depot: 
                self.locations.append(activity.location)
                self.averageLocation = (sum(x[0] for x in self.locations) / len(self.locations), sum(x[1] for x in self.locations) / len(self.locations))
        
            return True

        return False 


    #Printer ruten 
    def printSoultion(self): 
        print("DAG "+str(self.day)+ " ANSATT "+str(self.employee.id))
        for a in self.route: 
            print("activity "+str(a.id)+ " start "+ str(a.startTime))    
        print("---------------------")
        
    def calculateTotalHeaviness(self):
        self.totalHeaviness = sum(act.heaviness for act in self.route)
        return self.totalHeaviness

    def updateObjective(self): 
        i = 0 
        self.travel_time = 0
        self.aggSkillDiff = 0 
        self.suitability = 0
        for act in self.route: 
            j = act.id
            self.travel_time += math.ceil(T_ij[i][j])
            i = j 
            self.aggSkillDiff += self.employee.skillLevel - act.skillReq
            self.suitability += act.suitability
        self.travel_time += math.ceil(T_ij[i][0])
   
    #TODO: Oppdates ikke oppover igjen i hierarkiet
    def removeActivityID(self, activityID):
        index = 0 
        for act in self.route: 
            if act.id == activityID: 
                self.route = np.delete(self.route, index)
                act.employeeNotAllowedDueToPickUpDelivery = []
                act.startTime = None
                self.updateActivityDependenciesInRoute(act)
                return
            index += 1 
        return

    
    def insertActivityOnIndex(self, activity, index):

        if self.checkTrueFalse(activity) == False: 
            return False

        self.makeSpaceForIndex(index)
        #Beg: Må oppdatere verdiene innad basert på det som er flyttet 

        self.updateActivityBasedOnDependenciesInRoute(activity)
        for possiblyMovedActivity in self.route: 
            self.updateActivityBasedOnDependenciesInRoute(possiblyMovedActivity)

        if len(self.route) == 0: 
            return self.insertToEmptyList(activity)
            
        if index == 0: 
            i_id = 0
            S_i = self.start_time
            D_i = 0
            T_ia = T_ij[0][activity.id]
        else:
            i = self.route[index - 1]
            i_id = i.id
            S_i = i.startTime
            D_i = i.duration
            T_ia = T_ij[i_id][activity.id]
        if index == len(self.route): 
            j_id = 0
            S_j = self.end_time
        else:
            j = self.route[index]
            j_id = j.id
            S_j = j.startTime

        if S_i + D_i + T_ia <= max(activity.earliestStartTime, activity.getNewEarliestStartTime()) and (
            max(activity.earliestStartTime, activity.getNewEarliestStartTime()) + activity.duration + math.ceil(T_ij[activity.id][j_id]) <= S_j): 
            activity.startTime = max(activity.earliestStartTime, activity.getNewEarliestStartTime())
            self.route = np.insert(self.route, index, activity)
            if activity.location != depot: 
                self.locations.append(activity.location)
                self.averageLocation = (sum(x[0] for x in self.locations) / len(self.locations), sum(x[1] for x in self.locations) / len(self.locations))
            return True
        
        if min(activity.latestStartTime, activity.getNewLatestStartTime()) >= S_i + D_i + T_ia and (
            S_i + D_i + T_ia >= max(activity.earliestStartTime, activity.getNewEarliestStartTime())) and  (
            S_i + D_i + T_ia + activity.duration + math.ceil(T_ij[activity.id][j_id]) <= S_j): 
            activity.startTime = S_i + D_i + math.ceil(T_ia)
            self.route = np.insert(self.route, index, activity)
            if activity.location != depot: 
                self.locations.append(activity.location)
                self.averageLocation = (sum(x[0] for x in self.locations) / len(self.locations), sum(x[1] for x in self.locations) / len(self.locations))
            return True
        return False 
    

    def insertToEmptyList(self, activity): 
        if self.start_time + T_ij[0][activity.id] <= max(activity.earliestStartTime, activity.getNewEarliestStartTime()) and (
            max(activity.earliestStartTime, activity.getNewEarliestStartTime()) + activity.duration + math.ceil(T_ij[activity.id][0]) <= self.end_time): 
            activity.startTime = max(activity.earliestStartTime, activity.getNewEarliestStartTime())
            self.route = np.insert(self.route, 0, activity)
            if activity.location != depot: 
                self.locations.append(activity.location)
                self.averageLocation = (sum(x[0] for x in self.locations) / len(self.locations), sum(x[1] for x in self.locations) / len(self.locations))
           
            return True
   
        if min(activity.latestStartTime, activity.getNewLatestStartTime()) >= self.start_time + T_ij[0][activity.id] and (
            self.start_time + T_ij[0][activity.id] >= max(activity.earliestStartTime, activity.getNewEarliestStartTime())) and  (
            self.start_time + T_ij[0][activity.id] + activity.duration + math.ceil(T_ij[activity.id][0]) <= self.end_time): 
            activity.startTime = self.start_time + math.ceil(T_ij[0][activity.id])
            self.route = np.insert(self.route, 0, activity)
            if activity.location != depot: 
                self.locations.append(activity.location)
                self.averageLocation = (sum(x[0] for x in self.locations) / len(self.locations), sum(x[1] for x in self.locations) / len(self.locations))
            return True
        return False 
    
    def getActivity(self, actID): 
        for act in self.route: 
            if act.id == actID: 
                return act 
        return None       


    def moveActivitiesEarlier(self, stopIndex): 
        i_id = 0
        S_i = self.start_time
        D_i = 0
        for j in range(stopIndex): 
            act = self.route[j]

            new_startTime =  max(act.earliestStartTime, act.getNewEarliestStartTime(), S_i + D_i + math.ceil(T_ij[i_id][act.id]) )
            if new_startTime < act.startTime: 
                act.startTime = new_startTime
                
                self.updateActivityDependenciesInRoute(act)
                
            i_id = act.id 
            S_i = act.startTime 
            D_i = act.duration


    def moveActivitiesLater(self, stopIndex): 
        j_id = 0
        S_j = self.end_time
       
        for i in range(len(self.route)-1, stopIndex-1, -1): 
            act = self.route[i]
            
            new_startTime = min(act.latestStartTime, act.getNewLatestStartTime(), S_j - math.ceil(T_ij[act.id][j_id]) - act.duration )
            if new_startTime > act.startTime: 
                act.startTime = new_startTime

                #Beg: Når vi endrer et startdispunkt kan det ha effeke på de neste 
                self.updateActivityDependenciesInRoute(act)
           
            j_id = act.id 
            S_j = act.startTime 
         
    
    def makeSpaceForIndex(self, index): 
        #Det er noe med oppdateringen tilbake til route_plan 
        #Når vi prøver å sette inn 63 så 
        #Når vi ved add activity oppdaterer funksjonen på ruten, så henter den de gamle ruteplanene
        self.moveActivitiesEarlier(index)
        self.moveActivitiesLater(index)

    
    def updateActivityDependenciesInRoute(self, act): 
        for nextActID in act.NextNode: 
            nextAct = self.getActivity(nextActID)
            if nextAct != None: 
                self.updateNextDependentActivityBasedOnActivityInRoute(nextAct, act)
        
        for prevActID in act.PrevNode: 
            prevAct = self.getActivity(prevActID)
            if prevAct != None: 
                self.updatePrevDependentActivityBasedOnActivityInRoute(prevAct, act)

        for nextActInTimeTupl in act.NextNodeInTime: 
            nextActInTime = self.getActivity(nextActInTimeTupl[0])
            if nextActInTime != None: 
                self.updateNextInTimeDependentActivityBasedOnActivityInRoute(nextActInTime, act, nextActInTimeTupl[1])
        
        for prevActInTimeTupl in act.PrevNodeInTime: 
            prevActInTime = self.getActivity(prevActInTimeTupl[0])
            if prevActInTime != None: 
                self.updatePrevInTimeDependentActivityBasedOnActivityInRoute(prevActInTime, act, prevActInTimeTupl[1])        

    
    #TODO: Disse funskjonene kunne kanskje bare vært gjort i funksjonen over
    def updateNextDependentActivityBasedOnActivityInRoute(self, nextAct, act):
        if act.startTime == None: 
            nextAct.setNewEarliestStartTime(0, act.id)
            return
        nextAct.setNewEarliestStartTime(act.startTime + act.duration, act.id)

    
    def updatePrevDependentActivityBasedOnActivityInRoute(self, prevAct, act):
        if act.startTime == None: 
            prevAct.setNewLatestStartTime(1440, act.id)
            return
        prevAct.setNewLatestStartTime(act.startTime - prevAct.duration, act.id)
    
    def updateNextInTimeDependentActivityBasedOnActivityInRoute(self, nextInTimeAct, act, inTime):
        if act.startTime == None: 
            nextInTimeAct.setNewLatestStartTime(1440, act.id)
            return
        nextInTimeAct.setNewLatestStartTime(act.startTime + act.duration + inTime, act.id)
        
    
    def updatePrevInTimeDependentActivityBasedOnActivityInRoute(self, prevInTimeAct, act, inTime):
        if act.startTime == None: 
            prevInTimeAct.setNewEarliestStartTime(0, act.id)
            return
        prevInTimeAct.setNewEarliestStartTime(act.startTime - inTime , act.id)


    def updateActivityBasedOnDependenciesInRoute(self, activity): 
        for prevNodeID in activity.PrevNode: 
            prevNodeAct = self.getActivity(prevNodeID)
            if prevNodeAct != None:
                activity.setNewEarliestStartTime(prevNodeAct.startTime + prevNodeAct.duration, prevNodeID)

        for nextNodeID in activity.NextNode: 
            nextNodeAct = self.getActivity(nextNodeID)
            if nextNodeAct != None:
                activity.setNewLatestStartTime(nextNodeAct.startTime - activity.duration, nextNodeID)
        
        for PrevNodeInTimeID in activity.PrevNodeInTime: 
            prevNodeAct = self.getActivity(PrevNodeInTimeID[0])
            if prevNodeAct != None:
                activity.setNewLatestStartTime(prevNodeAct.startTime+ prevNodeAct.duration + PrevNodeInTimeID[1], PrevNodeInTimeID[0])
                activity.setNewEarliestStartTime(prevNodeAct.startTime + prevNodeAct.duration, PrevNodeInTimeID[0])
                   

        for NextNodeInTimeID in activity.NextNodeInTime: 
            nextNodeAct = self.getActivity(NextNodeInTimeID[0])
            if nextNodeAct != None:
                activity.setNewEarliestStartTime(nextNodeAct.startTime - NextNodeInTimeID[1], NextNodeInTimeID[0])
                activity.setNewLatestStartTime(nextNodeAct.startTime - activity.duration, NextNodeInTimeID[0])
            