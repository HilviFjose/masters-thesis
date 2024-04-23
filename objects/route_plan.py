
import pandas as pd
#import numpy as np
import os
import sys
sys.path.append( os.path.join(os.path.split(__file__)[0],'..') )  # Include subfolders
from objects.employee import Employee
from objects.route import Route
import copy
import random 
import datetime
from config.construction_config import depot
from config.main_config import penalty_act, penalty_visit, penalty_treat, penalty_patient
from config.construction_config import preferredEmployees
from config.main_config import weight_C, weight_DW, weight_WW, weight_SG, weight_S


class RoutePlan:
    def __init__(self, days, employee_df):
        self.employee_df = employee_df
        
        employee_skills = {} # For å holde styr på ansattes ferdigheter

        self.employees = [] #Antar at de alle ansatte jobber alle dager

        #Lager employees objektene og lagerer de i en liste 
        for key, value in employee_df.iterrows():
            emp = Employee(employee_df, key)
            employee_skills[key] = value['professionalLevel'] 
            self.employees.append(emp)

        self.routes = {day: {employee.id: None for employee in self.employees} for day in range(1, days+1)}
        self.days = days 
        for day in range (1, self.days +1):
            for employee in self.employees:
                self.routes[day][employee.id] =  Route(day, employee) # Lagrer professionalLevel sammen med Route

        # Sorter routes basert på skill for hver dag - TODO: Burde muligens sorteres på en annen måte
        #for day in self.routes:
        #    self.routes[day] = [route for _, route in sorted(self.routes[day], key=lambda x: x[0])]

        #OBS: Jeg forstår ikke hvorfor denne er slik: 
        #self.routes[day].append((emp.skillLevel, Route(day, emp))) 
        
        
        self.objective = [0,0,0,0]
        self.weeklyHeaviness = 0
        self.dailyHeaviness = 0
        self.totalContinuity = 0

        self.treatments = {}
        self.visits = {}
        self.allocatedPatients = {}
        self.notAllocatedPatients = []
        self.illegalNotAllocatedPatients = []
        self.illegalNotAllocatedTreatments = []
        self.illegalNotAllocatedVisitsWithPossibleDays = {}
        self.illegalNotAllocatedActivitiesWithPossibleDays = {}


