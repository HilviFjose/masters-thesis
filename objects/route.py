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

class Route:
    def __init__(self, day, employee):
        self.employee = employee
        self.start_time = employee.getShiftStart(day) 
        self.end_time = employee.getShiftEnd(day)
        self.route = []
        self.skillLev = employee.getSkillLevel()
        self.day = day
        self.travel_time = 0
        self.aggSkillDiff = 0 
        self.totalHeaviness = 0        
        self.suitability = 0



    def addActivity(self, activity_in):
        activity = copy.deepcopy(activity_in)
        # Initial checks to see if the activity can be inserted into the route
        if (self.employee.getID() == activity.employeeRestrictions or
            self.employee.getID() in activity.employeeNotAllowedDueToPickUpDelivery or
            activity.skillReq > self.skillLev or not activity.possibleToInsert): 
            return False
        
        for index in range(len(self.route) + 1):
            # Before trying to insert, make space for the activity and update dependencies if necessary
            #self.makeSpaceForIndex(index)
            #self.updateActivityBasedOnDependenciesInRoute(activity)
            
            # Try to insert the activity using insertActivityOnIndex
            if self.insertActivityOnIndex(activity, index):
                return True
        return False
    
    def insertActivityOnIndex(self, activity, index):
        self.makeSpaceForIndex(index)
        self.updateActivityBasedOnDependenciesInRoute(activity)
        if len(self.route) == 0: 
            return self.insertToEmptyList(activity)
        
        S_i = self.start_time if index == 0 else self.route[index - 1].startTime
        D_i = 0 if index == 0 else self.route[index - 1].duration
        T_ia = T_ij[0][activity.id] if index == 0 else T_ij[self.route[index - 1].id][activity.id]
        S_j = self.end_time if index == len(self.route) else self.route[index].startTime
        j_id = 0 if index == len(self.route) else self.route[index].id
        earliest_possible_start = max(activity.earliestStartTime, activity.getNewEarliestStartTime())
        latest_possible_start = min(activity.latestStartTime, activity.getNewLatestStartTime())
        activity_end_time = earliest_possible_start + activity.duration + math.ceil(T_ij[activity.id][j_id])

        # First condition: Check if the activity fits starting from the earliest possible start
        if S_i + D_i + T_ia <= earliest_possible_start and activity_end_time <= S_j:
            activity.setStartTime(earliest_possible_start)
            self.route.insert(index, activity)
            return True
        
        # Second condition: Check based on the latest possible start, but still fitting before the next activity or end time
        if S_i + D_i + T_ia <= latest_possible_start and S_i + D_i + T_ia + activity.duration + math.ceil(T_ij[activity.id][j_id]) <= S_j:
            activity.setStartTime(S_i + D_i + T_ia)
            self.route.insert(index, activity)
            return True
        return False


    
    #Dette er alternativ måte å regne ut objektivet. Slik at ikke alt ligger i routeplan 
    def updateObjective(self): 
        i = 0 
        travel_time = 0 
        aggregated_skilldiff = 0
        for act in self.route: 
            j = act.id
            travel_time += math.ceil(T_ij[i][j])
            i = j 
            aggregated_skilldiff += self.employee.getSkillLevel() - act.skillReq
        travel_time += math.ceil(T_ij[i][0])
        self.aggSkillDiff= aggregated_skilldiff
        self.travel_time = travel_time

        
    def calculateTotalHeaviness(self):
        self.totalHeaviness = sum([act.heaviness for act in self.route])
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
            self.aggSkillDiff += self.employee.getSkillLevel() - act.skillReq
            self.suitability += act.suitability
        self.travel_time += math.ceil(T_ij[i][0])
   
    #TODO: Oppdates ikke oppover igjen i hierarkiet
    def removeActivityID(self, activityID):
        #if activityID == 48: 
        index = 0 
        for act in self.route: 
            if act.id == activityID: 
                del self.route[index]
                act.employeeNotAllowedDueToPickUpDelivery = []
                act.startTime = None
                self.updateActivityDependenciesInRoute(act)
                return
            index += 1 
        return
    

    def insertToEmptyList(self, activity):
        # Calculate common variables used in both conditions
        earliest_start = max(activity.earliestStartTime, activity.getNewEarliestStartTime())
        latest_start = min(activity.latestStartTime, activity.getNewLatestStartTime())
        travel_time_to_activity = math.ceil(T_ij[0][activity.id])
        travel_time_from_activity = math.ceil(T_ij[activity.id][0])
        activity_start_with_travel = self.start_time + travel_time_to_activity
        activity_end_with_travel = earliest_start + activity.duration + travel_time_from_activity

        # First condition: Check if activity can start after earliest possible start time and finish before end time
        if activity_start_with_travel <= earliest_start and activity_end_with_travel <= self.end_time:
            activity.setStartTime(earliest_start)
            self.route.insert(0, activity)
            return True

        # Second condition: Adjusted to check if the activity can also start based on the latest start time constraint
        if activity_start_with_travel <= latest_start and activity_end_with_travel <= self.end_time:
            activity.setStartTime(activity_start_with_travel)
            self.route.insert(0, activity)
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
            travel_time = math.ceil(T_ij[i_id][act.id])
            new_startTime = max(act.earliestStartTime, act.getNewEarliestStartTime(), S_i + D_i + travel_time)
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
            travel_time_backward = math.ceil(T_ij[act.id][j_id])
            new_startTime = min(act.latestStartTime, act.getNewLatestStartTime(), S_j - travel_time_backward - act.duration)
            if new_startTime > act.startTime:
                act.startTime = new_startTime
                self.updateActivityDependenciesInRoute(act)
            j_id = act.id
            S_j = act.startTime
         
    def makeSpaceForIndex(self, index): 
        self.moveActivitiesEarlier(index)
        self.moveActivitiesLater(index)


    def getActivity(self, ActID):
        for activity in self.route:
            if activity.id == ActID:
                return activity
        return None
    
    def updateActivityDependenciesInRoute(self, act):
        # Create a dictionary mapping IDs to activities for quick lookup
        uniqueActIDs = set(act.NextNode + act.PrevNode + [node[0] for node in act.NextNodeInTime] + [node[0] for node in act.PrevNodeInTime])
        activityDict = {activity.id: activity for activity in self.route if activity.id in uniqueActIDs}

        # Update based on NextNode
        for nextActID in act.NextNode:
            nextAct = activityDict.get(nextActID)
            if nextAct is not None:
                self.updateNextDependentActivityBasedOnActivityInRoute(nextAct, act)

        # Update based on PrevNode
        for prevActID in act.PrevNode:
            prevAct = activityDict.get(prevActID)
            if prevAct is not None:
                self.updatePrevDependentActivityBasedOnActivityInRoute(prevAct, act)

        # Update based on NextNodeInTime
        for nextActInTimeTupl in act.NextNodeInTime:
            nextActInTime = activityDict.get(nextActInTimeTupl[0])
            if nextActInTime is not None:
                self.updateNextInTimeDependentActivityBasedOnActivityInRoute(nextActInTime, act, nextActInTimeTupl[1])

        # Update based on PrevNodeInTime
        for prevActInTimeTupl in act.PrevNodeInTime:
            prevActInTime = activityDict.get(prevActInTimeTupl[0])
            if prevActInTime is not None:
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
        activityDict = {activity.id: activity for activity in self.route}
        # Update based on PrevNode
        for prevNodeID in activity.PrevNode:
            prevNodeAct = activityDict.get(prevNodeID)
            if prevNodeAct is not None:
                activity.setNewEarliestStartTime(prevNodeAct.startTime + prevNodeAct.duration, prevNodeID)

        # Update based on NextNode
        for nextNodeID in activity.NextNode:
            nextNodeAct = activityDict.get(nextNodeID)
            if nextNodeAct is not None:
                activity.setNewLatestStartTime(nextNodeAct.startTime - activity.duration, nextNodeID)
            
        # Update based on PrevNodeInTime
        for prevNodeInTimeID, timeDelta in activity.PrevNodeInTime:
            prevNodeAct = activityDict.get(prevNodeInTimeID)
            if prevNodeAct is not None:
                activity.setNewLatestStartTime(prevNodeAct.startTime + prevNodeAct.duration + timeDelta, prevNodeInTimeID)

        # Update based on NextNodeInTime
        for nextNodeInTimeID, timeDelta in activity.NextNodeInTime:
            nextNodeAct = activityDict.get(nextNodeInTimeID)
            if nextNodeAct is not None:
                activity.setNewEarliestStartTime(nextNodeAct.startTime - timeDelta, nextNodeInTimeID)

    #Printer ruten 
    def printSoultion(self): 
        print("DAG "+str(self.day)+ " ANSATT "+str(self.employee.getID()))
        for a in self.route: 
            print("activity "+str(a.id)+ " start "+ str(a.startTime))    
        print("---------------------")