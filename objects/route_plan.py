import pandas as pd
import numpy as np
import os
import sys
sys.path.append( os.path.join(os.path.split(__file__)[0],'..') )  # Include subfolders
from objects.employee import Employee
from objects.route import Route
import copy


'''
Info: 
Dette er selve løsningen som inneholder routes. 
'''
class RoutePlan:
    def __init__(self, days, employee_df):
        self.routes = {day: [] for day in range(1, days+1)}
        for  key, value in employee_df.iterrows():
            emp = Employee(employee_df, key)
            for day in self.routes: 
                self.routes[day].append(Route(day, emp))
        self.days = days 
        self.objective = [0,0,0,0,0]
        self.objective1 = [0,0,0,0,0]

        #TODO: Revurdere om vi skal reversere listene som iterers over eller gjøre random 
        self.rev = True


    '''
    Når skal de oppdateres 
    '''

                
    
    def addNodeOnDay(self, activity, day):
        '''
        Funksjonen legger til aktiviteten på den gitte dagen ved å iterere over alle rutene som finnes på dagen 

        Arg: 
        activity (Activity): Activity objekt som vil legges til i en rute 
        day (int): Dagen aktiviten skal legges til på 

        Return: 
        True/False på om innsettingen av aktiviteten var velykket 
        '''
        #Reverserer rekkefølgen på routes for å ikke alltid begynne med samme ansatt på den gitte dagen
        if self.rev == True:
            routes =  reversed(self.routes[day])
            self.rev = False
        else: 
            routes = self.routes[day]
            self.rev = True

        #Prøver iterativt å legge til aktiviteten i hver rute på den gitte dagen 
        for route in routes: 
            old_skillDiffObj = route.aggSkillDiff
            old_travel_time = route.travel_time
            insertStatus = route.addActivity(activity)
            if insertStatus == True: 
                self.objective[3] -= old_skillDiffObj
                self.objective[3] += route.aggSkillDiff
                self.objective[4] -= old_travel_time
                self.objective[4] += route.travel_time
                return True
        return False
    
    def getRoutePlan(self): 
        return self.routes
 
    def printSolution(self): 
        '''
        Printer alle rutene som inngår i routeplan
        '''
        print("Printer alle rutene")
        for day in range(1, self.days +1): 
            for route in self.routes[day]: 
                route.printSoultion()

    def getEmployeeAllocatedForActivity(self, activity, day): 
        '''
        returnerer employee ID-en til den ansatte som er allokert til en aktivitet 
        
        Arg: 
        activity (Activity): Activity objekt som finnes i en rute på en gitt dag
        day (int): dagen aktiviten finnes i en rute  

        Return: 
        Int employeeID til den ansatte som er allokert til aktiviteten 
        
        '''
        for route in self.routes[day]: 
            for act in route.getRoute(): 
                if act.getID() == activity: 
                    return route.getEmployee().getID()
    
    def getOtherEmplOnDay(self, empl, day): 
        '''
        returnerer en liste employee ID-en til de andr ansatte som jobber på den gitte dagen
        
        Arg: 
        empl (int): EmployeeID som jobber på en gitt dag
        day (int): dagen den ansatte jobber på 

        Return: 
        List (Int) employeeID til de ansatte som ikke er empl 
        
        '''
        otherEmpl = []
        for route in self.routes[day]: 
            if route.getEmployee().getID() != empl: 
                otherEmpl.append(route.getEmployee().getID())
        return otherEmpl

    def getActivity(self, actID, day): 
        '''
        returnerer employee ID-en til den ansatte som er allokert til en aktivitet 
        
        Arg: 
        actID (int): ID til en aktivitet som gjøres en gitt dag
        day (int): dagen aktiviten finnes i en rute  

        Return: 
        activity (Activity) Activity objektet som finnes i en rute på en gitt dag
        '''
        for route in self.routes[day]: 
            for act in route.getRoute(): 
                if act.getID() == actID: 
                    return act        


    def updateObjective(self): 
        objective = [self.objective[0], 0, 0, 0, 0]
        for day in range(1, 1+self.days): 
            for route in self.routes[day]: 
                obj_34_tupl = route.updateObjective()
                objective[3] += obj_34_tupl[0]
                objective[4] += obj_34_tupl[1]
        self.objective = objective

    def removeActivityFromEmployeeOnDay(self, employee, activity, day):
        for route in self.routes[day]: 
            if route.employee.getID() == employee:
                route.removeActivity(activity.getID())


    def insertActivityInEmployeesRoute(self, employee, activity, day): 
        #Må dyp kopiere aktiviten slik at ikke aktiviteten i den orginale rotueplanen restartes
        insert_activity = copy.deepcopy(activity)
        insert_activity.restartActivity()
        
        for route in self.routes[day]: 
            if route.employee.getID() == employee:
                return route.addActivity(activity)
       
        
    def getObjective(self): 
        return self.objective
    
    def swithRoute(self, route, day): 
        #Det er viktig at route objektet ikke er det samme som org_route
        for org_route in self.routes[day]: 
            if org_route.employee.id == route.employee.id: 
                self.routes[day].remove(org_route)
                self.routes[day].append(route)