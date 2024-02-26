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

        if  self.employee.getID() in activity.getEmployeeRestriction() or (
            self.employee.getID() in activity.employeeNotAllowedDueToPickUpDelivery) or (
                activity.getSkillreq() > self.skillLev) or (activity.possibleToInsert == False): 
            return False

        
        #Begynner med å sette i noden til å være depoet på starten av ruten, for å sjekke om vi kan starte med denne aktiviten
        S_i = self.start_time
        T_ia = math.ceil(T_ij[0][activity.id])
        D_i = 0 
        index_count = 0 
        i = None

        #Nå har vi satt i noden til å være depoet, også vil vi hoppe videre mellom aktivtene 
        for j in self.route: 
            
            if S_i + D_i + T_ia <= max(activity.getEarliestStartTime(), activity.newEeariestStartTime) and (
                max(activity.getEarliestStartTime(), activity.newEeariestStartTime) + activity.getDuration() + math.ceil(T_ij[activity.getID()][j.getID()]) <= j.getStartTime()):  
                activity.setStartTime(max(activity.getEarliestStartTime(), activity.newEeariestStartTime))
                self.route = np.insert(self.route, index_count, activity)
                return True
            
            #Dersom latest start time er større enn starttiden + varigheten + reiseveien fra i til a 
            if min(activity.getLatestStartTime(), activity.newLatestStartTime) >= S_i + D_i + T_ia and (
                #og starttiden + varigheten + reiseveien fra i til a  er større enn earliest starttime
                S_i + D_i + T_ia >= max(activity.getEarliestStartTime(), activity.newEeariestStartTime)) and  (
                #og aktivitetens starttid + aktivitetens varighet og reiseveien fra a til j er mindre enn starttidspunktet for j 
                S_i + D_i + T_ia + activity.getDuration() + math.ceil(T_ij[activity.getID()][j.getID()]) <= j.getStartTime()): 
                #Legger til aktiviteten på i ruten og oppdatere starttidspunktet til å startiden til i + varigheten til i + reiseveien fra i til a 
                activity.setStartTime(S_i + D_i + math.ceil(T_ia))
                self.route = np.insert(self.route, index_count, activity)
                '''
                self.aggSkillDiff +=  self.skillLev - activity.getSkillreq()
                if index_count == 0: 
                    self.travel_time -= T_ij[0][j.getID()]
                else: 
                    self.travel_time -= T_ij[i.getID()][j.getID()]
                self.travel_time += T_ia + T_ij[activity.getID()][j.getID()]
                '''
                return True
          
            #Så settes j noden til å være i noden for å kunne sjekke neste mellomrom i ruten
            S_i = j.getStartTime()
            T_ia = math.ceil(T_ij[j.getID()][activity.getID()])
            D_i = j.getDuration()
            i = copy.copy(j) 
            index_count +=1
       
        #Etter vi har iterert oss gjennom alle mollom rom mellom aktiviteter sjekker vi her om det er plass i slutten av ruta       
        #Det er samme logikk som i iterasjonen over, bare at vi her sjekker opp mot slutten av ruta
        if S_i + D_i + T_ia <= max(activity.getEarliestStartTime(), activity.newEeariestStartTime) and (
            max(activity.getEarliestStartTime(), activity.newEeariestStartTime)+ activity.getDuration() + math.ceil(T_ij[activity.getID()][0]) <= self.end_time): 
            activity.setStartTime(max(activity.getEarliestStartTime(), activity.newEeariestStartTime))
            self.route = np.insert(self.route, index_count, activity)
            '''
            self.aggSkillDiff +=  self.skillLev - activity.getSkillreq()
            if index_count != 0 : 
                self.travel_time -= math.ceil(T_ij[i.getID()][0])
            self.travel_time += T_ia + math.ceil(T_ij[activity.getID()][0])      
            '''     
            return True

        if min(activity.getLatestStartTime(), activity.newLatestStartTime) >= S_i + D_i + T_ia and (
            S_i + D_i + T_ia >= max(activity.getEarliestStartTime(), activity.newEeariestStartTime)) and (
            S_i + D_i + T_ia + activity.getDuration() + math.ceil(T_ij[activity.getID()][0]) <= self.end_time): 
            activity.setStartTime(S_i + D_i + math.ceil(T_ia))
            self.route = np.insert(self.route, index_count, activity)
            '''
            self.aggSkillDiff +=  self.skillLev - activity.getSkillreq()
            if index_count != 0 : 
                self.travel_time -= math.ceil(T_ij[i.getID()][0])
            self.travel_time += T_ia + math.ceil(T_ij[activity.getID()][0])
            '''
            return True

        #Returnerer false dersom det ikke var plass mellom noen aktiviteter i ruten 
        return False 

        
    def getEmployee(self):
        return self.employee

    def getRoute(self): 
        return self.route

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
        for act in self.route: 
            j = act.getID()
            travel_time += math.ceil(T_ij[i][j])
            i = j 
            aggregated_skilldiff += self.employee.getSkillLevel() - act.getSkillreq()
        travel_time += math.ceil(T_ij[i][0])
        self.aggSkillDiff= aggregated_skilldiff
        self.travel_time = travel_time
    
    def removeActivityID(self, activityID):
        index = 0 
        for act in self.route: 
            if act.getID() == activityID: 
                self.route = np.delete(self.route, index)
                return 
            index += 1 
        #print("Activity", activity.getID() , " not found in route employee", self.getEmployee().getID(), "on day", self.day)
        return
    
    def insertActivityOnIndex(self, activity_old, index):
        activity = copy.deepcopy(activity_old)

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

        if S_i + D_i + T_ia <= max(activity.getEarliestStartTime(), activity.newEeariestStartTime) and (
            max(activity.getEarliestStartTime(), activity.newEeariestStartTime) + activity.getDuration() + math.ceil(T_ij[activity.getID()][j_id]) <= S_j): 
            activity.setStartTime(max(activity.getEarliestStartTime(), activity.newEeariestStartTime))
            self.route = np.insert(self.route, index, activity)
            return True
        
        if min(activity.getLatestStartTime(), activity.newLatestStartTime) >= S_i + D_i + T_ia and (
            S_i + D_i + T_ia >= max(activity.getEarliestStartTime(), activity.newEeariestStartTime)) and  (
            S_i + D_i + T_ia + activity.getDuration() + math.ceil(T_ij[activity.getID()][j_id]) <= S_j): 
            activity.setStartTime(S_i + D_i + math.ceil(T_ia))
            self.route = np.insert(self.route, index, activity)
            return True
        return False 
    

    def insertToEmptyList(self, activity): 
        if self.start_time + T_ij[0][activity.id] <= max(activity.getEarliestStartTime(), activity.newEeariestStartTime) and (
            #og aktivitetens starttid + aktivitetens varighet og reiseveien fra a til j er mindre enn starttidspunktet for j 
            max(activity.getEarliestStartTime(), activity.newEeariestStartTime) + activity.getDuration() + math.ceil(T_ij[activity.getID()][0]) <= self.end_time): 
            #Legger til aktiviteten på i ruten og oppdatere starttidspunktet til å være earliest startime 
            activity.setStartTime(max(activity.getEarliestStartTime(), activity.newEeariestStartTime))
            self.route = np.insert(self.route, 0, activity)
            return True
        
        #Dersom latest start time er større enn starttiden + varigheten + reiseveien fra i til a 
        if min(activity.getLatestStartTime(), activity.newLatestStartTime) >= self.start_time + T_ij[0][activity.id] and (
            #og starttiden + varigheten + reiseveien fra i til a  er større enn earliest starttime
            self.start_time + T_ij[0][activity.id] >= max(activity.getEarliestStartTime(), activity.newEeariestStartTime)) and  (
            #og aktivitetens starttid + aktivitetens varighet og reiseveien fra a til j er mindre enn starttidspunktet for j 
            self.start_time + T_ij[0][activity.id] + activity.getDuration() + math.ceil(T_ij[activity.getID()][0]) <= self.end_time): 
            #Legger til aktiviteten på i ruten og oppdatere starttidspunktet til å startiden til i + varigheten til i + reiseveien fra i til a 
            activity.setStartTime(self.start_time + math.ceil(T_ij[0][activity.id]))
            self.route = np.insert(self.route, 0, activity)
            return True
        return False 
    
    def getActivity(self, actID): 
        '''
        returnerer employee ID-en til den ansatte som er allokert til en aktivitet 
        
        Arg: 
        actID (int): ID til en aktivitet som gjøres en gitt dag
        day (int): dagen aktiviten finnes i en rute  

        Return: 
        activity (Activity) Activity objektet som finnes i en rute på en gitt dag
        '''
        for act in self.route: 
            if act.getID() == actID: 
                return act        

