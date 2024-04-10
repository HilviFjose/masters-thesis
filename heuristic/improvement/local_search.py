from objects.route_plan import RoutePlan
from helpfunctions import *
import copy
import numpy as np 

#TODO: Tenke mer over hvike operatorer vi har innad på en dag i vår struktur. 
#Det må være noen operatorer for alle typer aktiviteter.

#TODO: Skal vi ha 
'''
Skal man ved hjelp av disse operatorene kunne komme til optimal løsning? 
'''

#TODO: Se på om vi skal gjøre de samme operatorene på visit nivå.  Hensyntar ikke at vi har dependensies mellom ruter.

class LocalSearch:
    def __init__(self, candidate): 
        #Får inn en kandidatløsning som er et route_plan objekt 
        self.candidate = candidate
        self.candidate.updateObjective()
     
    
    def do_local_search(self):
        # TODO: Finne ut om det er noe teori på hva som burd være først 
        candidate = copy.deepcopy(self.candidate)

        
        # CHANGE EMPLOYEE
        for day in range(1, self.candidate.days + 1):
           candidate = self.change_employee(candidate,day)
        for day in range(1, self.candidate.days + 1):
           candidate = self.change_employee(candidate,day)
        #print("NY LØSNING ETTER CHANGE EMPLOYEE LOKALSØK")
        #candidate.printSolution()
        
        
        # SWAP EMPLOYEE
        for day in range(1, self.candidate.days + 1):
           candidate = self.swap_employee(candidate, day)
        for day in range(1, self.candidate.days + 1):
            candidate = self.swap_employee(candidate,day)
        #print("NY LØSNING ETTER SWAP EMPLOYEE LOKALSØK")
        #candidate.printSolution()
        

        # MOVE ACTIVITY
        for day in range(1, self.candidate.days + 1):
            for route in candidate.routes[day]:
                new_route = self.move_activity_in_route(copy.deepcopy(route))
                candidate.switchRoute(new_route, day)
        for day in range(1, self.candidate.days + 1):
            for route in candidate.routes[day]:
                new_route = self.move_activity_in_route(copy.deepcopy(route))
                candidate.switchRoute(new_route, day)
        #print("NY LØSNING ETTER MOVE ACTIVITY LOKALSØK")
        #candidate.printSolution()
        

        # SWAP ACTIVITY
        for day in range(1, self.candidate.days + 1):
            for route in candidate.routes[day]:
                new_route = self.swap_activities_in_route(copy.deepcopy(route))
                candidate.switchRoute(new_route, day)
        for day in range(1, self.candidate.days + 1):
            for route in candidate.routes[day]:
                new_route = self.swap_activities_in_route(copy.deepcopy(route))
                candidate.switchRoute(new_route, day)
        #print("NY LØSNING ETTER SWAP ACTIVITIES LOKALSØK")
        #candidate.printSolution()
        
        return candidate
    
   
 
    
    def swap_activities_in_route(self, route):
        #TODO: Sjekke litt mer nøye hvordan det er med dependencies. Kanskje den ikke fungerer for det. Fungerer forenkeltstående
        route.updateObjective()
        best_travel_time = route.travel_time
        old_objective = best_travel_time
        best_found_route = route
    
        for activity1 in route.route:
            for activity2 in route.route: 
                if activity1.id >= activity2.id: 
                    continue
                
                NextDependentActivitiyIDs = []
                for elem in (activity1.NextNodeInTime + activity2.NextNodeInTime): 
                    NextDependentActivitiyIDs.append(elem[0])
                NextDependentActivitiyIDs = activity1.NextNode +  activity2.NextNode 
                new_route = copy.deepcopy(route)
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

                
                information_candidate = copy.deepcopy(self.candidate)


                if index_act1 < index_act2:
                    status = new_route.insertActivityOnIndex(activity2_new, index_act1)
                    if status == False: 
                        continue

                    information_candidate.switchRoute(new_route, new_route.day)
                    #Lagt inn restart uten å sjekke
                    
                    information_candidate.updateActivityBasedOnRoutePlanOnDay(activity1_new, route.day)
                    status = new_route.insertActivityOnIndex(activity1_new, index_act2)
                    if status == False: 
                        continue
                
                else: 
                    status = new_route.insertActivityOnIndex(activity1_new, index_act2)
                    if status == False: 
                        continue

                    information_candidate.switchRoute(new_route, new_route.day)
                    
                    information_candidate.updateActivityBasedOnRoutePlanOnDay(activity2_new, route.day)
                    status = new_route.insertActivityOnIndex( activity2_new, index_act1)
                    if status == False: 
                        continue
       
                for nextAct in NextDependentActivityList: 
                    information_candidate.switchRoute(new_route, new_route.day)
                    
                    information_candidate.updateActivityBasedOnRoutePlanOnDay(nextAct, route.day)
                    status = new_route.addActivity(nextAct)
                    if status == False: 
                        continue
                new_route.updateObjective()
            
                if status == True and new_route.travel_time < best_travel_time:
                    best_travel_time = new_route.travel_time
                    best_found_route = copy.deepcopy(new_route) 
                    #print("swap is done", activity1.id, activity2.id)
                    #print("changed objective old", old_objective, "new objective", best_travel_time)
                    #print("--------------------")
        return best_found_route
  


