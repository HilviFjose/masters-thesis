#from objects.route_plan import RoutePlan
from helpfunctions import *
import copy
#import numpy as np 

#TODO: Tenke mer over hvike operatorer vi har innad på en dag i vår struktur. 
#Det må være noen operatorer for alle typer aktiviteter.


'''
Har gjort en test på rekkefølgen på operatorene i lokalsøket til optimum. 
Fikk ikke så mye indikasjoner på hva som er best rekkefølge, så tenker vi kan argumentere for den som står der nå
'''



class LocalSearch:
    def __init__(self, candidate, current_iteration, total_iterations): 
        #Får inn en kandidatløsning som er et route_plan objekt 
        self.candidate = candidate
        self.days = self.candidate.days
        self.current_iteration = current_iteration
        self.total_iterations = total_iterations
        self.candidate.updateObjective(current_iteration, total_iterations)
     
    
    def do_local_search_to_local_optimum(self):
        candidate = copy.deepcopy(self.candidate)
        last_objective = copy.copy(candidate.objective)
        iteration = 0 
         
        # CHANGE EMPLOYEE
        while checkCandidateBetterThanBest(candidate.objective, last_objective) or iteration == 0: 
            iteration += 1
            last_objective = copy.copy(candidate.objective)
            for day in range(1, self.days + 1):
                candidate = self.change_employee(candidate, day)
        iteration = 0

        # SWAP EMPLOYEE
        while checkCandidateBetterThanBest(candidate.objective, last_objective) or iteration == 0: 
            last_objective = copy.copy(candidate.objective)
            iteration += 1
            for day in range(1, self.days + 1):
                candidate = self.swap_employee(candidate, day)
        iteration = 0

        
        # SWAP ACTIVITY 
        while checkCandidateBetterThanBest(candidate.objective, last_objective) or iteration == 0: 
            last_objective = copy.copy(candidate.objective)
            iteration += 1
            for day in range(1, self.days + 1):
                employeeOnDayList = [route.employee.id for route in candidate.routes[day].values()]
                for emplID in employeeOnDayList: 
                    new_route = self.swap_activities_in_route(copy.deepcopy(candidate.routes[day][emplID]), candidate)
                    candidate.insertNewRouteOnDay(new_route, day)
                    candidate.updateObjective(self.current_iteration, self.total_iterations)

        iteration = 0 
        
        # MOVE ACTIVITY
        while checkCandidateBetterThanBest(candidate.objective, last_objective) or iteration == 0: 
            last_objective = copy.copy(candidate.objective)
            iteration += 1
            for day in range(1, self.days + 1):
                employeeOnDayList = [route.employee.id for route in candidate.routes[day].values()]
                for emplID in employeeOnDayList: 
                    new_route = self.move_activity_in_route(copy.deepcopy(candidate.routes[day][emplID]), candidate)
                    candidate.insertNewRouteOnDay(new_route, day)
                    candidate.updateObjective(self.current_iteration, self.total_iterations)
        iteration = 0

        return candidate


    def do_local_search(self):
        candidate = copy.deepcopy(self.candidate)
        
        # CHANGE EMPLOYEE
        for day in range(1, self.days + 1):
            candidate = self.change_employee(candidate, day)
        for day in range(1, self.days + 1):
           candidate = self.change_employee(candidate, day)

        candidate.printSolution("candidate_after_initial_local_search_after_change_empl", "ingen operator")

        
        # SWAP EMPLOYEE
        for day in range(1, self.days + 1):
           candidate = self.swap_employee(candidate, day)
        for day in range(1, self.days + 1):
            candidate = self.swap_employee(candidate, day)

        candidate.printSolution("candidate_after_initial_local_search_after_swap_empl", "ingen operator")

        # MOVE ACTIVITY
        for day in range(1, self.days + 1):
            employeeOnDayList = [route.employee.id for route in candidate.routes[day].values()]
            for emplID in employeeOnDayList: 
                new_route = self.move_activity_in_route(copy.deepcopy(candidate.routes[day][emplID]), candidate)
                candidate.insertNewRouteOnDay(new_route, day)
        for day in range(1, self.days + 1):
            employeeOnDayList = [route.employee.id for route in candidate.routes[day].values()]
            for emplID in employeeOnDayList: 
                new_route = self.move_activity_in_route(copy.deepcopy(candidate.routes[day][emplID]), candidate)
                candidate.insertNewRouteOnDay(new_route, day)

        candidate.printSolution("candidate_after_initial_local_search_after_ma", "ingen operator")


        # SWAP ACTIVITY 
        for day in range(1, self.days + 1):
            employeeOnDayList = [route.employee.id for route in candidate.routes[day].values()]
            for emplID in employeeOnDayList: 
                new_route = self.swap_activities_in_route(copy.deepcopy(candidate.routes[day][emplID]), candidate)
                candidate.insertNewRouteOnDay(new_route, day)
        for day in range(1, self.days + 1):
            employeeOnDayList = [route.employee.id for route in candidate.routes[day].values()]
            for emplID in employeeOnDayList: 
                new_route = self.swap_activities_in_route(copy.deepcopy(candidate.routes[day][emplID]), candidate)
                candidate.insertNewRouteOnDay(new_route, day)
        
        candidate.printSolution("candidate_after_initial_local_search_after_sa", "ingen operator")

        return candidate
    
    def do_local_search_on_day(self, day):
        candidate = copy.deepcopy(self.candidate)
        
        #CHANGE EMPLOYEE
        candidate = self.change_employee(candidate, day)
        candidate = self.change_employee(candidate, day)
        
        # SWAP EMPLOYEE
        candidate = self.swap_employee(candidate, day)
        candidate = self.swap_employee(candidate, day)

        # MOVE ACTIVITY
        
        employeeOnDayList = [route.employee.id for route in candidate.routes[day].values()]
        for emplID in employeeOnDayList: 
            new_route = self.move_activity_in_route(copy.deepcopy(candidate.routes[day][emplID]), candidate)
            candidate.insertNewRouteOnDay(new_route, day)
    
        employeeOnDayList = [route.employee.id for route in candidate.routes[day].values()]
        for emplID in employeeOnDayList: 
            new_route = self.move_activity_in_route(copy.deepcopy(candidate.routes[day][emplID]), candidate)
            candidate.insertNewRouteOnDay(new_route, day)

        # SWAP ACTIVITY 
        employeeOnDayList = [route.employee.id for route in candidate.routes[day].values()]
        for emplID in employeeOnDayList: 
            new_route = self.swap_activities_in_route(copy.deepcopy(candidate.routes[day][emplID]), candidate)
            candidate.insertNewRouteOnDay(new_route, day)
    
        employeeOnDayList = [route.employee.id for route in candidate.routes[day].values()]
        for emplID in employeeOnDayList: 
            new_route = self.swap_activities_in_route(copy.deepcopy(candidate.routes[day][emplID]), candidate)
            candidate.insertNewRouteOnDay(new_route, day)

        return candidate
 
    
   
 
    
    def swap_activities_in_route(self, route, candidate):
        #TODO: Sjekke litt mer nøye hvordan det er med dependencies. Kanskje den ikke fungerer for det. Fungerer forenkeltstående
        information_candidate = candidate
        candidate.updateObjective(self.current_iteration, self.total_iterations)
        route.updateObjective()
        best_travel_time = route.travel_time
        best_found_route = route
    
        for activity1 in route.route:
            for activity2 in route.route: 
                if activity1.id >= activity2.id: 
                    continue

                new_route = copy.deepcopy(route)

                NextDependentActivitiyIDs = []
                for elem in (activity1.NextNodeInTime + activity2.NextNodeInTime): 
                    NextDependentActivitiyIDs.append(elem[0])
                NextDependentActivitiyIDs = activity1.NextNode +  activity2.NextNode 

                NextDependentActivityList = []
                for nextActID in NextDependentActivitiyIDs: 
                    if new_route.getActivity(nextActID) != None: 
                        NextDependentActivityList.append(new_route.getActivity(nextActID))
                    new_route.removeActivityID(nextActID)

                index_count = 0
                index_act1 = 0 
                index_act2 = 0 
                for act in new_route.route:
                    if act.id == activity1.id:
                        index_act1 = index_count
                    if act.id == activity2.id:
                        index_act2 = index_count
                    index_count += 1
        
                new_route.removeActivityID(activity1.id)
                new_route.removeActivityID(activity2.id)
                activity1_new = copy.deepcopy(activity1)
                activity2_new = copy.deepcopy(activity2)

                #TESTLEGGER TIL 
                for testAct in new_route.route: 
                    information_candidate.updateActivityBasedOnRoutePlanOnDay(testAct, new_route.day)
                    new_route.updateActivityBasedOnDependenciesInRoute(testAct)

                if index_act1 < index_act2:
                    
                    information_candidate.updateActivityBasedOnRoutePlanOnDay(activity2_new, route.day)
                    status = new_route.insertActivityOnIndex(activity2_new, index_act1)
                    if status == False: 
                        continue

                    information_candidate.insertNewRouteOnDay(new_route, new_route.day)
                    information_candidate.updateActivityBasedOnRoutePlanOnDay(activity1_new, route.day)
                    status = new_route.insertActivityOnIndex(activity1_new, index_act2)
                    if status == False: 
                        continue
            
                else: 
                    information_candidate.updateActivityBasedOnRoutePlanOnDay(activity1_new, route.day)
                    status = new_route.insertActivityOnIndex(activity1_new, index_act2)
                    if status == False: 
                        continue

                    information_candidate.insertNewRouteOnDay(new_route, new_route.day)
                    information_candidate.updateActivityBasedOnRoutePlanOnDay(activity2_new, route.day)
                    status = new_route.insertActivityOnIndex( activity2_new, index_act1)
                    if status == False: 
                        continue
       
                        
                for nextAct in NextDependentActivityList: 
                    information_candidate.insertNewRouteOnDay(new_route, new_route.day)
                    information_candidate.updateActivityBasedOnRoutePlanOnDay(nextAct, route.day)
                    status = new_route.addActivity(nextAct)
                    if status == False: 
                        break

                new_route.updateObjective()
                
                if status == True and new_route.travel_time < best_travel_time:
                    best_travel_time = new_route.travel_time
                    best_found_route = copy.deepcopy(new_route) 

        return best_found_route
  

    def move_activity_in_route(self, route, candidate):
        information_candidate = candidate
        candidate.updateObjective(self.current_iteration, self.total_iterations)
        route.updateObjective()
        best_travel_time = route.travel_time
        best_found_route = route
    
    
        for activity in route.route:
            NextDependentActivitiyIDs = activity.NextNode
            for elem in (activity.NextNodeInTime): 
                NextDependentActivitiyIDs.append(elem[0])
            
            new_route = copy.deepcopy(route)

            NextDependentActivitiyList = []
            for nextActID in NextDependentActivitiyIDs: 
                if new_route.getActivity(nextActID) != None: 
                    NextDependentActivitiyList.append(new_route.getActivity(nextActID))
                new_route.removeActivityID(nextActID)

            index_count = 0
            index_act = 0 
            for act in new_route.route:
                if act.id == activity.id:
                    index_act = index_count
                index_count += 1
    
            new_route.removeActivityID(activity.id)
            activity_new = copy.deepcopy(activity)

            information_candidate.updateActivityBasedOnRoutePlanOnDay(activity_new, new_route.day)
            for nextAct in NextDependentActivitiyList:
                information_candidate.updateActivityBasedOnRoutePlanOnDay(nextAct, new_route.day)

            for index in range(len(new_route.route)+1):
                newer_route = copy.deepcopy(new_route)
                if index == index_act:
                    continue

                #TESTLEGGER TIL 
                for testAct in newer_route.route: 
                    information_candidate.updateActivityBasedOnRoutePlanOnDay(testAct, newer_route.day)
                    newer_route.updateActivityBasedOnDependenciesInRoute(testAct)

                #newer_route.updateActivityBasedOnDependenciesInRoute(activity_new)
                status = newer_route.insertActivityOnIndex(activity_new, index)
                if status == False:
                    continue

                for nextAct in NextDependentActivitiyList:
                    newer_route.updateActivityBasedOnDependenciesInRoute(nextAct)
                    status = newer_route.addActivity(nextAct)
                    if status == False: 
                        break

                newer_route.updateObjective()
                if status == True and newer_route.travel_time < best_travel_time:
                    best_travel_time = newer_route.travel_time
                    best_found_route = copy.deepcopy(newer_route) 
       
        return best_found_route
    

    '''
    Her skal det være en eller annen feil, det er i denne funksjonen. 
    '''
    def swap_employee(self, route_plan, day):
        route_plan.updateObjective(self.current_iteration, self.total_iterations)
        best_objective = route_plan.objective
        best_found_candidate = route_plan

        for route1 in route_plan.routes[day].values(): 
            for route2 in route_plan.routes[day].values(): 
                if route1.employee.id >= route2.employee.id: 
                    continue
                for activity1 in route1.route: 
                    for activity2 in route2.route: 
                        new_candidate = copy.deepcopy(route_plan)

                        #Kunne muligens bare hentet rutene fra new candidiate. 
                        new_route1 = new_candidate.routes[day][route1.employee.id]
                        new_route2 = new_candidate.routes[day][route2.employee.id]

                        new_route1.removeActivityID(activity1.id)
                        new_route2.removeActivityID(activity2.id)
                        
                        
                        #Oppdaterer grenser for alle aktiviteter som er i rute 1 
                        for testAct in new_route1.route: 
                            new_candidate.updateActivityBasedOnRoutePlanOnDay(testAct, new_route1.day)
                            #new_route1.updateActivityBasedOnDependenciesInRoute(testAct)

                        new_candidate.updateActivityBasedOnRoutePlanOnDay(activity2, day)
                        status = new_route1.addActivity(activity2)
                        if status == False: 
                            continue

                        
                        #TESTLEGGER TIL 
                        for testAct in new_route2.route: 
                            new_candidate.updateActivityBasedOnRoutePlanOnDay(testAct, new_route2.day)
                        #TODO: Nå sendes routeplan inn her. har ikke sjekket premissene. Var ikke med før
                        new_candidate.updateActivityBasedOnRoutePlanOnDay(activity1, day)
                        status = new_route2.addActivity(activity1)
                        if status == False: 
                            continue
                  
                         
                        new_candidate.insertNewRouteOnDay(new_route1, day)
                        new_candidate.insertNewRouteOnDay(new_route2, day)
                        new_candidate.updateObjective(self.current_iteration, self.total_iterations)
                       
                        if checkCandidateBetterThanBest( new_candidate.objective, best_objective ):
                            best_objective = new_candidate.objective
                            best_found_candidate = new_candidate 
        return best_found_candidate
    

    

    def change_employee(self, route_plan, day):
        #TODO: Legge inn comdition som i swap_activity. Dersom del av pickup&delivery par, tas andre halvdel ut og plasseres inn igjen.
        best_found_candidate = copy.deepcopy(route_plan)
        
        for route in route_plan.routes[day].values(): 
            
            for activity in route.route:

                employee = route_plan.getEmployeeIDAllocatedForActivity(activity, day)
                otherEmployees = route_plan.getListOtherEmplIDsOnDay(activity.id, day)
                sameEmployeeActivity = route_plan.getActivity(activity.pickUpActivityID, day)

                for othEmpl in otherEmployees: 
                    new_candidate = copy.deepcopy(route_plan)
                    new_candidate.removeActivityFromEmployeeOnDay(employee, activity, day)
                    if sameEmployeeActivity != None: 
                        new_candidate.removeActivityFromEmployeeOnDay(employee, sameEmployeeActivity, day)

                     #TESTLEGGER TIL 
                    for testAct in new_candidate.routes[day][othEmpl].route: 
                        new_candidate.updateActivityBasedOnRoutePlanOnDay(testAct, new_candidate.routes[day][othEmpl].day)
                        #TODO: Sjønner ikke hvorfor vi kjører denne? Burde være håndtert i linjen over
                        new_candidate.routes[day][othEmpl].updateActivityBasedOnDependenciesInRoute(testAct)
                      
                    
                    status = new_candidate.insertActivityInEmployeesRoute(othEmpl, activity, day)
                    if status == False: 
                        continue
                  
                    if sameEmployeeActivity != None: 
                        status = new_candidate.insertActivityInEmployeesRoute(othEmpl, sameEmployeeActivity, day)
                        if status == False: 
                            continue
                  
                    new_candidate.updateObjective(self.current_iteration, self.total_iterations)
                    
                    if checkCandidateBetterThanBest(new_candidate.objective, best_found_candidate.objective ):
                        best_found_candidate = new_candidate 
        
        return best_found_candidate
        
    '''
    Informasjonsflyt mellom aktivitetene innad i rute, skal håndteres av insettingsfunksjonene
    Informasjonsflyt mellom aktiviteter med dependencies i ulike ruter, skal håndteres på forhånd

    Det vi har gjort 12.04:
    Lagt til oppdatering av aktivitene som kan bli flyttet når du lager plass med MakeSpace
    Tror dette løste problemet man får med presedens etter lokalsøk

    '''



                                        