#TODO: Burde evaluere når disse sorteringsfunksjonene skal benyttes. Må ha en eller annen form for random innimellom hvertflal 
#Nå brukes den alltid
    def sortRoutesByAcitivyLocation(self, routes, activity):
       
        if activity.location == depot: 
            random.shuffle(routes)
            return routes
  
        return sorted(routes, key=lambda route: abs(route.averageLocation[0] - activity.location[0]) + abs(route.averageLocation[1]- activity.location[1]))

  
                
    def getSortedRoutes(self, activity, day): 
        
        routes_grouped_by_skill = {}
        for route in self.routes[day].values():
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
             
            routes_for_skill = self.sortRoutesByAcitivyLocation(routes_for_skill, activity)
            random.shuffle(routes_for_skill) #Denne sto her før, vanskelig å forstår hvorfor, er muligens et annet alternativ til sortRoutesByActivityLocation

            
            routes += routes_for_skill

        return routes

    '''
    Oppdateringsinfo: 
    I utganspunktet så skal man før hver flytting eller innsetting gjøre de hensynen man trenger, 
    det er altså aldri nødvendig å rydde opp etter seg ford man i de neste 
    '''
    def addActivityOnDay(self, activity, day):
        
        sorted_routes = self.getSortedRoutes(activity, day)

        for route in sorted_routes:
   
            self.updateActivityBasedOnRoutePlanOnDay(activity, day)

            #Beg: Disse aktivitetene flyttes muligens når vi skvinser inn aktivitet i rute
            for willPossiblyMoveActivity in route.route: 
                self.updateActivityBasedOnRoutePlanOnDay(willPossiblyMoveActivity, day)
        
      
            #OBS: Denne er fjernet nå grunnet at oppdateringen skal gjøres på forhånd, og ikke i ettertid
            #for possiblyMovedActivity in route.route: 
            #    self.updateDependentActivitiesBasedOnRoutePlanOnDay(possiblyMovedActivity, day)
        
            
            if route.addActivity(activity):
                return True
            
        return False


    '''
    Feil funnet: Det gjøres en fjerning først, som gjør at vi aldri vil sjekke den første 
    '''

    def remove_activityIDs_from_route_plan(self, activityIDs):
        activityIDs_set = set(activityIDs)
        for day in range(1, self.days +1): 
            for route in self.routes[day].values(): 
                inforoute = [act.id for act in route.route]
                for actID in inforoute: 
                    if actID in activityIDs_set:
                        route.removeActivityID(actID)
        

    def remove_activityIDs_return_day(self, activityIDs):
        activityIDs_set = set(activityIDs)
        original_day = None
        for day in range(1, self.days +1): 
            for route in self.routes[day].values(): 
                inforoute = [act.id for act in route.route]
                for actID in inforoute: 
                    if actID in activityIDs_set:
                        route.removeActivityID(actID)
                        original_day = day
        return original_day


    
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
 
    def printSolution(self, txtName, operator_string, current_iteration = None):
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
            #self.updateObjective()
            print("operator brukt:", operator_string)
            print("updated objective ", self.objective)
            print("primary objective without penalty ", self.getOriginalObjective())
            print("visits", self.visits)
            print("treatments", self.treatments)
            print("allocated patients ", self.allocatedPatients)
            print("not allocated ", self.notAllocatedPatients)
            print("illegalNotAllocatedPatients", self.illegalNotAllocatedPatients)
            print("illegalNotAllocatedTreatments", self.illegalNotAllocatedTreatments)
            print("illegalNotAllocatedVisits", self.illegalNotAllocatedVisitsWithPossibleDays)
            print("illegalNotAllocatedActivities", self.illegalNotAllocatedActivitiesWithPossibleDays)

            print('-------------------------------------------------------')

            '''
            Printer alle rutene som inngår i routeplan
            '''
            print("Printer alle rutene")
            for day in range(1, self.days +1): 
                for route in self.routes[day].values(): 
                    route.printSoultion()

             # Tilbakestill sys.stdout til original
            sys.stdout = original_stdout
            
    def getEmployeeIDAllocatedForActivity(self, activity, day): 
        '''
        returnerer employee ID-en til den ansatte som er allokert til en aktivitet 
        
        Arg: 
        activity (Activity): Activity objekt som finnes i en rute på en gitt dag
        day (int): dagen aktiviten finnes i en rute  

        Return: 
        Int employeeID til den ansatte som er allokert til aktiviteten 
        
        '''
        for route in self.routes[day].values(): 
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
        
        
        empForAct = None
        activityIDinRoute = False
        otherEmpl = []
        for route in self.routes[day].values(): 
            for act in route.route: 
                if act.id == activityID: 
                    activityIDinRoute = True
                    empForAct = route.employee.id
        if not activityIDinRoute: 
            return otherEmpl
        for route in self.routes[day].values(): 
            if route.employee.id != empForAct: 
                otherEmpl.append(route.employee.id)
        return otherEmpl
        '''

        empForAct = None
        allEmplIDs = set()

        for route in self.routes[day].values():
            for act in route.route:
                # Add every employee ID encountered to the set.
                allEmplIDs.add(route.employee.id)
                
                # If the current activity is the one we're interested in,
                # record the employee ID and continue collecting others.
                if act.id == activityID:
                    empForAct = route.employee.id

        # If the activityID was found and associated with an employee,
        # remove that employee's ID from the set of all employee IDs.
        if empForAct is not None:
            allEmplIDs.discard(empForAct)
            return list(allEmplIDs)
        else:
            # If the activity wasn't found, return an empty list.
            return []
            
            

    def getActivity(self, actID, day): 
        '''
        returnerer employee ID-en til den ansatte som er allokert til en aktivitet 
        
        Arg: 
        actID (int): ID til en aktivitet som gjøres en gitt dag
        day (int): dagen aktiviten finnes i en rute  

        Return: 
        activity (Activity) Activity objektet som finnes i en rute på en gitt dag
        '''
        for route in self.routes[day].values(): 
            for act in route.route: 
                if act.id == actID: 
                    return act 
        return None 
    
    def getActivityFromEntireRoutePlan(self, actID): 
        '''
        returnerer employee ID-en til den ansatte som er allokert til en aktivitet 
        
        Arg: 
        actID (int): ID til en aktivitet som gjøres en gitt dag
        day (int): dagen aktiviten finnes i en rute  

        Return: 
        activity (Activity) Activity objektet som finnes i en rute på en gitt dag
        '''
        for day in range(1, self.days +1): 
            for route in self.routes[day].values(): 
                for act in route.route: 
                    if act.id == actID: 
                        return act 
        return None       



    def getOriginalObjective(self):
        first_objective = 0
        for day in range(1, 1+self.days): 
            for route in self.routes[day].values(): 
                route.updateObjective()
                first_objective += route.suitability
        return first_objective
    
    def updateObjective(self, current_iteration, total_iterations): 
        weight_C, weight_DW, weight_WW, weight_SG, weight_S
        self.objective = [0, 0, 0, 0]
        self.calculateWeeklyHeaviness()
        self.calculateDailyHeaviness()
        self.calculateTotalContinuity()
        aggSkillDiff = 0
        for day in range(1, 1+self.days): 
            for route in self.routes[day].values(): 
                route.updateObjective()
                self.objective[0] += route.suitability
                aggSkillDiff += route.aggSkillDiff 
                self.objective[3] += route.travel_time   
        self.objective[1] = self.totalContinuity 
        self.objective[2] = round(weight_WW*self.weeklyHeaviness + weight_DW*self.dailyHeaviness + weight_S*aggSkillDiff)
        #Oppdaterer første-objektivet med straff for illegal      
        self.objective[0] = self.calculatePenaltyIllegalSolution(current_iteration, total_iterations)


    def calculatePenaltyIllegalSolution(self, current_iteration, total_iterations):
        # Penalty in first objective per illegal treatment, visit or activity 
        updated_first_objective = self.objective[0]
        penalty = 0
        if (len(self.illegalNotAllocatedPatients)
            + len(self.illegalNotAllocatedTreatments)
            + len(self.illegalNotAllocatedVisitsWithPossibleDays) 
            + len(self.illegalNotAllocatedActivitiesWithPossibleDays)) > 0:

            iteration_factor = 1
            if current_iteration != None and total_iterations != None:
                iteration_factor = max(1 - ((total_iterations - current_iteration) / total_iterations), 0.1) #Tvinger iterasjonsfaktoren til å være mellom 0.1 og 1

            penalty = iteration_factor * (len(self.illegalNotAllocatedPatients) * penalty_patient
                    + len(self.illegalNotAllocatedTreatments) * penalty_treat 
                    + len(self.illegalNotAllocatedVisitsWithPossibleDays) * penalty_visit
                    + len(self.illegalNotAllocatedActivitiesWithPossibleDays) * penalty_act)
            
            updated_first_objective = self.objective[0] - penalty
            #print(f'PENALTY IN FIRST OBJECTIVE: {penalty}. Original objective: {self.objective[0]}, Updated objective: {updated_first_objective}')
        return updated_first_objective
     
    def calculateWeeklyHeaviness(self):
        daily_heaviness_within_group = {}

        for day in range(1, self.days +1):
            for route in self.routes[day].values():
                profession = route.skillLev
                if profession not in daily_heaviness_within_group:
                    daily_heaviness_within_group[profession] = {}
                
                if day not in daily_heaviness_within_group[profession]:
                    daily_heaviness_within_group[profession][day] = route.calculateTotalHeaviness()

                # Summerer opp heaviness for hver dag innen hver profession level
                else:
                    daily_heaviness_within_group[profession][day] += route.calculateTotalHeaviness()
                
                #print(f'Profession {profession} day {day}: {daily_heaviness_within_group[profession][day]}')
            
            # Finnes gjennomsnittlig 'heaviness' for hver profesjon basert på antall ansatte som jobber de ulike dagene.
            num_employees_day = len(self.routes[day].values()) 
            for profession in daily_heaviness_within_group.keys():
                if day in daily_heaviness_within_group[profession]:
                    daily_heaviness_within_group[profession][day] /= num_employees_day

        # Kalkulerer differansen mellom maks og min 'heaviness' for hver profession level
        weekly_diffs = []
        for profession, days in daily_heaviness_within_group.items():
            if days:
                profession_heaviness_values = list(days.values())
                #print(f"profession {profession} with tot heaviness days {profession_heaviness_values}")
                weekly_diffs.append(max(profession_heaviness_values)-min(profession_heaviness_values))
                #print(f"profession {profession} weekly diff {weekly_diffs}")
        
        self.weeklyHeaviness = sum(weekly_diffs)

    def calculateDailyHeaviness(self):
        daily_diffs = []
        #for day, routes in self.routes.items():    
        for day in range(1, self.days+1):
            profession_groups = {}
            #for route in routes:
            for route in self.routes[day].values():
                profession = route.skillLev
                if profession not in profession_groups:
                    profession_groups[profession] = []
                profession_groups[profession].append(route.calculateTotalHeaviness())

            for profession, heaviness in profession_groups.items():
                daily_diffs.append(max(heaviness) - min(heaviness))
        self.dailyHeaviness = sum(daily_diffs)

    def calculateTotalContinuity(self):
        continuity_routes = []
        for day in range(1, self.days+1):
            for route in self.routes[day].values():
                continuity_route = 0
                for act in route.route:
                    continuity_score, employeeIds = next(iter(act.employeeHistory.items()))
                    if act.skillReq > 1: #Forsikre om at det kun er health care tasks som får en score
                        if act.continuityGroup == 1: 
                            if route.employee.id in employeeIds:
                                continuity_route += continuity_score
                        elif act.continuityGroup == 2: 
                            if route.employee.id in employeeIds:
                                continuity_route += continuity_score
                        else: 
                            if route.employee.id in employeeIds:
                                continuity_route += continuity_score
                           
                continuity_routes.append(continuity_route)

        self.totalContinuity = - sum(continuity_routes)


    def removeActivityFromEmployeeOnDay(self, employee, activity, day):
        #TODO: Finne ut når attributter skal restartes. Det fungerer ikke slik det er nå. 
        #Oppdateringen må kjøres etter de er restartet, slik at de tilhørende aktivitetne får beskjed
        for route in self.routes[day].values(): 
            if route.employee.id == employee:
                if activity.id == 88: 
                    print("kommer hit - 2")
                route.removeActivityID(activity.id)
        


                #Beg: Må oppdater de på andre dager slik at de ikke er like bundet av aktivitetens tidsvinduer
                #self.updateDependentActivitiesBasedOnRoutePlanOnDay(activity, day)
              
    def insertActivityInEmployeesRoute(self, employeeID, activity, day): 
        #Må dyp kopiere aktiviten slik at ikke aktiviteten i den orginale rotueplanen restartes
        insert_activity = copy.deepcopy(activity)
         
        for route in self.routes[day].values(): 

            
            
            if route.employee.id == employeeID:
                #TODO: Her må muligens de aktivitene som kan flyttes seg ved innsettingen av en annen aktivitet oppdateres på forhånd? 
                #Beg: Må oppdatere grensene til alle i ruten som muligens kan flytte seg når vi prøver å legge til aktivtete

                #Det er noen som er lister og noen som er arrays, det er 
                for willPossiblyMoveActivity in route.route: 
                    self.updateActivityBasedOnRoutePlanOnDay(willPossiblyMoveActivity, day)
              
                self.updateActivityBasedOnRoutePlanOnDay(insert_activity, day)
             
                return route.addActivity(insert_activity)
                '''
                status = route.addActivity(insert_activity)

                for routeActivity in route.route: 
                    self.updateActivityBasedOnRoutePlanOnDay(routeActivity, day)
                return status
                '''

    
  

    def updateActivityBasedOnRoutePlanOnDay(self, activity,day):
        '''
        Denne funksjonen skal håndtere oppdatering av de variable attributttene til activity
        Basert på det som allerede ligger inne i routeplanen 
        '''    

        #Her håndteres pick up and delivery
        if activity.pickUpActivityID != 0 : 
            otherEmplOnDay = self.getListOtherEmplIDsOnDay(activity.pickUpActivityID, day)
            activity.employeeNotAllowedDueToPickUpDelivery = otherEmplOnDay
            
        #Her håndteres presedens.   
        #Aktivitetns earliests starttidspunkt oppdateres basert på starttidspunktet til presedens aktiviten

        for prevNodeID in activity.PrevNode: 
            
            prevNodeAct = self.getActivity(prevNodeID, day)
            if prevNodeAct != None:
                activity.setNewEarliestStartTime(prevNodeAct.startTime + prevNodeAct.duration, prevNodeID)

        for nextNodeID in activity.NextNode: 
            nextNodeAct = self.getActivity(nextNodeID, day)
            if nextNodeAct != None:
                activity.setNewLatestStartTime(nextNodeAct.startTime - activity.duration, nextNodeID)
        
        #Her håndteres presedens med tidsvindu
        #aktivitetens latest start time oppdateres til å være seneste starttidspunktet til presedensnoden
        for PrevNodeInTimeID in activity.PrevNodeInTime: 
            prevNodeAct = self.getActivity(PrevNodeInTimeID[0], day)
            if prevNodeAct != None:
                activity.setNewLatestStartTime(prevNodeAct.startTime+ prevNodeAct.duration + PrevNodeInTimeID[1], PrevNodeInTimeID[0])
                activity.setNewEarliestStartTime(prevNodeAct.startTime + prevNodeAct.duration, PrevNodeInTimeID[0])


        for NextNodeInTimeID in activity.NextNodeInTime: 
            nextNodeAct = self.getActivity(NextNodeInTimeID[0], day)
            if nextNodeAct != None:
                activity.setNewEarliestStartTime(nextNodeAct.startTime - NextNodeInTimeID[1], NextNodeInTimeID[0])
                activity.setNewLatestStartTime(nextNodeAct.startTime - activity.duration, NextNodeInTimeID[0])


        
    def updateDependentActivitiesBasedOnRoutePlanOnDay(self, activity ,day):
        for depActID in activity.dependentActivities: 
            depActivity = self.getActivity(depActID, day)
            if depActivity != None: 
                self.updateActivityBasedOnRoutePlanOnDay(depActivity, day)

    def insertNewRouteOnDay(self, new_route,  day):
        employeeOnDayList = [route.employee.id for route in self.routes[day].values()]
        for emplID in employeeOnDayList: 
            if emplID == new_route.employee.id: 
                del self.routes[day][emplID]
                self.routes[day][emplID] = new_route
                #self.routes[day].remove(org_route)
                #self.routes[day].append(new_route) 
    
    #TODO: Når kalles switch route? kan vi kopiere 
    '''
    Hva er konseptet her? Vi ønsker å finne den den ansatte hvor den nye ruten skal settes inn
    '''
            
    def getRouteSkillLevForActivityID(self, activityID): 
        for day in range(1, self.days +1): 
            for route in self.routes[day].values(): 
                for act in route.route: 
                    if act.id == activityID: 
                        return route.skillLev
                    
    def removeActivityIDgetRemoveDay(self, activityID):
        #TODO: Finne ut når attributter skal restartes. Det fungerer ikke slik det er nå. 
        #Oppdateringen må kjøres etter de er restartet, slik at de tilhørende aktivitetne får beskjed
        for day in range(1, self.days +1): 
            for route in self.routes[day].values(): 
                for act in route.route:
                    if act.id == activityID: 
                        route.removeActivityID(activityID)
                        #Beg: Må oppdater de på andre dager slik at de ikke er like bundet av aktivitetens tidsvinduer
                        #self.updateDependentActivitiesBasedOnRoutePlanOnDay(act, day)
                        return day
                    
    def updateAllocationAfterPatientInsertor(self, patient, constructor): 
        #Oppdaterer allokerings dictionariene 
  
        self.allocatedPatients[patient] = constructor.patients_df.loc[patient, 'treatmentsIds']
        for treatment in self.allocatedPatients[patient]:
            self.treatments[treatment] = constructor.treatment_df.loc[treatment, 'visitsIds']
            for visit in self.treatments[treatment]: 
                self.visits[visit] = constructor.visit_df.loc[visit, 'activitiesIds']

        #Fjerner pasienten fra ikkeAllokert listen 
        if patient in self.notAllocatedPatients: 
            self.notAllocatedPatients.remove(patient)


    def getActivityAndActivityIndexAndRoute(self, actID): 
        for day in range(1, self.days+1):
            for route in self.routes[day].values(): 
                index = 0 
                for act in route.route: 
                    if act.id == actID: 
                        return act, index, route 
                    index += 1
        return None, None, None


    def getDayForActivityID(self, actID): 
        for day in range(1, self.days+1):
            for route in self.routes[day].values(): 
                for act in route.route: 
                    if act.id == actID: 
                        return day
        return None