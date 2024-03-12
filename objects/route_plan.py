import pandas as pd
import numpy as np
import os
import sys
sys.path.append( os.path.join(os.path.split(__file__)[0],'..') )  # Include subfolders
from objects.employee import Employee
from objects.route import Route
import copy
import random 


'''
Info: 
Dette er selve løsningen som inneholder routes. 
'''
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

        #self.rev = True #Dersom vi ønsker å reversere listene (Sorterer heller listene annerledes nå)
'''
class RoutePlan:
    def __init__(self, days, employee_df):
        self.employee_df = employee_df
        self.routes = {day: [] for day in range(1, days+1)}
        employee_skills = {} # For å holde styr på ansattes ferdigheter

        for key, value in employee_df.iterrows():
            emp = Employee(employee_df, key)
            employee_skills[key] = value['professionalLevel'] 

            for day in self.routes:
                self.routes[day].append((emp.skillLevel, Route(day, emp))) # Lagrer professionalLevel sammen med Route

        # Sorter routes basert på skill for hver dag
        for day in self.routes:
            self.routes[day] = [route for _, route in sorted(self.routes[day], key=lambda x: x[0])]

        self.days = days 
        self.objective = [0,0,0,0,0]
        self.weeklyHeaviness = 0
        self.dailyHeaviness = 0


    def addActivityOnDay(self, activity, day):
        #TODO: Her er det mulig å velge hvilken metode som er ønskelig å kjøre med. De gir ganske ulike resultater. 
        # De metodene som bruker random-biblioteket vil gi nye løsninger for hver kjøring (med samme datasett).
        ''' FORKLARING
        Funksjonen legger til aktiviteten på den gitte dagen ved å iterere over alle rutene som finnes på dagen 

        Arg: 
        activity (Activity): Activity objekt som vil legges til i en rute 
        day (int): Dagen aktiviten skal legges til på 

        Return: 
        True/False på om innsettingen av aktiviteten var velykket 
        '''

        ''' #GAMMEL METODE - Reverserer rekkefølgen på routes for å ikke alltid begynne med samme ansatt på den gitte dagen
        if self.rev == True:
            routes =  reversed(self.routes[day])
            self.rev = False
        else: 
            routes = self.routes[day]
            self.rev = True
        '''
        '''
         #GAMMEL METODE - Itererer helt tilfeldig
        routes = self.routes[day]
        index_random = [i for i in range(len(routes))]
        random.shuffle(index_random)

        for index in index_random: #Disse to linjene erstattes med første linje i for-løkken nedenfor
            route = routes[index]
            old_skillDiffObj = route.aggSkillDiff
            old_travel_time = route.travel_time

            #TODO: Update funskjonene burde sjekkes med de andre   
            #TODO: Hvorfor er det bare denne ene som skal oppdateres i forhold til de andre? Er det fordi de  i ruten allerede er oppdatert
            #Ettersom vi ikke kjører på de andre, så antar vi at de resterende aktivitetene har riktig oppdaterte grenserf fra andre ruter       
            #Beg: Ettersom aktivteten ikke finnes i ruten, har den ikke oppdatert grensene mot andr aktiviteter  
            
            #Denne trenger vi nok ikke. Ford disse blir nok oppdatert av funksjonen under.
            
            self.updateActivityBasedOnRoutePlanOnDay(activity, day)
         
            insertStatus = route.addActivity(activity)
            
            if insertStatus == True: 
                #Beg: Alle aktivteter kan ha blitt flyttet på i ruten og må derfor oppdatere grensene på tvers 
                #Må gjøres på alle fordi alle kan ha blitt flyttet
                for possiblyMovedActivity in route.route: 
                    self.updateDependentActivitiesBasedOnRoutePlanOnDay(possiblyMovedActivity, day)
            
                self.objective[3] -= old_skillDiffObj
                self.objective[3] += route.aggSkillDiff
                self.objective[4] -= old_travel_time
                self.objective[4] += route.travel_time
                return True
        return False
        '''
        # Grupperer ruter basert på profesjonen til den ansatte
        routes_grouped_by_skill = {}
        for route in self.routes[day]:
            skill_level = route.skillLev 
            if skill_level not in routes_grouped_by_skill:
                routes_grouped_by_skill[skill_level] = [route]
            else:
                routes_grouped_by_skill[skill_level].append(route)
        
        # Iterer gjennom sorterte professionLevels og iterer i tilfeldig rekkefølge
        for skill_level in sorted(routes_grouped_by_skill):
            routes = routes_grouped_by_skill[skill_level]
            random.shuffle(routes)  
            
            #Prøver iterativt å legge til aktiviteten i hver rute på den gitte dagen 
            for route in routes:
                old_skillDiffObj = route.aggSkillDiff
                old_travel_time = route.travel_time
                #TODO: Update funskjonene burde sjekkes med de andre   
                #TODO: Hvorfor er det bare denne ene som skal oppdateres i forhold til de andre? Er det fordi de  i ruten allerede er oppdatert
                #Ettersom vi ikke kjører på de andre, så antar vi at de resterende aktivitetene har riktig oppdaterte grenserf fra andre ruter       
                #Beg: Ettersom aktivteten ikke finnes i ruten, har den ikke oppdatert grensene mot andr aktiviteter  
                
                #Denne trenger vi nok ikke. Ford disse blir nok oppdatert av funksjonen under.
                
                self.updateActivityBasedOnRoutePlanOnDay(activity, day)
                insertStatus = route.addActivity(activity)
                #Beg: Alle aktivteter kan ha blitt flyttet på i ruten og må derfor oppdatere grensene på tvers 
                #Må gjøres på alle fordi alle kan ha blitt flyttet
                for possiblyMovedActivity in route.route: 
                    self.updateDependentActivitiesBasedOnRoutePlanOnDay(possiblyMovedActivity, day)
            
                if insertStatus:
                    self.objective[3] -= old_skillDiffObj
                    self.objective[3] += route.aggSkillDiff
                    self.objective[4] -= old_travel_time
                    self.objective[4] += route.travel_time
                    return True
        return False
        '''
        #GAMMEL METODE - Itererer etter sortert skill
        # Iterer gjennom routes i den sorterte rekkefølgen basert på skill
        for route in self.routes[day]:
            old_skillDiffObj = route.aggSkillDiff
            old_travel_time = route.travel_time

            #TODO: Update funskjonene burde sjekkes med de andre   
            #TODO: Hvorfor er det bare denne ene som skal oppdateres i forhold til de andre? Er det fordi de  i ruten allerede er oppdatert
            #Ettersom vi ikke kjører på de andre, så antar vi at de resterende aktivitetene har riktig oppdaterte grenserf fra andre ruter       
            #Beg: Ettersom aktivteten ikke finnes i ruten, har den ikke oppdatert grensene mot andr aktiviteter  
            
            #Denne trenger vi nok ikke. Ford disse blir nok oppdatert av funksjonen under.
            
            self.updateActivityBasedOnRoutePlanOnDay(activity, day)
         
            insertStatus = route.addActivity(activity)
            
            if insertStatus == True: 
                #Beg: Alle aktivteter kan ha blitt flyttet på i ruten og må derfor oppdatere grensene på tvers 
                #Må gjøres på alle fordi alle kan ha blitt flyttet
                for possiblyMovedActivity in route.route: 
                    self.updateDependentActivitiesBasedOnRoutePlanOnDay(possiblyMovedActivity, day)
            
                self.objective[3] -= old_skillDiffObj
                self.objective[3] += route.aggSkillDiff
                self.objective[4] -= old_travel_time
                self.objective[4] += route.travel_time
                return True
        return False
        '''

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
        self.updateObjective()
        print("objective ", self.objective)
        print("allocated patients ", self.)

    def getEmployeeIDAllocatedForActivity(self, activity, day): 
        '''
        returnerer employee ID-en til den ansatte som er allokert til en aktivitet 
        
        Arg: 
        activity (Activity): Activity objekt som finnes i en rute på en gitt dag
        day (int): dagen aktiviten finnes i en rute  

        Return: 
        Int employeeID til den ansatte som er allokert til aktiviteten 
        
        '''
        for route in self.routes[day]: 
            for act in route.route: 
                if act.id== activity.id: 
                    return route.employee.id
    
    #TODO: Denne fungerer ikke nå. Må endre på den sånn at den funker!!
    def getListOtherEmplIDsOnDay(self, activityID, day):  
        #TODO: Ggjøre raskere 
        '''
        Oppdatert: Sender inn aktivitetsID til den aktiviteten som må gjøres på samme dag. 
        Det er en aktivitet, men vi vet ikke om den ligger i lista. 

        returnerer en liste employee ID-en til de andr ansatte som jobber på den gitte dagen
        
        Arg: 
        empl (int): EmployeeID som jobber på en gitt dag
        day (int): dagen den ansatte jobber på 

        Return: 
        List (Int) employeeID til de ansatte som ikke er empl 
        
        '''
        empForAct = None
        activityIDinRoute = False
        otherEmpl = []
        for route in self.routes[day]: 
            for act in route.route: 
                if act.id == activityID: 
                    activityIDinRoute = True
                    empForAct = route.employee.id
        if not activityIDinRoute: 
            return otherEmpl
        for route in self.routes[day]: 
            if route.employee.id != empForAct: 
                otherEmpl.append(route.employee.id)
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
            for act in route.route: 
                if act.id == actID: 
                    return act 
        return None       


    def updateObjective(self): 
        objective = [self.objective[0], 0, 0, 0, 0]
        self.calculateWeeklyHeaviness()
        self.calculateDailyHeaviness()
        objective[1] = self.weeklyHeaviness
        objective[2] = self.dailyHeaviness
        for day in range(1, 1+self.days): 
            for route in self.routes[day]: 
                route.updateObjective()
                objective[3] += route.aggSkillDiff 
                objective[4] += route.travel_time
        self.objective = objective
        
    def calculateWeeklyHeaviness(self):
        employee_weekly_heaviness = {}

        for day, routes in self.routes.items():
            for route in routes:
                employee_id = route.employee.id
                profession = route.skillLev  
                if profession not in employee_weekly_heaviness:
                    employee_weekly_heaviness[profession] = {}
                if employee_id not in employee_weekly_heaviness[profession]:
                    employee_weekly_heaviness[profession][employee_id] = []
                # Legger til route's "heaviness" for den ansatte
                employee_weekly_heaviness[profession][employee_id].append(route.calculateTotalHeaviness())

        # Gjennomsnittlig "heaviness" for hver ansatt og finner deretter max-min innen hver yrkesgruppe
        weekly_diffs = []
        for profession, employees in employee_weekly_heaviness.items():
            avg_heaviness_per_employee = [np.mean(heaviness) for heaviness in employees.values()]
            if avg_heaviness_per_employee: 
                weekly_diffs.append(max(avg_heaviness_per_employee) - min(avg_heaviness_per_employee))

        self.weeklyHeaviness = sum(weekly_diffs)


    def calculateDailyHeaviness(self):
        daily_diffs = []
        for day, routes in self.routes.items():    
            profession_groups = {}
            for route in routes:
                profession = route.skillLev
                if profession not in profession_groups:
                    profession_groups[profession] = []
                profession_groups[profession].append(route.calculateTotalHeaviness())

            for profession, heaviness in profession_groups.items():
                daily_diffs.append(max(heaviness) - min(heaviness))
        self.dailyHeaviness = sum(daily_diffs)


    def removeActivityFromEmployeeOnDay(self, employee, activity, day):
         #TODO: Finne ut når attributter skal restartes. Det fungerer ikke slik det er nå. 
        #Oppdateringen må kjøres etter de er restartet, slik at de tilhørende aktivitetne får beskjed
        for route in self.routes[day]: 
            if route.employee.id == employee:
                route.removeActivityID(activity.id)
                #Beg: Må oppdater de på andre dager slik at de ikke er like bundet av aktivitetens tidsvinduer
                self.updateDependentActivitiesBasedOnRoutePlanOnDay(activity, day)
              
    def insertActivityInEmployeesRoute(self, employeeID, activity, day): 
        #Må dyp kopiere aktiviten slik at ikke aktiviteten i den orginale rotueplanen restartes
        insert_activity = copy.deepcopy(activity)
         
        for route in self.routes[day]: 
            if route.employee.id == employeeID:
                #Beg: Må oppdatere grensene til alle i ruten som muligens kan flytte seg når vi prøver å legge til aktivtete
              
                self.updateActivityBasedOnRoutePlanOnDay(insert_activity, day)
             
                status = route.addActivity(insert_activity)
                if status == True: 
                    for routeActivity in route.route: 
                        self.updateActivityBasedOnRoutePlanOnDay(routeActivity, day)
                return status
        
    def getObjective(self): 
        return self.objective
    
    def swithRoute(self, route, day): 
        #Det er viktig at route objektet ikke er det samme som org_route
        for org_route in self.routes[day]: 
            if org_route.employee.id == route.employee.id: 
                self.routes[day].remove(org_route)
                self.routes[day].append(route)

    def updateActivityBasedOnRoutePlanOnDay(self, activity,day):
            '''
            Denne funksjonen skal håndtere oppdatering av de variable attributttene til activity
            Basert på det som allerede ligger inne i routeplanen 
            '''    

            #Her håndteres pick up and delivery
            if activity.getPickUpActivityID() != 0 : 
                otherEmplOnDay = self.getListOtherEmplIDsOnDay(activity.getPickUpActivityID(), day)
                activity.setemployeeNotAllowedDueToPickUpDelivery(otherEmplOnDay)
                
            #Her håndteres presedens.   
            #Aktivitetns earliests starttidspunkt oppdateres basert på starttidspunktet til presedens aktiviten
            for prevNodeID in activity.PrevNode: 
                prevNodeAct = self.getActivity(prevNodeID, day)
                if prevNodeAct != None:
                    activity.setNewEarliestStartTime(prevNodeAct.getStartTime() + prevNodeAct.getDuration(), prevNodeID)
  
            for nextNodeID in activity.NextNode: 
                nextNodeAct = self.getActivity(nextNodeID, day)
                if nextNodeAct != None:
                    activity.setNewLatestStartTime(nextNodeAct.getStartTime() - activity.getDuration(), nextNodeID)
            
            #Her håndteres presedens med tidsvindu
            #aktivitetens latest start time oppdateres til å være seneste starttidspunktet til presedensnoden
            for PrevNodeInTimeID in activity.PrevNodeInTime: 
                prevNodeAct = self.getActivity(PrevNodeInTimeID[0], day)
                if prevNodeAct != None:
                    activity.setNewLatestStartTime(prevNodeAct.getStartTime()+ prevNodeAct.duration + PrevNodeInTimeID[1], PrevNodeInTimeID[0])


            for NextNodeInTimeID in activity.NextNodeInTime: 
                nextNodeAct = self.getActivity(NextNodeInTimeID[0], day)
                if nextNodeAct != None:
                    activity.setNewEarliestStartTime(nextNodeAct.getStartTime() - NextNodeInTimeID[1], NextNodeInTimeID[0])
        
    def updateDependentActivitiesBasedOnRoutePlanOnDay(self, activity ,day):
        for depActID in activity.dependentActivities: 
            depActivity = self.getActivity(depActID, day)
            if depActivity != None: 
                self.updateActivityBasedOnRoutePlanOnDay(depActivity, day)

    def switchRoute(self, new_route,  day):
            for org_route in self.routes[day]: 
                if org_route.employee.id == new_route.employee.id: 
                    self.routes[day].remove(org_route)
                    self.routes[day].append(new_route) 
            
        