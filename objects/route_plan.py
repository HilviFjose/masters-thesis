import pandas as pd
import numpy as np

import sys
sys.path.append("C:\\Users\\agnesost\\masters-thesis")
from objects.employee import Employee
from objects.route import Route


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

        #TODO: Revurdere om vi skal reversere listene som iterers over eller gjøre random 
        self.rev = True

            
         
    #TODO: Vi vil legge til aktivitet på denne dagen. Sjekke om totalt sett går
    def addNodeOnDay(self, activity, day):

        if self.rev == True:
            routes =  reversed(self.routes[day])
            self.rev = False
        else: 
            routes = self.routes[day]
            self.rev = True


        for route in routes: 
            insertStatus = route.addActivity(activity)
            if insertStatus == True: 
                return True
        return False
    
    #Informasjon om den ansatte ligger i ruta. 

    
    def getRoutePlan(self): 
        return self.routes
 
    def printSoultion(self): 
        print("Printer alle rutene")
        for day in range(1, self.days +1): 
            for route in self.routes[day]: 
                route.printSoultion()

#Presedensen vil altid gjelde aktivitere for samme dag, så vi sender inn dag også
    def getEmployeeAllocatedForActivity(self, activity, day): 
        for route in self.routes[day]: 
            for act in route.getRoute(): 
                if act.getID() == activity: 
                    return route.getEmployee().getID()
    
    def getOtherEmplOnDay(self, empl, day): 
        otherEmpl = []
        for route in self.routes[day]: 
            if route.getEmployee().getID() != empl: 
                otherEmpl.append(route.getEmployee().getID())
        return otherEmpl

    def getActivity(self, prevNode, day): 
        for route in self.routes[day]: 
            for act in route.getRoute(): 
                if act.getID() == prevNode: 
                    return act        

    def checkAcitivyInRoutePlan(self, node, day):
        for route in self.routes[day]: 
            for act in route.getRoute(): 
                if act.getID() == node: 
                    return True
        return False        
       
