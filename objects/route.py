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
from config.construction_config import depot

class Route:
    def __init__(self, day, employee):
        self.employee = employee
        self.start_time = employee.shifts[day]["startShift"] 
        self.end_time = employee.shifts[day]["endShift"]
        self.route = []
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

        self.lastIndexUpdate = None

        #Flyttingen er mer omfattende når forrige status var True, så vi begynner med den 
        self.latestInsertStatus = True
        self.latestModificationWasRemove = False



    '''
    Ønsker å sortere rutene etter den som har best lokasjon i forhold til aktiviteten som skal legges inn.
    Hvordan skal det sees i sammenheng med hvordan det velges nå. Må vel fortsatt kunn være på skill? 

    TODO: Oppdater gjennomsnittslokasjonen når nye aktiviteter puttes inn. 
    Dersom den får noen andre aktiviter enn depoet, så settes den 

    Kan også fjerne fra ruta. 
    Må ta med det i beregningen. Det kan altså ha blitt fjernet. 
    
    Forutsetter alle fjerninger av aktiviteter skjer gjennom funskjonen 

    Alternativer: 
    1) tar bort en aktivitete som har index til vesntre fra siste oppdaterte index.- > De til venstre for flyttet trenger ikke flyttes. Alle mellom må flyttes, og lst updated oppdateres til
    Kan ikke flytte på noe etter removed. Kan lage en som heter last removed index. Når du setter inn en ny, så må last removed settes null. 
    Spørsmålet er hva som var det siste som ble gjort, var det en innsetting, altså et flytt, eller var det remove, sånn at vi må ta med det i bildet når vi flytter på nytt


    Alternativer til løsning: 
    Rask løsning: Dersom siste er remove, så flytter vi bare alle. Hvor ofte vil dette være. 
    I lokalsøket hopper vi endel mellom 

    Dersom forrige modifikasjon var remove, så må det være en ny innsetting før vi kan si at forrige index er gjeldene

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
       
        if  self.employee.id == activity.employeeRestricions or (
            self.employee.id in activity.employeeNotAllowedDueToPickUpDelivery) or (
                activity.skillReq > self.skillLev) or (activity.possibleToInsert == False): 
            return False

        S_i = self.start_time
        T_ia = math.ceil(T_ij[0][activity.id])
        D_i = 0 
        index_count = 0 
        i = None

        #TODO: Virker ikke som at det er så stor forskjell på brukes av første loop og andre loop 
        for j in self.route: 
            self.makeSpaceForIndex(index_count)
            #Beg: Activites grenser i ruten må oppdateres etter at Makespace flytter på startTidspunkter
            self.updateActivityBasedOnDependenciesInRoute(activity) 
            
           
            if (activity.possibleToInsert == True) and (
                S_i + D_i + T_ia <= max(activity.earliestStartTime, activity.getNewEarliestStartTime())) and (
                max(activity.earliestStartTime, activity.getNewEarliestStartTime()) + activity.duration + math.ceil(T_ij[activity.id][j.id]) <= j.startTime):  
                activity.startTime = max(activity.earliestStartTime, activity.getNewEarliestStartTime())
                self.route.insert(index_count, activity) 
                if activity.location != depot: 
                    self.locations.append(activity.location)
                    self.averageLocation = (sum(x[0] for x in self.locations) / len(self.locations), sum(x[1] for x in self.locations) / len(self.locations))
                self.lastIndexUpdate = index_count
                self.latestInsertStatus = True
                self.latestModificationWasRemove = False
                return True
         
            
            if (activity.possibleToInsert == True) and (
                min(activity.latestStartTime, activity.getNewLatestStartTime()) >= S_i + D_i + T_ia) and (
                S_i + D_i + T_ia >= max(activity.earliestStartTime, activity.getNewEarliestStartTime())) and  (
                S_i + D_i + T_ia + activity.duration + math.ceil(T_ij[activity.id][j.id]) <= j.startTime): 
                activity.startTime = S_i + D_i + math.ceil(T_ia)
                self.route.insert(index_count, activity)
                if activity.location != depot: 
                    self.locations.append(activity.location)
                    self.averageLocation = (sum(x[0] for x in self.locations) / len(self.locations), sum(x[1] for x in self.locations) / len(self.locations))
                self.lastIndexUpdate = index_count
                self.latestInsertStatus = True
                self.latestModificationWasRemove = False
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
            self.route.insert(index_count, activity)
            if activity.location != depot: 
                self.locations.append(activity.location)
                self.averageLocation = (sum(x[0] for x in self.locations) / len(self.locations), sum(x[1] for x in self.locations) / len(self.locations))
            self.lastIndexUpdate = index_count
            self.latestInsertStatus = True
            self.latestModificationWasRemove = False

            return True
   
        if (activity.possibleToInsert == True) and (
            min(activity.latestStartTime, activity.getNewLatestStartTime()) >= S_i + D_i + T_ia) and (
            S_i + D_i + T_ia >= max(activity.earliestStartTime, activity.getNewEarliestStartTime())) and (
            S_i + D_i + T_ia + activity.duration + math.ceil(T_ij[activity.id][0]) <= self.end_time): 
            activity.startTime = S_i + D_i + math.ceil(T_ia)
            self.route.insert(index_count, activity)
            if activity.location != depot: 
                self.locations.append(activity.location)
                self.averageLocation = (sum(x[0] for x in self.locations) / len(self.locations), sum(x[1] for x in self.locations) / len(self.locations))
            self.lastIndexUpdate = index_count
            self.latestInsertStatus = True
            self.latestModificationWasRemove = False
            return True

        self.lastIndexUpdate = index_count
        self.latestInsertStatus = False
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
        indexes = [i for i, act in enumerate(self.route) if act.id == activityID]
        # Check if the activity was found; since activity IDs should be unique, we only need to deal with the first match
        if indexes:
            index = indexes[0]

            activity_to_remove = self.route[index]
            
            activity_to_remove = self.route.pop(index)  # Use pop to directly remove by index
            
            # Reset the removed activity's properties
            activity_to_remove.employeeNotAllowedDueToPickUpDelivery = []
            activity_to_remove.startTime = None
            
            # Update dependencies for the removed activity
            #OBS: Denne er jeg ganske sikker på at vi må ha fordi det 
            self.updateActivityDependenciesInRoute(activity_to_remove)
        self.latestModificationWasRemove = True

    
    def insertActivityOnIndex(self, activity, index):

        if self.checkTrueFalse(activity) == False: 
            return False

        self.makeSpaceForIndex(index)
        #Beg: Må oppdatere verdiene innad basert på det som er flyttet 

        self.updateActivityBasedOnDependenciesInRoute(activity)
        #for possiblyMovedActivity in self.route: 
        #    self.updateActivityBasedOnDependenciesInRoute(possiblyMovedActivity)

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
            self.route.insert(index, activity)
            if activity.location != depot: 
                self.locations.append(activity.location)
                self.averageLocation = (sum(x[0] for x in self.locations) / len(self.locations), sum(x[1] for x in self.locations) / len(self.locations))
            self.lastIndexUpdate = index
            self.latestInsertStatus = True
            self.latestModificationWasRemove = False
            return True
        
        if min(activity.latestStartTime, activity.getNewLatestStartTime()) >= S_i + D_i + T_ia and (
            S_i + D_i + T_ia >= max(activity.earliestStartTime, activity.getNewEarliestStartTime())) and  (
            S_i + D_i + T_ia + activity.duration + math.ceil(T_ij[activity.id][j_id]) <= S_j): 
            activity.startTime = S_i + D_i + math.ceil(T_ia)
            self.route.insert(index, activity)
            if activity.location != depot: 
                self.locations.append(activity.location)
                self.averageLocation = (sum(x[0] for x in self.locations) / len(self.locations), sum(x[1] for x in self.locations) / len(self.locations))
            self.lastIndexUpdate = index
            self.latestInsertStatus = True
            self.latestModificationWasRemove = False

            return True
        
        self.lastIndexUpdate = index
        self.latestInsertStatus = False
        return False 
    
    #TODO: Litt usikker på hvrodan det blir her med innsettingen når vi er her 
    def insertToEmptyList(self, activity): 
        if self.start_time + T_ij[0][activity.id] <= max(activity.earliestStartTime, activity.getNewEarliestStartTime()) and (
            max(activity.earliestStartTime, activity.getNewEarliestStartTime()) + activity.duration + math.ceil(T_ij[activity.id][0]) <= self.end_time): 
            activity.startTime = max(activity.earliestStartTime, activity.getNewEarliestStartTime())
            self.route.insert(0, activity) 
            if activity.location != depot: 
                self.locations.append(activity.location)
                self.averageLocation = (sum(x[0] for x in self.locations) / len(self.locations), sum(x[1] for x in self.locations) / len(self.locations))
            self.lastIndexUpdate = 0
            self.latestInsertStatus = True
            self.latestModificationWasRemove = False

            return True
   
        if min(activity.latestStartTime, activity.getNewLatestStartTime()) >= self.start_time + T_ij[0][activity.id] and (
            self.start_time + T_ij[0][activity.id] >= max(activity.earliestStartTime, activity.getNewEarliestStartTime())) and  (
            self.start_time + T_ij[0][activity.id] + activity.duration + math.ceil(T_ij[activity.id][0]) <= self.end_time): 
            activity.startTime = self.start_time + math.ceil(T_ij[0][activity.id])
            self.route.insert(0, activity) 
            if activity.location != depot: 
                self.locations.append(activity.location)
                self.averageLocation = (sum(x[0] for x in self.locations) / len(self.locations), sum(x[1] for x in self.locations) / len(self.locations))
            self.lastIndexUpdate = 0
            self.latestInsertStatus = True
            self.latestModificationWasRemove = False

            return True
        self.lastIndexUpdate = 0
        self.latestInsertStatus = False
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
        for j in range(self.lastIndexUpdate, stopIndex): 
            act = self.route[j]

            new_startTime =  max(act.earliestStartTime, act.getNewEarliestStartTime(), S_i + D_i + math.ceil(T_ij[i_id][act.id]) )
            if new_startTime < act.startTime: 
                act.startTime = new_startTime
                
                #self.updateActivityDependenciesInRoute(act)
                
            i_id = act.id 
            S_i = act.startTime 
            D_i = act.duration

 

    '''
    Hva er logikken her? 
    '''
    def moveActivitiesLater(self, index): 
        j_id = 0
        S_j = self.end_time
       
        last_index_to_move = self.lastIndexUpdate -1
        if self.latestInsertStatus == True: 
            last_index_to_move = self.lastIndexUpdate
            
        for i in range(last_index_to_move, index -1 , -1): 
            act = self.route[i]
           
            
            new_startTime = min(act.latestStartTime, act.getNewLatestStartTime(), S_j - math.ceil(T_ij[act.id][j_id]) - act.duration )
            if new_startTime > act.startTime: 
                act.startTime = new_startTime

                #Beg: Når vi endrer et startdispunkt kan det ha effeke på de neste 
                #self.updateActivityDependenciesInRoute(act)
           
            j_id = act.id 
            S_j = act.startTime 
         
    
    def makeSpaceForIndex(self, index): 

        #Dersom vi legger til noe til høre for siste oppdatering 

        if len(self.route) == 0:
            return 
        
        for possiblyMovedActivity in self.route: 
            self.updateActivityBasedOnDependenciesInRoute(possiblyMovedActivity)

        if self.latestModificationWasRemove: 
            self.makeSpaceForIndexWhenRouteNotCharted(index)
            return 
        #Kan vi anta at dersom det ikke er noen 
        

        if index > self.lastIndexUpdate: 
            self.moveActivitiesEarlier(index)

        else: 
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
                activity.setNewEarliestStartTime(nextNodeAct.startTime- NextNodeInTimeID[1], NextNodeInTimeID[0])
                activity.setNewLatestStartTime(nextNodeAct.startTime - activity.duration, NextNodeInTimeID[0])
            

    def makeSpaceForIndexWhenRouteNotCharted(self, index): 

        #Dersom vi legger til noe til høre for siste oppdatering 

        #Kan vi anta at dersom det ikke er noen 
    

        self.moveAllActivitiesEarlier(index)
        self.moveAllActivitiesLater(index)


    def moveAllActivitiesEarlier(self, stopIndex): 
        i_id = 0
        S_i = self.start_time
        D_i = 0
        for j in range(0, stopIndex): 
            act = self.route[j]

            new_startTime =  max(act.earliestStartTime, act.getNewEarliestStartTime(), S_i + D_i + math.ceil(T_ij[i_id][act.id]) )
            if new_startTime < act.startTime: 
                act.startTime = new_startTime
                
                #self.updateActivityDependenciesInRoute(act)
                
            i_id = act.id 
            S_i = act.startTime 
            D_i = act.duration

 

    def moveAllActivitiesLater(self, index): 
        j_id = 0
        S_j = self.end_time
       
   
            
        for i in range(len(self.route) -1, index -1 , -1): 
            act = self.route[i]
            
            new_startTime = min(act.latestStartTime, act.getNewLatestStartTime(), S_j - math.ceil(T_ij[act.id][j_id]) - act.duration )
            if new_startTime > act.startTime: 
                act.startTime = new_startTime

                #Beg: Når vi endrer et startdispunkt kan det ha effeke på de neste 
                #self.updateActivityDependenciesInRoute(act)
           
            j_id = act.id 
            S_j = act.startTime 