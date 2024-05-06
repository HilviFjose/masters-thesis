import copy
from objects.patterns import pattern
from objects.activity import Activity
import random 
from helpfunctions import * 
from config.main_config import iterations, max_num_explored_branches


class Insertor:
    def __init__(self, constructor, route_plan, insertion_efficiency_level):
        self.constructor = constructor
        #self.route_plan = copy.deepcopy(route_plan)
        self.route_plan = route_plan
        self.rev = False

        self.InsertionFound_BetterInsertVisit = False
        self.InsertionFound_BetterInsertVisitWitLim = False
        self.InsertionFound_BestInsertVisit = False
        self.betterInsertVisit_explored_branches = 0


        self.visitOnDayInsertorList = [self.simple_insert_visit_on_day, self.better_insert_visit_on_day_with_iteration_limitation, self.better_insert_visit_on_day,  self.best_insert_visit_on_day]   
        if insertion_efficiency_level >= len(self.visitOnDayInsertorList): 
            print("IKKE GYLDIG insertion_efficiency_level")
        self.insertVisitOnDay = self.visitOnDayInsertorList[insertion_efficiency_level] #Dette er en funskjon 


    def insert_patient(self, patient):
        old_route_plan = copy.deepcopy(self.route_plan)
        #TODO: Treatments bør sorteres slik at de mest kompliserte komme tidligst
        treatments_index = self.constructor.patients_array[0].tolist().index('treatmentsIds')
        treamentList = self.constructor.patients_array[patient][treatments_index]
        for treatment in treamentList: 
            status = self.insert_treatment(treatment)
            if status == False: 
                self.route_plan = old_route_plan
                return False
        
        return True 

    #TODO: Sjekke denne funksjonen. Finne ut hvor denne funksjonaliteten skal ligge, for i de andre illegal funksjonene så er det 
    

    def insert_treatment(self, treatment): 
        visitsIds_index = self.constructor.treatments_array[0].tolist().index('visitsIds')
        visitList = self.constructor.treatments_array[treatment][visitsIds_index]

        old_route_plan = copy.deepcopy(self.route_plan)

        '''
            #Reverserer listen annen hver gang for å ikke alltid begynne med pattern på starten av uken
            if self.rev == True:
                patterns =  reversed(pattern[self.constructor.treatment_df.loc[treatment, 'patternType']])
                self.rev = False
            else: 
                patterns = pattern[self.constructor.treatment_df.loc[treatment, 'patternType']]
                self.rev = True
        '''
        #Iterer over alle patterns som er mulige for denne treatmenten
        patternType_index = self.constructor.treatments_array[0].tolist().index('patternType')
        patterns = pattern[self.constructor.treatments_array[treatment][patternType_index]]
        index_random = [i for i in range(len(patterns))]
        random.shuffle(index_random) #TODO: Hvis du skal feilsøke kan du vurdere å kommentere ut denne linjen. 

        for index in index_random:
            self.route_plan = copy.deepcopy(old_route_plan)
            insertStatus = self.insert_visit_with_pattern(visitList, patterns[index]) 
            if insertStatus == True:
                return True
            
        return False
    

    def insert_visit_with_pattern(self, visits, pattern):
        '''
        Funksjonen forsøker å legge til alle visits for pasienten. 

        Arg: 
        visits (list): Liste av vists som skal legges til i self.route_plan, eks: [5,6,7]
        pattern (list): Liste som inneholder et pattern, med 1 på dager visits skal gjennomføre, eks: [1,0,1,0,1]

        Returns: 
        True/False på om det var plass til visitene på hjemmesykehuset med dette patternet 
        '''

        visit_index = 0
        #Iterer gjennom alle dagene i patternet 
        for day_index in range(len(pattern)): 
            #hvis patternet på den gitte dagen er 1, så forsøker vi å inserte visittet på den gitte dagen
            #Dersom insert ikke er mulig returerer funkjsonen False
            if pattern[day_index] == 1: 
                insertStatus = self.insertVisitOnDay(visits[visit_index], day_index+1)
                #insertStatus = self.insert_visit_on_day(visits[visit_index], day_index+1) 
                if insertStatus == False: 
                    return False
                #Øker indeksen for å betrakte neste visit i visitlisten
                visit_index += 1 
        return True   
                
   

    def simple_insert_visit_on_day(self, visit, day):  
        activitiesIds_index = self.constructor.visits_array[0].tolist().index('activitiesIds')
        activitiesList = self.constructor.visits_array[visit][activitiesIds_index]
        old_route_plan = copy.deepcopy(self.route_plan)
        #Iterer over alle aktivitere i visitet som må legges til på denne dagen 
        # Create a list of activity objects
        activities = [Activity(self.constructor.activities_df, activityID) for activityID in activitiesList]
        for activity in activities: 
            activityStatus = self.route_plan.addActivityOnDay(activity, day)
            if activityStatus == False: 
                self.route_plan = old_route_plan
                return False
        #Dersom alle aktivitene har blitt lagt til returers true  
        return True
    
    def better_insert_visit_on_day(self, visit, day):
        
        self.InsertionFound_BetterInsertVisit = False 
        activitiesIds_index = self.constructor.visits_array[0].tolist().index('activitiesIds')
        activitiesList = self.constructor.visits_array[visit][activitiesIds_index]
        test_route_plan = copy.deepcopy(self.route_plan)
        
        activities = [Activity(self.constructor.activities_df, activityID) for activityID in activitiesList]
        activity = activities[0]
        rest_acitivites = activities[1:]
      
        old_route_plan = copy.deepcopy(test_route_plan)
        for route in test_route_plan.getSortedRoutes(activity, day):
            if self.InsertionFound_BetterInsertVisit == True: 
                break 
            for index_place in range(len(route.route)+1): 
            
                test_route_plan = copy.deepcopy(old_route_plan)

                if self.InsertionFound_BetterInsertVisit == False: 
                    self.insertNextActiviy_forBetterInsertion(activity, rest_acitivites, test_route_plan, day, route.employee.id, index_place)
                    if self.InsertionFound_BetterInsertVisit == True: 
                        break
                else: 
                    break
        
        return self.InsertionFound_BetterInsertVisit



    def insertNextActiviy_forBetterInsertion(self, activity, rest_acitivites, route_plan, day, employeeID, index_place):
        #TODO: Sammkjøre denne med andre aktiviteter som fungere 
        #BEG: Må ha med denne også for å sjekke om det er 
        route_plan.updateActivityBasedOnRoutePlanOnDay(activity, day)

        for activitiesWithPossibleNewUpdated in route_plan.routes[day][employeeID].route: 
            route_plan.updateActivityBasedOnRoutePlanOnDay(activitiesWithPossibleNewUpdated, day)

        insertStatus = route_plan.routes[day][employeeID].insertActivityOnIndex(activity, index_place)
  
        if insertStatus == False: 
            return
        
        if len(rest_acitivites) == 0: 
            self.route_plan = route_plan
            self.InsertionFound_BetterInsertVisit = True
            return
            
        
        next_actitivy = rest_acitivites[0]
        rest_acitivites = rest_acitivites[1:] 
        
       
        old_route_plan = copy.deepcopy(route_plan)
        for route in route_plan.getSortedRoutes(activity, day): 
            if self.InsertionFound_BetterInsertVisit == True: 
                break
            for index_place in range(len(route.route)+1): 
                route_plan = copy.deepcopy(old_route_plan)
    
                if self.InsertionFound_BetterInsertVisit == False: 
                    self.insertNextActiviy_forBetterInsertion(next_actitivy, rest_acitivites, route_plan, day, route.employee.id, index_place)
                    if self.InsertionFound_BetterInsertVisit == True: 
                        break
                else: 
                    break

    
    '''
    Når skal vi si at den er ferdig. Kan telle hver gang den kommer til en stopp

    Denne har returnert tidligere når vi har funnet en løsning som fungerer nå vil vi returnere 
    '''

    def better_insert_visit_on_day_with_iteration_limitation(self, visit, day):
        
        self.InsertionFound_BetterInsertVisitWitLim = False 
        self.betterInsertVisit_explored_branches = 0 

        activitiesIds_index = self.constructor.visits_array[0].tolist().index('activitiesIds')
        activitiesList = self.constructor.visits_array[visit][activitiesIds_index]
        test_route_plan = copy.deepcopy(self.route_plan)

        
        activities = [Activity(self.constructor.activities_df, activityID) for activityID in activitiesList]
        activity = activities[0]
        rest_acitivites = activities[1:]
      
        old_route_plan = copy.deepcopy(test_route_plan)
        for route in test_route_plan.getSortedRoutes(activity, day):
            if self.InsertionFound_BetterInsertVisitWitLim == True or self.betterInsertVisit_explored_branches > max_num_explored_branches: 
                break 
            for index_place in range(len(route.route)+1): 
            
                test_route_plan = copy.deepcopy(old_route_plan)

                if self.InsertionFound_BetterInsertVisitWitLim == False and self.betterInsertVisit_explored_branches <= max_num_explored_branches: 
                    self.insertNextActiviy_forBetterInsertion_with_iteration_limitation(activity, rest_acitivites, test_route_plan, day, route.employee.id, index_place)
                    if self.InsertionFound_BetterInsertVisitWitLim == True: 
                        break
                else: 
                    break
        
        return self.InsertionFound_BetterInsertVisitWitLim



    def insertNextActiviy_forBetterInsertion_with_iteration_limitation(self, activity, rest_acitivites, route_plan, day, employeeID, index_place):
        #TODO: Sammkjøre denne med andre aktiviteter som fungere 
        #BEG: Må ha med denne også for å sjekke om det er 
        route_plan.updateActivityBasedOnRoutePlanOnDay(activity, day)
       
        for activitiesWithPossibleNewUpdated in route_plan.routes[day][employeeID].route: 
            route_plan.updateActivityBasedOnRoutePlanOnDay(activitiesWithPossibleNewUpdated, day)

        insertStatus = route_plan.routes[day][employeeID].insertActivityOnIndex(activity, index_place)
  
        if insertStatus == False or self.betterInsertVisit_explored_branches > max_num_explored_branches: 
            self.betterInsertVisit_explored_branches += 1 
            return
        
        if len(rest_acitivites) == 0: 
            self.route_plan = route_plan
            self.InsertionFound_BetterInsertVisitWitLim = True
            return
            
        
        next_actitivy = rest_acitivites[0]
        rest_acitivites = rest_acitivites[1:] 
        
       
        old_route_plan = copy.deepcopy(route_plan)
        for route in route_plan.getSortedRoutes(activity, day): 
            if self.InsertionFound_BetterInsertVisitWitLim == True  or self.betterInsertVisit_explored_branches > max_num_explored_branches: 
                break
            for index_place in range(len(route.route)+1): 
                route_plan = copy.deepcopy(old_route_plan)
    
                if self.InsertionFound_BetterInsertVisitWitLim == False: 
                    self.insertNextActiviy_forBetterInsertion_with_iteration_limitation(next_actitivy, rest_acitivites, route_plan, day, route.employee.id, index_place)
                    if self.InsertionFound_BetterInsertVisitWitLim == True  or self.betterInsertVisit_explored_branches > max_num_explored_branches: 
                        break
                else: 
                    break

             
    def best_insert_visit_on_day(self, visit, day):
        self.InsertionFound_BestInsertVisit = False
        activitiesIds_index = self.constructor.visits_array[0].tolist().index('activitiesIds')
        activitiesList = self.constructor.visits_array[visit][activitiesIds_index]
        test_route_plan = copy.deepcopy(self.route_plan)
        test_route_plan.updateObjective(0, iterations)
        
        activities = [Activity(self.constructor.activities_df, activityID) for activityID in activitiesList]
        activity = activities[0]
        rest_acitivites = activities[1:]
      
        old_route_plan = copy.deepcopy(test_route_plan)
        #TODO: Trenger ikke bruke den SortedRoutes nødvendighvis 
        for route in test_route_plan.getSortedRoutes(activity, day):
            for index_place in range(len(route.route)+1): 
            
                test_route_plan = copy.deepcopy(old_route_plan)

                self.insertNextActiviy_forBestInsertion(activity, rest_acitivites, test_route_plan, day, route.employee.id, index_place)
                    
            
        
        return self.InsertionFound_BestInsertVisit

    '''
    Den må hvordan skal den breake her. Vi får ingen breaks. 

    Den må likevel ha funksjonalitet for å stoppe. For hvis det blir ulovelig, så ønsker vi ikke å utforske videre

    Kanskje den skal ha en status for hvert plan vi er på. 

    Hva er det vi øsnker å fange opp: Dersom den møter på en stopp, så er det ikke vits, å prøve på 
    '''


    def insertNextActiviy_forBestInsertion(self, activity, rest_acitivites, route_plan, day, employeeID, index_place):
        route_plan.updateObjective(0, iterations)
        #TODO: Sammkjøre denne med andre aktiviteter som fungere 
        #BEG: Må ha med denne også for å sjekke om det er 
        route_plan.updateActivityBasedOnRoutePlanOnDay(activity, day)
       
 

        for activitiesWithPossibleNewUpdated in route_plan.routes[day][employeeID].route: 
            route_plan.updateActivityBasedOnRoutePlanOnDay(activitiesWithPossibleNewUpdated, day)

        insertStatus = route_plan.routes[day][employeeID].insertActivityOnIndex(activity, index_place)

      
        if insertStatus == False: 
            return 
        
        if len(rest_acitivites) == 0: 
            route_plan.updateObjective(0, iterations)
         
            if checkCandidateBetterThanBest(route_plan.objective, self.route_plan.objective): 
                self.route_plan = copy.deepcopy(route_plan)
        
            self.InsertionFound_BestInsertVisit = True 
            return 
            
        
        next_actitivy = rest_acitivites[0]
        rest_acitivites = rest_acitivites[1:] 
        
       
        old_route_plan = copy.deepcopy(route_plan)
        for route in route_plan.getSortedRoutes(activity, day): 
            for index_place in range(len(route.route)+1): 
                route_plan = copy.deepcopy(old_route_plan)
    
                self.insertNextActiviy_forBestInsertion(next_actitivy, rest_acitivites, route_plan, day, route.employee.id, index_place)
                    
                

    

    
    '''
    Blir dette et bredde først søk? Nei fordi den søker seg

    Den komme seg ned, finner løsningen. Men på vei opp så må den gjøre alle de andre 
    
    Må ha en form for while, slik at den bare kjører hvis den forrige ikke fill true 
    Begynne på laveste nivå

    Hva skal true returnere. Den setter ruteplanen og den setter den globale verdien, så vi trenger ikke ha de andre true/false lenger? 

    Må ha en eller annen global variabel som sier om vi har funnet dette punktet 


    Teste med å printe hvert steg når en aktivitet legges til. 

    Videre arbeid: 
    Dette er ikke en best insertion. 
    Hvordan skulle man laget best insertion: Kan bruke mye av det samme som nå, bare at man endrer til at den går gjennom alle muligheter, og velger den som gir best resultat. 
    Jeg er veldig usikker på hvor lang tid det tar å kjøre disse insertionene.
    '''