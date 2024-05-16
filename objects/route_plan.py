
#import pandas as pd
#import numpy as np
import os
import sys
sys.path.append( os.path.join(os.path.split(__file__)[0],'..') )  # Include subfolders
from objects.employee import Employee
from objects.route import Route
import copy
import random 
import datetime
depot = (59.9365, 10.7396)
#from config.main_config import depot
#from config.main_config import penalty_act, penalty_visit, penalty_treat, penalty_patient
#from config.main_config import  weight_DW, weight_WW, weight_SG, weight_S

class RoutePlan:
    def __init__(self, days, employee_df, folder_name, main_config):
        self.employee_df = employee_df
        self.folder_name = folder_name
        
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
        self.aggSkillDiff = 0
        self.aggDeviationPrefSpes = 0 

        self.treatments = {}
        self.visits = {}
        self.allocatedPatients = {}
        self.notAllocatedPatients = []
        self.illegalNotAllocatedPatients = []
        self.illegalNotAllocatedTreatments = []
        self.illegalNotAllocatedVisitsWithPossibleDays = {}
        self.illegalNotAllocatedActivitiesWithPossibleDays = {}

        self.main_config = main_config

    '''
    Hvordan vil vi endre klassen med nye route_plan -> Vil ikke ha noen endringer i funksjonalitet, så fikser på oppsettet, men ingen 
   

    Notater Agnes: 
    Gå gjennom hver 

    Første aktivitet, finne den som den har same employee aktivitet med, og sjekke at det er plass til den. Det må ikke være i samme tids

    Spørsmål/Problemer: 
    * Den må jo iterere seg både gjennom tidspunkter og plasser i ruten. Det er altså tre ting å velge: rute, plass i rekkefølgen og starttidspunkt. 

    Kan sjekke rutene og holde styr på hvordan viduene for innsetting ser ut, basert på det som ligger der.
    Eller bare kjøre deepcopy av ruteplanen og sjekke om de neste innsettingen vil gå gjennom 
    Da må vi også dypkopiere aktiviteten for, dette er ikke de ekte aktiviteen 

    Dette kan nok kjøres rekursivt på noen måte.

    Poenget er velge plass, 
        Neste må velge plass,
            Neste velge plass, 

    for hver rute og hver indeks så: 
        

    '''


    def sortRoutesByAcitivyLocation(self, routes, activity):
        #Sjekker om det er depot aktivitet, da returnere bare listen random av hva som lønner seg 
        if activity.location == depot: 
            random.shuffle(routes)
            return routes
  
   
        return sorted(routes, key=lambda route: abs(route.averageLocation[0] - activity.location[0]) + abs(route.averageLocation[1]- activity.location[1]))


    def makeRoutesGroupedBySkill(self): 
        route_grouped_by_skill = {day: {} for day in range(1, self.days+1)}      
        for day in range (1, self.days+1): 
            routes_grouped_by_skill_for_day = {}
            for route in self.routes[day].values():
                skill_level = route.skillLev 
                if skill_level not in routes_grouped_by_skill_for_day:
                    routes_grouped_by_skill_for_day[skill_level] = [route]
                else:
                    routes_grouped_by_skill_for_day[skill_level].append(route)
            route_grouped_by_skill[day] = routes_grouped_by_skill_for_day

        return route_grouped_by_skill
            
                
    def getSortedRoutes(self, activity, day): 
        routes = [route for route in self.routes[day].values() if route.checkTrueFalse(activity)]
        #routes = [item for key, value_list in self.makeRoutesGroupedBySkill()[day].items() if key >= activity.skillReq for item in value_list]
        return sorted(routes, key=lambda route: (len(route.route), route.skillLev))

    
    def getSortedRoutesForBetter(self, activity, day):     
        #TODO: Her er det mulig å velge hvilken metode som er ønskelig å kjøre med. De gir ganske ulike resultater. 
        # De metodene som bruker random-biblioteket vil gi nye løsninger for hver kjøring (med samme datasett).
        # Grupperer ruter basert på profesjonen til den ansatte
    
        #routes_grouped_by_skill = self.makeRoutesGroupedBySkill()[day]
         # Iterer gjennom sorterte professionLevels og iterer i tilfeldig rekkefølge

        routes_grouped_by_skill = {}
        for route in self.routes[day].values():
            skill_level = route.skillLev 
            if skill_level not in routes_grouped_by_skill:
                routes_grouped_by_skill[skill_level] = [route]
            else:
                routes_grouped_by_skill[skill_level].append(route)

        routes = []
        for act_skill_level in range (activity.skillReq, 4): 
            try:
                routes_for_skill = routes_grouped_by_skill[act_skill_level]
            #TODO: Sortere hvor mange som er 
            except: 
                routes_for_skill = []
     
            routes_for_skill = self.sortRoutesByAcitivyLocation(routes_for_skill, activity)
            #random.shuffle(routes_for_skill)
            
            routes += routes_for_skill

        return [route for route in routes if route.checkTrueFalse(activity)]


    def addActivityOnDay(self, activity, day):
     
        
        for route in self.getSortedRoutes(activity, day):
  
            #TODO: Update funskjonene burde sjekkes med de andre   
            #TODO: Hvorfor er det bare denne ene som skal oppdateres i forhold til de andre? Er det fordi de  i ruten allerede er oppdatert
            #Ettersom vi ikke kjører på de andre, så antar vi at de resterende aktivitetene har riktig oppdaterte grenserf fra andre ruter       
            #Beg: Ettersom aktivteten ikke finnes i ruten, har den ikke oppdatert grensene mot andr aktiviteter  
            
            #Denne trenger vi nok ikke. Ford disse blir nok oppdatert av funksjonen under.
   
            self.updateActivityBasedOnRoutePlanOnDay(activity, day)

            #Beg: Disse aktivitetene flyttes muligens når vi skvinser inn aktivitet i ruta
            for willPossiblyMoveActivity in route.route: 
                self.updateActivityBasedOnRoutePlanOnDay(willPossiblyMoveActivity, day)
        
            
            insertStatus = route.addActivity(activity)
      
            #TODO: Er det unødvendig å gjøre oppdatering både før og etter 
            #Beg: Alle aktivteter kan ha blitt flyttet på i ruten og må derfor oppdatere grensene på tvers 
            #Må gjøres på alle fordi alle kan ha blitt flyttet
            for possiblyMovedActivity in route.route: 
                self.updateDependentActivitiesBasedOnRoutePlanOnDay(possiblyMovedActivity, day)
        
            if insertStatus:
                return True
        return False


    def remove_activityIDs_from_route_plan(self, activityIDs):
        for day in range(1, self.days +1): 
            for route in self.routes[day].values(): 
                for act in route.route: 
                    if act.id in activityIDs:
                        route.removeActivityID(act.id)

    def remove_activityIDs_return_day(self, removed_activityIDs):
        original_day = None
        for day in range(1, self.days +1): 
            for route in self.routes[day].values(): 
                for act in route.route: 
                    if act.id in removed_activityIDs:
                        route.removeActivityID(act.id)
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
        # Ensure directory exists
        #results_dir = os.path.join('results', self.folder_name)
        os.makedirs(self.folder_name, exist_ok=True)

        # Open the file for writing in the correct directory
        file_path = os.path.join(self.folder_name, txtName + ".txt")
        with open(file_path, "w") as log_file:
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
            print("objective 2 [weeklyHeaviness, dailyHeaviness, aggSkillDiff, aggDeviationPrefSpes]", [self.weeklyHeaviness, self.dailyHeaviness,self.aggSkillDiff , self.aggDeviationPrefSpes])
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
        
        '''
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
        self.objective = [0, 0, 0, 0]
        self.calculateWeeklyHeaviness()
        self.calculateDailyHeaviness()
        self.calculateTotalContinuity()
        self.aggSkillDiff = 0
        self.aggDeviationPrefSpes = 0 
        for day in range(1, 1+self.days): 
            for route in self.routes[day].values(): 
                route.updateObjective()
                self.objective[0] += route.suitability
                self.aggSkillDiff += route.aggSkillDiff 
                self.aggDeviationPrefSpes += route.deviationPrefSpes
                self.objective[3] += route.travel_time   
        self.objective[2] = self.totalContinuity 
        self.objective[1] = round(self.main_config.weight_WW*self.weeklyHeaviness + self.main_config.weight_DW*self.dailyHeaviness + self.main_config.weight_S*self.aggSkillDiff + self.main_config.weight_SG*self.aggDeviationPrefSpes)
        #Oppdaterer første-objektivet med straff for illegal      
        self.objective[0] = self.calculatePenaltyIllegalSolution(current_iteration, total_iterations)

    '''
    HER ER OBJEKTIVENE IKKE SLÅTT SAMMEN.
    def updateObjective(self, current_iteration, total_iterations): 
        self.objective = [0, 0, 0, 0, 0, 0]
        self.calculateWeeklyHeaviness()
        self.calculateDailyHeaviness()
        self.calculateTotalContinuity()
        self.objective[1] = self.totalContinuity
        self.objective[2] = self.weeklyHeaviness
        self.objective[3] = self.dailyHeaviness
        for day in range(1, 1+self.days): 
            for route in self.routes[day].values(): 
                route.updateObjective()
                self.objective[0] += route.suitability
                self.objective[4] += route.aggSkillDiff 
                self.objective[5] += route.travel_time   
        #Oppdaterer første-objektivet med straff for illegal      
        self.objective[0] = self.calculatePenaltyIllegalSolution(current_iteration, total_iterations)
    '''

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

            penalty = iteration_factor * (len(self.illegalNotAllocatedPatients) * self.main_config.penalty_patient
                    + len(self.illegalNotAllocatedTreatments) * self.main_config.penalty_treat 
                    + len(self.illegalNotAllocatedVisitsWithPossibleDays) * self.main_config.penalty_visit
                    + len(self.illegalNotAllocatedActivitiesWithPossibleDays) * self.main_config.penalty_act)
            
            updated_first_objective = self.objective[0] - penalty
            #print(f'PENALTY IN FIRST OBJECTIVE: {penalty}. Original objective: {self.objective[0]}, Updated objective: {updated_first_objective}')
        return updated_first_objective
     
    def calculateWeeklyHeaviness(self):
        daily_heaviness_within_group = {}

        for day in range(1, self.days +1):
            num_employee_with_profession_on_day = {}
            for route in self.routes[day].values():
                profession = route.skillLev
                if profession not in daily_heaviness_within_group:
                    daily_heaviness_within_group[profession] = {}
                
                if day not in daily_heaviness_within_group[profession]:
                    daily_heaviness_within_group[profession][day] = route.calculateTotalHeaviness()

                # Summerer opp heaviness for hver dag innen hver profession level
                else:
                    daily_heaviness_within_group[profession][day] += route.calculateTotalHeaviness()
                
                if profession not in num_employee_with_profession_on_day.keys(): 
                    num_employee_with_profession_on_day[profession] = 0 

                num_employee_with_profession_on_day[profession] += 1  
                
                #print(f'Profession {profession} day {day}: {daily_heaviness_within_group[profession][day]}')
            
            # Finnes gjennomsnittlig 'heaviness' for hver profesjon basert på antall ansatte som jobber de ulike dagene.
            #num_employees_day = len(self.routes[day].values()) 
    
            for profession in daily_heaviness_within_group.keys():
                if day in daily_heaviness_within_group[profession]:
                    daily_heaviness_within_group[profession][day] /= num_employee_with_profession_on_day[profession]

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
                route.removeActivityID(activity.id)
                #Beg: Må oppdater de på andre dager slik at de ikke er like bundet av aktivitetens tidsvinduer
                self.updateDependentActivitiesBasedOnRoutePlanOnDay(activity, day)
              
    def insertActivityInEmployeesRoute(self, employeeID, activity, day): 
        #Må dyp kopiere aktiviten slik at ikke aktiviteten i den orginale rotueplanen restartes
        insert_activity = copy.deepcopy(activity)
         
        for route in self.routes[day].values(): 
            if route.employee.id == employeeID:
                #Beg: Må oppdatere grensene til alle i ruten som muligens kan flytte seg når vi prøver å legge til aktivtete
              
                self.updateActivityBasedOnRoutePlanOnDay(insert_activity, day)
             
                status = route.addActivity(insert_activity)
                for routeActivity in route.route: 
                    self.updateActivityBasedOnRoutePlanOnDay(routeActivity, day)
                return status



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
                        self.updateDependentActivitiesBasedOnRoutePlanOnDay(act, day)
                        return day
                    
    def updateAllocationAfterPatientInsertor(self, patient, constructor): 
        #Oppdaterer allokerings dictionariene 
        '''
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


    def getActivityAndActivityIndexAndRoute(self, actID): 
        '''
        returnerer employee ID-en til den ansatte som er allokert til en aktivitet 
        
        Arg: 
        actID (int): ID til en aktivitet som gjøres en gitt dag
        day (int): dagen aktiviten finnes i en rute  

        Return: 
        activity (Activity) Activity objektet som finnes i en rute på en gitt dag
        '''
        for day in range(1, self.days+1):
            for route in self.routes[day].values(): 
                index = 0 
                for act in route.route: 
                    if act.id == actID: 
                        return act, index, route 
                    index += 1
        return None, None, None


    def getDayForActivityID(self, actID): 
        '''
        returnerer employee ID-en til den ansatte som er allokert til en aktivitet 
        
        Arg: 
        actID (int): ID til en aktivitet som gjøres en gitt dag
        day (int): dagen aktiviten finnes i en rute  

        Return: 
        activity (Activity) Activity objektet som finnes i en rute på en gitt dag
        '''
        for day in range(1, self.days+1):
            for route in self.routes[day].values(): 
                for act in route.route: 
                    if act.id == actID: 
                        return day
        return None
    

        