# TODO: Tenke over at in time tidsvinduer ikke tas hensyn til av aktiviteten mellom de to som har det.
    '''
    Her må vi tenke på når vi gjør hvilke oppdateringer av tidsbegresninger 
    Nå jobber vi med ruteobjekter, ønsker derfor ikke å kalle updatebasedonrouteplan inne i 
    '''
    def move_activity_in_route(self, route):
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

            for index in range(len(new_route.route)+1):
                newer_route = copy.deepcopy(new_route)
                #information_candidate = copy.deepcopy(self.candidate)
                #information_candidate.switchRoute(newer_route, newer_route.day)
                if index == index_act:
                    continue

                #ACTIVITY NY MÅ ENDRES FOR DEN ER IKKE LENGE RBUNDET AV KRAVENE TIL DE ANDRE AKTIVITENE I RUTEN
                newer_route.updateActivityBasedOnDependenciesInRoute(activity_new)
                status = newer_route.insertActivityOnIndex(activity_new, index)
                if status == False:
                    continue

                for nextAct in NextDependentActivitiyList:
                    #nextAct.restartActivity()
                    #TODO: Muligens endre under
                    #information_candidate.updateActivityBasedOnRoutePlanOnDay(nextAct, route.day)
                    #NEXT ACT MÅ OPPDATERES FORDI DET HAR SKJEDD ENRINGER
                    newer_route.updateActivityBasedOnDependenciesInRoute(nextAct)
                    status = newer_route.addActivity(nextAct)
                    if status == False: 
                        break
                newer_route.updateObjective()

                if status == True and newer_route.travel_time < best_travel_time:
                    best_travel_time = newer_route.travel_time
                    best_found_route = copy.deepcopy(newer_route) 
                    #print("move is done", activity.id)
        return best_found_route

    def swap_employee(self, route_plan, day):
        route_plan.updateObjective()
        best_objective = route_plan.getObjective()
        best_found_candidate = route_plan

        for route1 in route_plan.routes[day]: 
            for route2 in route_plan.routes[day]: 
                if route1.employee.id >= route2.employee.id: 
                    continue
                for activity1 in route1.route: 
                    for activity2 in route2.route: 
                        
                        
                        new_route1 = copy.deepcopy(route1)
                        new_route2 = copy.deepcopy(route2)

                        new_route1.removeActivityID(activity1.id)
                        new_route2.removeActivityID(activity2.id)
                        
                        #TODO: Nå sendes routeplan inn her. har ikke sjekket premissene. Var ikke med før
                        for routeActivity in new_route1.route: 
                            route_plan.updateActivityBasedOnRoutePlanOnDay(routeActivity, day)
                        route_plan.updateActivityBasedOnRoutePlanOnDay(activity2, day)
                        state = new_route1.addActivity(activity2)
                        if state == False: 
                            continue
              
                        for routeActivity in new_route2.route: 
                            route_plan.updateActivityBasedOnRoutePlanOnDay(routeActivity, day)
                        route_plan.updateActivityBasedOnRoutePlanOnDay(activity1, day)
                        state = new_route2.addActivity(activity1)
                        if state == False: 
                            continue
                  
                        
                        
                        new_candidate = copy.deepcopy(route_plan) 
                        new_candidate.switchRoute(new_route1, day)
                        new_candidate.switchRoute(new_route2, day)
                        new_candidate.updateObjective()
                       
                            
                        
                        if checkCandidateBetterThanBest( new_candidate.objective, best_objective ):
                            best_objective = new_candidate.objective
                            best_found_candidate = new_candidate 
                            #print( "bytter plass på aktivitet ", activity1.id, activity2.id)
                            #print("new_candidate.objective", new_candidate.objective)
        return best_found_candidate

    

    def change_employee(self, route_plan, day):
        #TODO: Legge inn comdition som i swap_activity. Dersom del av pickup&delivery par, tas andre halvdel ut og plasseres inn igjen.
        
        
      
        best_found_candidate = copy.deepcopy(route_plan)
        
        for route in route_plan.routes[day]: 
            
            for activity in route.route:

                employee = route_plan.getEmployeeIDAllocatedForActivity(activity, day)
                otherEmployees = route_plan.getListOtherEmplIDsOnDay(activity.id, day)
                sameEmployeeActivity = route_plan.getActivity(activity.pickUpActivityID, day)

                for othEmpl in otherEmployees: 
                    new_candidate = copy.deepcopy(route_plan)
                    new_candidate.removeActivityFromEmployeeOnDay(employee, activity, day)
                    if sameEmployeeActivity != None: 
                        new_candidate.removeActivityFromEmployeeOnDay(employee, sameEmployeeActivity, day)

                    status = new_candidate.insertActivityInEmployeesRoute(othEmpl, activity, day)
                    if status == False: 
                        break
                  
                    #Legger til sameEmployee aktiviteten 
                    if sameEmployeeActivity != None: 
                        status = new_candidate.insertActivityInEmployeesRoute(othEmpl, sameEmployeeActivity, day)
                        if status == False: 
                            break
                  
                    new_candidate.updateObjective()
                    
                    if checkCandidateBetterThanBest(new_candidate.objective, best_found_candidate.objective ):
                        best_found_candidate = new_candidate 
        return best_found_candidate
        
    


                                        
