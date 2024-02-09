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
        self.travel_time = 0
        self.start_time = employee.getShiftStart(day) 
        self.end_time = employee.getShiftEnd(day)
        self.route = np.empty(0, dtype=object)
        self.skillLev = employee.getSkillLevel()
        self.day = day
        self.employee = employee
        self.accumSuitability = 0 


    def addActivity(self, activity):
        '''
        Hva skal sjekkes når vi skal legge til aktiviteter 
        Må returnere true eller fals slik at man eventuelt kan bli sendt videre til en annen rute

        Presedens er ikke hensyntatt
        Same employee activity - Denne må altså være i samme rute som noen andre
        '''
        #Oppfyller employee restrictions 
        #Oppfyller skillevel 
        if activity.getEmployeeRestriction == self.employee.getID() or activity.getSkillreq() > self.skillLev: 
            return False

        #TODO. Må finne ut hvordan man skal iterere over de ulike. 
        #Kaller aktiviteten vi ser på nå for a, foregående aktivitet for i, kommenda aktiviet for j  
         
        S_i = self.start_time
        T_ia = T_ij[0][activity.id]
        #T_ia = 0 
        D_i = 0 
        index_count = 0 
        for j in self.route: 
            #hva sjekker denne: 
            if S_i + D_i + T_ia <= activity.getEarliestStartTime() and activity.getEarliestStartTime() + activity.getDuration() + T_ij[activity.getID()][j.getID()] <= j.getStartTime(): 
                activity.setStartTime(activity.getEarliestStartTime())
                self.route = np.insert(self.route, index_count, activity)
                if activity.id == 15: 
                    print("legger til aktivitet pga dette1")
                return True
            if S_i + D_i + T_ia >= activity.getEarliestStartTime() and  S_i + D_i + math.ceil(T_ia) + activity.getDuration() + T_ij[activity.getID()][j.getID()] <= j.getStartTime(): 
                activity.setStartTime(S_i + D_i + math.ceil(T_ia))
                self.route = np.insert(self.route, index_count, activity)
                if activity.id == 15: 
                    print("legger til aktivitet pga dette2")
                return True
            if S_i + D_i + T_ia <= j.getStartTime()- T_ij[activity.getID()][j.getID()] - activity.getDuration() and activity.getLatestStartTime() <= j.getStartTime() - T_ij[activity.getID()][j.getID()] - activity.getDuration():
                activity.setStartTime(activity.getLatestStartTime())
                self.route = np.insert(self.route, index_count, activity)
                if activity.id == 15: 
                    print("legger til aktivitet pga dette3")
                return True
            S_i = j.getStartTime()
            T_ia = T_ij[j.getID()][activity.getID()]
            D_i = j.getDuration()
            index_count +=1
       
        if S_i + D_i + T_ia <= activity.getEarliestStartTime() and activity.getEarliestStartTime() + activity.getDuration() + T_ij[activity.getID()][0] <= self.end_time: 
            activity.setStartTime(activity.getEarliestStartTime())
            self.route = np.insert(self.route, index_count, activity)
            return True
        if S_i + D_i + T_ia >= activity.getEarliestStartTime() and S_i + D_i + T_ia + activity.getDuration() + T_ij[activity.getID()][0] <= self.end_time: 
            activity.setStartTime(S_i + D_i + math.ceil(T_ia))
            self.route = np.insert(self.route, index_count, activity)
            return True
        if S_i + D_i + T_ia <= self.start_time - T_ij[activity.getID()][0] - activity.getDuration() and activity.getLatestStartTime() <= self.end_time - T_ij[activity.getID()][0] - activity.getDuration():
            activity.setStartTime(activity.getLatestStartTime())
            self.route = np.insert(self.route, index_count, activity)
            return True
        
        return False 

       
#TODO: Må fikse slik at ceil er på alle funskjonen 
        

    def getRoute(self): 
        return self.route

    def getDistance(self, activity1, activity2): 
        return 0 
        #Viktig å hente distansematrisen bare en gang, hvis det gjøres på denne måten, så vil den bli hentet flere ganger.
        #Det er ikke heldig. Vil gjøre et kall til API-et 
    
    def printSoultion(self): 
        print("Printer ny løsning for dag "+str(self.day)+ " ansatt "+str(self.employee.getID()))
        print(self.getRoute())
        for a in self.route: 
            print("activity "+str(a.getID())+ "start "+ str(a.getStartTime()))    
        print("---------------------")

#Du må rekke å begynne på aktiviteten før 

#TODO: Er aktivtet et objekt eller en
#TODO: Må finne ut hvordanman aksesserer duration og T_ij herfra 
#TODO: Legge til skillrequirement 

df_employees  = pd.read_csv("data/EmployeesNY.csv").set_index(["EmployeeID"]) 
df_activities  = pd.read_csv("data/NodesNY.csv").set_index(["id"]) 

e1 = Employee(df_employees, 1)
r1 = Route(1, e1)
print("ruten starter", r1.start_time)
print("ruten slutter ", r1.end_time)
print("original route", r1.getRoute())
a1 = Acitivity(df_activities, 1)
r1.addActivity(a1)
r1.printSoultion()
a25 = Acitivity(df_activities, 25)
r1.addActivity(a25)
r1.printSoultion()
a6 = Acitivity(df_activities, 6)
a7 = Acitivity(df_activities, 7)
a8 = Acitivity(df_activities, 8)
a9 = Acitivity(df_activities, 9)
a10 = Acitivity(df_activities, 10)
a11 = Acitivity(df_activities, 11)
a13 = Acitivity(df_activities, 13)
a14 = Acitivity(df_activities, 14)
a15 = Acitivity(df_activities, 15)
print("a15.getDuration()",a15.getDuration())
a16 = Acitivity(df_activities, 16)
a17 = Acitivity(df_activities, 17)


print("aktivitet6 "+str(r1.addActivity(a6)))
print("aktivitet7 "+str(r1.addActivity(a7)))
print("aktivitet8 "+str(r1.addActivity(a8)))
print("aktivitet9 "+str(r1.addActivity(a9)))
print("aktivitet10 "+str(r1.addActivity(a10)))
print("aktivitet11 "+str(r1.addActivity(a11)))
print("aktivitet13 "+str(r1.addActivity(a13)))
print("aktivitet14 "+str(r1.addActivity(a14)))
print("aktivitet15 "+str(r1.addActivity(a15)))
print("aktivitet16 "+str(r1.addActivity(a16)))
print("aktivitet17 "+str(r1.addActivity(a17)))
r1.printSoultion()



'''
Sjekke for å finne alle aktivter som kan på mandager 
Nå fungere den med at noen aktiviteter kan legges til og noen ikke. Så nå må vi ha samling av alle rutene




Kommentar til resultater. Det skal fungere å legge inn den andre.
Hvilken av de skal den fungere på

Det er noe med når tidsvinduene strekker seg utenfor begge begrensninger. Da fungerer det ikke
'''


'''
Uganspunkt for klassen: Dette er rute for en spessifikk ansatt, med starttidspunkt og slutttidspunkt. 
Det er allerde gitt 


Skal vi her anta at vi allerde har sjekket om noden skal settes inn? 
Hvor skal det sjekkes hvorvidt noe skal legges inn eller ikke? 

Problemer, det er mye problemer her. For det første kan det være veldig spessfikt hvor noden skal inn
Dersom det for eksempel skal til en spessifik 

'''
