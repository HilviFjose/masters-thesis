import numpy as np
import pandas as pd
import sys
sys.path.append("C:\\Users\\agnesost\\masters-thesis")
from objects.employee import Employee
from objects.actitivites import Acitivity
from objects.distances import T_ij
import math

class Route:
    def __init__(self, day, employee):
        self.employee = employee
        self.start_time = employee.getShiftStart(day) 
        self.end_time = employee.getShiftEnd(day)
        self.route = np.empty(0, dtype=object)
        self.skillLev = employee.getSkillLevel()
        self.day = day
        


    def addActivity(self, activity):
        '''
        Funkjsonenen sjekker først om aktivitetnen oppfyller krav for å være i ruten
        Funkjsonen itererer vi over alle mellomrom mellom aktivitene som ligger i ruten. 
        Ugangspunktet er altså at ruten går fra i til j, og det skal byttes ut med å gå fra i til a og a til j 

        Arg: 
        activity (Activity) aktivitetsobjektet som skal legges til i ruten 

        Return: 
        True/False på om aktiviteten er blitt lagt til i ruten 
        '''
        #Sjekker om ruten oppfyller aktivitetens krav til employee restriction og skillevel 
        if  (self.employee.getID() in activity.getEmployeeRestriction() 
             or activity.getSkillreq() > self.skillLev): 
            return False

        
        #Begynner med å sette i noden til å være depoet på starten av ruten, for å sjekke om vi kan starte med denne aktiviten
        S_i = self.start_time
        T_ia = math.ceil(T_ij[0][activity.id])
        D_i = 0 
        index_count = 0 

        #Nå har vi satt i noden til å være depoet, også vil vi hoppe videre mellom aktivtene 
        for j in self.route: 
            
            #Dersom starttiden + varigheten + reiseveien fra i til a er mindre enn aktivitetens tidligste startid 
            if S_i + D_i + T_ia <= activity.getEarliestStartTime() and (
                #og aktivitetens starttid + aktivitetens varighet og reiseveien fra a til j er mindre enn starttidspunktet for j 
                activity.getEarliestStartTime() + activity.getDuration() + math.ceil(T_ij[activity.getID()][j.getID()]) <= j.getStartTime()): 
                #Legger til aktiviteten på i ruten og oppdatere starttidspunktet til å være earliest startime 
                activity.setStartTime(activity.getEarliestStartTime())
                self.route = np.insert(self.route, index_count, activity)
                return True
            
            #Dersom latest start time er større enn starttiden + varigheten + reiseveien fra i til a 
            if activity.getLatestStartTime() >= S_i + D_i + T_ia and (
                #og starttiden + varigheten + reiseveien fra i til a  er større enn earliest starttime
                S_i + D_i + T_ia >= activity.getEarliestStartTime()) and  (
                #og aktivitetens starttid + aktivitetens varighet og reiseveien fra a til j er mindre enn starttidspunktet for j 
                S_i + D_i + T_ia + activity.getDuration() + math.ceil(T_ij[activity.getID()][j.getID()]) <= j.getStartTime()): 
                #Legger til aktiviteten på i ruten og oppdatere starttidspunktet til å startiden til i + varigheten til i + reiseveien fra i til a 
                activity.setStartTime(S_i + D_i + math.ceil(T_ia))
                self.route = np.insert(self.route, index_count, activity)
                return True
          
            #Så settes j noden til å være i noden for å kunne sjekke neste mellomrom i ruten
            S_i = j.getStartTime()
            T_ia = math.ceil(T_ij[j.getID()][activity.getID()])
            D_i = j.getDuration()
            index_count +=1
       
        #Etter vi har iterert oss gjennom alle mollom rom mellom aktiviteter sjekker vi her om det er plass i slutten av ruta       
        #Det er samme logikk som i iterasjonen over, bare at vi her sjekker opp mot slutten av ruta
        if S_i + D_i + T_ia <= activity.getEarliestStartTime() and (
            activity.getEarliestStartTime() + activity.getDuration() + math.ceil(T_ij[activity.getID()][0]) <= self.end_time): 
            activity.setStartTime(activity.getEarliestStartTime())
            self.route = np.insert(self.route, index_count, activity)
            return True

        if activity.getLatestStartTime() >= S_i + D_i + T_ia and (
            S_i + D_i + T_ia >= activity.getEarliestStartTime()) and (
            S_i + D_i + T_ia + activity.getDuration() + math.ceil(T_ij[activity.getID()][0]) <= self.end_time): 
            activity.setStartTime(S_i + D_i + math.ceil(T_ia))
            self.route = np.insert(self.route, index_count, activity)
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

