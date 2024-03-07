import numpy as np
import pandas as pd
import sys
import os
sys.path.append( os.path.join(os.path.split(__file__)[0],'..') )  # Include subfolders
from objects.employee import Employee
from objects.activity import Activity
from objects.distances import T_ij
import math
import copy 

class Route:
    def __init__(self, day, employee):
        self.employee = employee
        self.start_time = employee.getShiftStart(day) 
        self.end_time = employee.getShiftEnd(day)
        self.route = np.empty(0, dtype=object)
        self.skillLev = employee.getSkillLevel()
        self.day = day
        self.travel_time = 0
        self.aggSkillDiff = 0 
        self.suitability = 0




#TODO: Denne klassen kan omstrukturers slik at addActivity bruker add activity on index. Slik at det blir færre funskjoner
    def addActivity(self, activity_in):
        activity = copy.deepcopy(activity_in)
      

        if  self.employee.getID() in activity.getEmployeeRestriction() or (
            self.employee.getID() in activity.employeeNotAllowedDueToPickUpDelivery) or (
                activity.getSkillreq() > self.skillLev) or (activity.possibleToInsert == False): 
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
                max(activity.earliestStartTime, activity.getNewEarliestStartTime()) + activity.getDuration() + math.ceil(T_ij[activity.getID()][j.getID()]) <= j.getStartTime()):  
                activity.setStartTime(max(activity.earliestStartTime, activity.getNewEarliestStartTime()))
                self.route = np.insert(self.route, index_count, activity)
                return True
         
            
            if (activity.possibleToInsert == True) and (
                min(activity.latestStartTime, activity.getNewLatestStartTime()) >= S_i + D_i + T_ia) and (
                S_i + D_i + T_ia >= max(activity.earliestStartTime, activity.getNewEarliestStartTime())) and  (
                S_i + D_i + T_ia + activity.getDuration() + math.ceil(T_ij[activity.getID()][j.getID()]) <= j.getStartTime()): 
                activity.setStartTime(S_i + D_i + math.ceil(T_ia))
                self.route = np.insert(self.route, index_count, activity)
       
                return True
            S_i = j.getStartTime()
            T_ia = math.ceil(T_ij[j.getID()][activity.getID()])
            D_i = j.getDuration()
            i = j 
            index_count +=1

        
        self.makeSpaceForIndex(index_count)
        #Beg: Activites grenser i ruten må oppdateres etter at Makespace flytter på startTidspunkter
        self.updateActivityBasedOnDependenciesInRoute(activity)
        if S_i != self.start_time:
            S_i = i.getStartTime()
       
                
        if (activity.possibleToInsert == True) and (
            S_i + D_i + T_ia <= max(activity.earliestStartTime, activity.getNewEarliestStartTime())) and (
            max(activity.earliestStartTime, activity.getNewEarliestStartTime())+ activity.getDuration() + math.ceil(T_ij[activity.getID()][0]) <= self.end_time): 
            activity.setStartTime(max(activity.earliestStartTime, activity.getNewEarliestStartTime()))
            self.route = np.insert(self.route, index_count, activity)
          
            return True
   
        if (activity.possibleToInsert == True) and (
            min(activity.latestStartTime, activity.getNewLatestStartTime()) >= S_i + D_i + T_ia) and (
            S_i + D_i + T_ia >= max(activity.earliestStartTime, activity.getNewEarliestStartTime())) and (
            S_i + D_i + T_ia + activity.getDuration() + math.ceil(T_ij[activity.getID()][0]) <= self.end_time): 
            activity.setStartTime(S_i + D_i + math.ceil(T_ia))
            self.route = np.insert(self.route, index_count, activity)
           
            return True

        return False 


    #Printer ruten 
    def printSoultion(self): 
        print("DAG "+str(self.day)+ " ANSATT "+str(self.employee.getID()))
        for a in self.route: 
            print("activity "+str(a.getID())+ " start "+ str(a.getStartTime()))    
        print("---------------------")

    #TODO: Denne fungerer ikke nå for skill d
    #Dette er alternativ måte å regne ut objektivet. Slik at ikke alt ligger i routeplan 
    def updateObjective(self): 
        i = 0 
        travel_time = 0 
        aggregated_skilldiff = 0
        aggsuit = 0
        for act in self.route: 
            j = act.getID()
            travel_time += math.ceil(T_ij[i][j])
            i = j 
            aggregated_skilldiff += self.employee.getSkillLevel() - act.getSkillreq()
            aggsuit += act.suitability
        travel_time += math.ceil(T_ij[i][0])
        self.aggSkillDiff= aggregated_skilldiff
        self.travel_time = travel_time
        self.aggregated_suitability = aggsuit
    
    #TODO: Oppdates ikke oppover igjen i hierarkiet
    def removeActivityID(self, activityID):
        index = 0 
        for act in self.route: 
            if act.getID() == activityID: 
                self.route = np.delete(self.route, index)
                act.employeeNotAllowedDueToPickUpDelivery = []
                act.startTime = None
                self.updateActivityDependenciesInRoute(act)
                return
            index += 1 
        #print("Activity", activity.getID() , " not found in route employee", self.getEmployee().getID(), "on day", self.day)
        return

    
    def insertActivityOnIndex(self, activity, index):
   
        
        self.makeSpaceForIndex(index)
        #Beg: Må oppdatere verdiene innad basert på det som er flyttet 
        self.updateActivityBasedOnDependenciesInRoute(activity)

        if len(self.route) == 0: 
            return self.insertToEmptyList(activity)
            
        if index == 0: 
            i_id = 0
            S_i = self.start_time
            D_i = 0
            T_ia = T_ij[0][activity.getID()]
        else:
            i = self.route[index - 1]
            i_id = i.getID()
            S_i = i.startTime
            D_i = i.duration
            T_ia = T_ij[i_id][activity.getID()]
        if index == len(self.route): 
            j_id = 0
            S_j = self.end_time
        else:
            j = self.route[index]
            j_id = j.getID()
            S_j = j.startTime

        if S_i + D_i + T_ia <= max(activity.earliestStartTime, activity.getNewEarliestStartTime()) and (
            max(activity.earliestStartTime, activity.getNewEarliestStartTime()) + activity.getDuration() + math.ceil(T_ij[activity.getID()][j_id]) <= S_j): 
            activity.setStartTime(max(activity.earliestStartTime, activity.getNewEarliestStartTime()))
            self.route = np.insert(self.route, index, activity)
            return True
        
        if min(activity.latestStartTime, activity.getNewLatestStartTime()) >= S_i + D_i + T_ia and (
            S_i + D_i + T_ia >= max(activity.earliestStartTime, activity.getNewEarliestStartTime())) and  (
            S_i + D_i + T_ia + activity.getDuration() + math.ceil(T_ij[activity.getID()][j_id]) <= S_j): 
            activity.setStartTime(S_i + D_i + math.ceil(T_ia))
            self.route = np.insert(self.route, index, activity)
            return True
        return False 
    

    def insertToEmptyList(self, activity): 
        if self.start_time + T_ij[0][activity.id] <= max(activity.earliestStartTime, activity.getNewEarliestStartTime()) and (
            max(activity.earliestStartTime, activity.getNewEarliestStartTime()) + activity.getDuration() + math.ceil(T_ij[activity.getID()][0]) <= self.end_time): 
            activity.setStartTime(max(activity.earliestStartTime, activity.getNewEarliestStartTime()))
            self.route = np.insert(self.route, 0, activity)
            return True
   
        if min(activity.latestStartTime, activity.getNewLatestStartTime()) >= self.start_time + T_ij[0][activity.id] and (
            self.start_time + T_ij[0][activity.id] >= max(activity.earliestStartTime, activity.getNewEarliestStartTime())) and  (
            self.start_time + T_ij[0][activity.id] + activity.getDuration() + math.ceil(T_ij[activity.getID()][0]) <= self.end_time): 
            activity.setStartTime(self.start_time + math.ceil(T_ij[0][activity.id]))
            self.route = np.insert(self.route, 0, activity)
            return True
        return False 
    
    def getActivity(self, actID): 
        for act in self.route: 
            if act.getID() == actID: 
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


    def getActivity(self, ActID):
        for activity in self.route:
            if activity.id == ActID:
                return activity
        return None
    
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
        nextAct.setNewEarliestStartTime(act.getStartTime() + act.getDuration(), act.id)

    
    def updatePrevDependentActivityBasedOnActivityInRoute(self, prevAct, act):
        if act.startTime == None: 
            prevAct.setNewLatestStartTime(1440, act.id)
            return
        prevAct.setNewLatestStartTime(act.getStartTime() - prevAct.duration, act.id)
    
    def updateNextInTimeDependentActivityBasedOnActivityInRoute(self, nextInTimeAct, act, inTime):
        if act.startTime == None: 
            nextInTimeAct.setNewLatestStartTime(1440, act.id)
            return
        nextInTimeAct.setNewLatestStartTime(act.getStartTime() + act.duration + inTime, act.id)
        
    
    def updatePrevInTimeDependentActivityBasedOnActivityInRoute(self, prevInTimeAct, act, inTime):
        if act.startTime == None: 
            prevInTimeAct.setNewEarliestStartTime(0, act.id)
            return
        prevInTimeAct.setNewEarliestStartTime(act.getStartTime() - inTime , act.id)


    def updateActivityBasedOnDependenciesInRoute(self, activity): 
        for prevNodeID in activity.PrevNode: 
            prevNodeAct = self.getActivity(prevNodeID)
            if prevNodeAct != None:
                activity.setNewEarliestStartTime(prevNodeAct.getStartTime() + prevNodeAct.getDuration(), prevNodeID)

        for nextNodeID in activity.NextNode: 
            nextNodeAct = self.getActivity(nextNodeID)
            if nextNodeAct != None:
                activity.setNewLatestStartTime(nextNodeAct.getStartTime() - activity.getDuration(), nextNodeID)
        
        for PrevNodeInTimeID in activity.PrevNodeInTime: 
            prevNodeAct = self.getActivity(PrevNodeInTimeID[0])
            if prevNodeAct != None:
                activity.setNewLatestStartTime(prevNodeAct.getStartTime()+ prevNodeAct.duration + PrevNodeInTimeID[1], PrevNodeInTimeID[0])


        for NextNodeInTimeID in activity.NextNodeInTime: 
            nextNodeAct = self.getActivity(NextNodeInTimeID[0])
            if nextNodeAct != None:
                activity.setNewEarliestStartTime(nextNodeAct.getStartTime() - NextNodeInTimeID[1], NextNodeInTimeID[0])