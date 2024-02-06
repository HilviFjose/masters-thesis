import numpy as np
import pandas as pd
from employee import Employee
from actitivites import Acitivity

class Route:
    def __init__(self, day, employee):
        self.travel_time = 0
        self.start_time = employee.getShiftStart(day) 
        self.end_time = employee.getShiftEnd(day)
        self.route = np.array([])
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

        #TODO. Må finne ut hvordan man skal iterere over de ulike. Det er 
        S_i = self.start_time
        T_ij = T_ij[0][activity.id]
        D_i = 0 
        for k in self.route: 
            if S_i + D_i + T_ij + act.duation + T_ij[act][after_node[0]] <= after_node[1]:
            

        if len(self.route == 0): 
            if activity.latestStartTime >= self.start_time + 


        start = self.start_time
        for act in 

        return True




        '''
        for i in range(len(self.route)-1): 
            before_node = self.route[i]
            after_node = self.route[i+1]
            if before_node[1] + Duration[before_node[0]] + T_ij[before_node[0]][activity] + Duration[activity] + T_ij[activity][after_node[0]] <= after_node[1]:
                self.route = np.insert(self.route, i, (activity, Duration[activity]))
                return True
        return False 
        '''

    def getRoute(self): 
        return self.route

    def getDistance(self, activity1, activity2): 
        return 0 
        #Viktig å hente distansematrisen bare en gang, hvis det gjøres på denne måten, så vil den bli hentet flere ganger.
        #Det er ikke heldig. Vil gjøre et kall til API-et 

#Du må rekke å begynne på aktiviteten før 

#TODO: Er aktivtet et objekt eller en
#TODO: Må finne ut hvordanman aksesserer duration og T_ij herfra 
#TODO: Legge til skillrequirement 

df_employees  = pd.read_csv("data/EmployeesNY.csv").set_index(["EmployeeID"]) 
df_activities  = pd.read_csv("data/NodesNY.csv").set_index(["id"]) 

e1 = Employee(df_employees, 1)
r1 = Route(1, e1)
print("original route", r1.getRoute())
a1 = Acitivity(df_activities, 1)
print("r1.addActivity(a1)",r1.addActivity(a1))
print("new route", r1.getRoute())

'''
Uganspunkt for klassen: Dette er rute for en spessifikk ansatt, med starttidspunkt og slutttidspunkt. 
Det er allerde gitt 


Skal vi her anta at vi allerde har sjekket om noden skal settes inn? 
Hvor skal det sjekkes hvorvidt noe skal legges inn eller ikke? 

Problemer, det er mye problemer her. For det første kan det være veldig spessfikt hvor noden skal inn
Dersom det for eksempel skal til en spessifik 

'''
