import pandas as pd
import numpy as np

import sys
sys.path.append("C:\\Users\\agnesost\\masters-thesis")
from objects.employee import Employee
from objects.route import Route

class RoutePlan:
    def __init__(self, days, employee_df):
        self.routes = {day: [] for day in range(1, days+1)}
        for  key, value in employee_df.iterrows():
            emp = Employee(employee_df, key)
            for day in self.routes: 
                self.routes[day].append(Route(day, emp))
        self.suitScore = 0 
        self.days = days 

            
    #def addActivity(self, activity): 


    #days er her entall dager, mens employees er en liste over    
    #Jeg tror vi skal ha rutene mer, med tilhørende score for alle rutene her. 
    #Hvis en rute legges til så økes scoren her     

    #De ansatte har   
    #Her blir det på hva vi skal sende inn. Sender inn hele employee dataframen kanskje? 

    '''
    Ansatt objektene lages bare en gang 
    '''
         
    #TODO: Vi vil legge til aktivitet på denne dagen. Sjekke om totalt sett går
    def addNodeOnDay(self, activity, day): 
        for route in self.routes[day]: 
            state = route.addActivity(activity)
            if state == True: 
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




df_employees = pd.read_csv("data/EmployeesNY.csv").set_index(["EmployeeID"])
rp = RoutePlan(5, employee_df= df_employees)
print(rp.getRoutePlan())


'''

Jobber alle ansatte alle dager? 
Nei det gjør de ikke. Så det må bli konstuert av 
I konstuktøren så lages alle parameterne

Skal denne oppdateres jevnlig, eller skal det konstureres nye underveid. 

Den må nesten være indeksert med alle ansatte alle dager. 
Det er ikke en effektiv måte å gjøre det på dersom de har veldig ulike arbeidstimer. 


Alt 1) Dictionary hvor de indekseres med ulike dager og ansatte 
Alt 2) To dimesjonal liste med ruteobjektet. Da må vi ha for alle kombinasjoner 
'''