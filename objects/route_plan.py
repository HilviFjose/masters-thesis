import pandas as pd
import numpy as np
import os
import sys
sys.path.append( os.path.join(os.path.split(__file__)[0],'..') )  # Include subfolders
from objects.employee import Employee
from objects.route import Route
import copy
import random 
import datetime


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

        self.treatments = {}
        self.visits = {}
        self.allocatedPatients = {}
        self.notAllocatedPatients = []
        self.illegalNotAllocatedPatients = []
        self.illegalNotAllocatedTreatments = []
        self.illegalNotAllocatedVisitsWithPossibleDays = {}
        self.illegalNotAllocatedActivitiesWithPossibleDays = {}


    def addActivityOnDay(self, activity, day):
        #TODO: Her er det mulig å velge hvilken metode som er ønskelig å kjøre med. De gir ganske ulike resultater. 
        # De metodene som bruker random-biblioteket vil gi nye løsninger for hver kjøring (med samme datasett).
        # Grupperer ruter basert på profesjonen til den ansatte
        routes_grouped_by_skill = {}
        for route in self.routes[day]:
            skill_level = route.skillLev 
            if skill_level not in routes_grouped_by_skill:
                routes_grouped_by_skill[skill_level] = [route]
            else:
                routes_grouped_by_skill[skill_level].append(route)
      
        # Iterer gjennom sorterte professionLevels og iterer i tilfeldig rekkefølge
        act_skill_level = activity.skillReq
        routes = []
        for act_skill_level in range (act_skill_level, 4): 
            routes_for_skill = routes_grouped_by_skill[act_skill_level]
            #random.shuffle(routes_for_skill)
            routes += routes_for_skill
            #if act_skill_level == 2: 
            #    random.shuffle(routes)
  

    
     
        #Prøver iterativt å legge til aktiviteten i hver rute på den gitte dagen 
        for route in routes:
            #print("forsøker legge til ", activity.id , "DAY ", route.day, "EMP ", route.employee.id)
        
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
                return True
        return False


    def remove_activityIDs_from_route_plan(self, activityIDs):
        for day in range(1, self.days +1): 
            for route in self.routes[day]: 
                for act in route.route: 
                    if act.id in activityIDs:
                        route.removeActivityID(act.id)

    def remove_activityIDs_return_day(self, removed_activityIDs):
        original_day = None
        for day in range(1, self.days +1): 
            for route in self.routes[day]: 
                for act in route.route: 
                    if act.id in removed_activityIDs:
                        route.removeActivityID(act.id)
                        original_day = day
        return original_day

    def getRoutePlan(self): 
        return self.routes
    
    def printDictionaryTest(self, txtName):
        #SKRIV TIL FIL I STEDET FOR TERMINAL
        # Åpne filen for å skrive
        with open(r"results\\" + txtName + ".txt", "w") as log_file:
            # Omdiriger sys.stdout til filen
            original_stdout = sys.stdout
            sys.stdout = log_file
            constructor = None 

            # Skriver klokkeslettet til når filen ble opprettet
            now = datetime.datetime.now() 
            log_file.write('Solution generated at time: {}\n\n'.format(now.strftime("%Y-%m-%d %H:%M:%S")))
            print('-------------------------------------------------------')
            print("visits", self.visits)
            print("treatments", self.treatments)
            print("allocated patients ", self.allocatedPatients)
            print("not allocated ", self.notAllocatedPatients)
            print("illegalNotAllocatedTreatments", self.illegalNotAllocatedTreatments)
            print("illegalNotAllocatedVisits", self.illegalNotAllocatedVisitsWithPossibleDays)
            print("illegalNotAllocatedActivities", self.illegalNotAllocatedActivitiesWithPossibleDays)

             # Tilbakestill sys.stdout til original
            sys.stdout = original_stdout
 
    def printSolution(self, txtName, operator_string):
        #SKRIV TIL FIL I STEDET FOR TERMINAL
        # Åpne filen for å skrive
        with open(r"results\\" + txtName + ".txt", "w") as log_file:
            # Omdiriger sys.stdout til filen
            original_stdout = sys.stdout
            sys.stdout = log_file
            constructor = None 

            # Skriver klokkeslettet til når filen ble opprettet
            now = datetime.datetime.now() 
            log_file.write('Solution generated at time: {}\n\n'.format(now.strftime("%Y-%m-%d %H:%M:%S")))
            print('-------------------------------------------------------')

            '''
            Printer alle rutene som inngår i routeplan
            '''
            print("Printer alle rutene")
            for day in range(1, self.days +1): 
                for route in self.routes[day]: 
                    route.printSoultion()
            self.updateObjective()
            print("operator brukt:", operator_string)
            print("objective ", self.objective)
            print("visits", self.visits)
            print("treatments", self.treatments)
            print("allocated patients ", self.allocatedPatients)
            print("not allocated ", self.notAllocatedPatients)
            print("illegalNotAllocatedPatients", self.illegalNotAllocatedPatients)
            print("illegalNotAllocatedTreatments", self.illegalNotAllocatedTreatments)
            print("illegalNotAllocatedVisits", self.illegalNotAllocatedVisitsWithPossibleDays)
            print("illegalNotAllocatedActivities", self.illegalNotAllocatedActivitiesWithPossibleDays)

             # Tilbakestill sys.stdout til original
            sys.stdout = original_stdout
    
    def printSolution1(self, day):
            '''
            Printer alle rutene som inngår i routeplan
            '''
            print("Printer alle rutene")
            for route in self.routes[day]: 
                route.printSoultion()
            self.updateObjective()
            
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
        self.objective = [0, 0, 0, 0, 0]
        self.calculateWeeklyHeaviness()
        self.calculateDailyHeaviness()
        self.objective[1] = self.weeklyHeaviness
        self.objective[2] = self.dailyHeaviness
        for day in range(1, 1+self.days): 
            for route in self.routes[day]: 
                route.updateObjective()
                self.objective[0] += route.suitability
                self.objective[3] += route.aggSkillDiff 
                self.objective[4] += route.travel_time
   
        
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
            
    def getRouteSkillLevForActivityID(self, activityID): 
        for day in range(1, self.days +1): 
            for route in self.routes[day]: 
                for act in route.route: 
                    if act.id == activityID: 
                        return route.skillLev
                    
    def removeActivityIDgetRemoveDay(self, activityID):
        #TODO: Finne ut når attributter skal restartes. Det fungerer ikke slik det er nå. 
        #Oppdateringen må kjøres etter de er restartet, slik at de tilhørende aktivitetne får beskjed
        for day in range(1, self.days +1): 
            for route in self.routes[day]: 
                for act in route.route:
                    if act.id == activityID: 
                        route.removeActivityID(activityID)
                        #Beg: Må oppdater de på andre dager slik at de ikke er like bundet av aktivitetens tidsvinduer
                        self.updateDependentActivitiesBasedOnRoutePlanOnDay(act, day)
                        return day
                    
    def updateAllocationAfterPatientInsertor(self, patient, constructor): 
        #Oppdaterer allokerings dictionariene 
        '''
        if patient == 49:
            print("visit mellom status REPAIRED", self.visits[70])
            print("visit mellom status INSERTORPLAN", self.visits[70])
        
        self.allocatedPatients[patient] = constructor.patients_df.loc[patient, 'treatmentsIds']
        for treatment in [item for sublist in self.allocatedPatients.values() for item in sublist]: 
            self.treatments[treatment] = constructor.treatment_df.loc[treatment, 'visitsIds']
        for visit in [item for sublist in self.treatments.values() for item in sublist]: 
            self.visits[visit] = constructor.visit_df.loc[visit, 'activitiesIds']
        '''
        self.allocatedPatients[patient] = constructor.patients_df.loc[patient, 'treatmentsIds']
        for treatment in self.allocatedPatients[patient]:
            self.treatments[treatment] = constructor.treatment_df.loc[treatment, 'visitsIds']
            for visit in self.treatments[treatment]: 
                self.visits[visit] = constructor.visit_df.loc[visit, 'activitiesIds']

        #Fjerner pasienten fra ikkeAllokert listen 
        if patient in self.notAllocatedPatients: 
            self.notAllocatedPatients.remove(patient)