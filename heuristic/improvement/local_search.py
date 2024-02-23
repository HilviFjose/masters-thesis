from objects.route_plan import RoutePlan
from helpfunctions import *
import copy
import numpy as np 

#TODO: Tenke mer over hvike operatorer vi har innad på en dag i vår struktur. 
#Det må være noen operatorer for alle typer aktiviteter.

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
        #TODO: Finne ut om det er noe teori på hva som burd være først 
        candidate = self.candidate
        for day in range(1, self.candidate.days + 1):
           candidate = self.change_employee(candidate,day)
        for day in range(1, self.candidate.days + 1):
            candidate = self.change_employee(candidate,day)
        print("NY LØSNING ETTER FØRSTE LOKALSØK")
        candidate.printSolution()
        candidate.updateObjective()
        print("Objective", candidate.objective)
        for day in range(1, self.candidate.days + 1):
            for route in candidate.routes[day]:
                #Denne returnerer ikkke riktig nye ruteplan
                new_route = self.swap_activities_in_route(copy.deepcopy(route))
                candidate = self.switchRoute(candidate, new_route, day)
        candidate.updateObjective()
        return candidate
    
    def switchRoute(self, candidate, new_route,  day):
        for org_route in candidate.routes[day]: 
            if org_route.employee.id == new_route.employee.id: 
               
                candidate.routes[day].remove(org_route)
                
                candidate.routes[day].append(new_route)
               
        return candidate
    '''
    Hva er forskjellen på denne og den over.
    Der sender vi inn candidaten, også blir den 
    Den gjør ingen av swapene i ruten. 
    Men den oppdaterer kjøretiden til det siste objektivet 
    '''
    
    def swap_activities_in_route(self, route):
        #TODO: Legge inn sånn at den oppdaterer tidsvinduverdiene basert på hvor de andre ligger
        #Lager ikke gyldige løsninger nå 
       
        route.updateObjective()
        best_travel_time = route.travel_time
        old_objective = best_travel_time
        best_found_route = route
    
        #Den fungerer nå for de uten presedens. Sjekke med
        for activity1 in route.route:
            for activity2 in route.route: 
                if activity1.id >= activity2.id: 
                    continue
                #TODO: Jeg forstår ikke hvorfor denne printen kommer to ganger. Finne ut  
                #print("Prøver å bytte aktivitet", activity1.id, activity2.id, "DAY", route.day, "emp", route.employee.id)
                
                NextDependentActivitiyIDs = []
                for elem in (activity1.NextNodeInTime + activity2.NextNodeInTime): 
                    NextDependentActivitiyIDs.append(elem[0])
                NextDependentActivitiyIDs = activity1.NextNode +  activity2.NextNode 
                new_route = copy.deepcopy(route)
                NextDependentActivityList = []
                for nextActID in NextDependentActivitiyIDs: 
                    if new_route.getActivity(nextActID) != None: 
                        NextDependentActivitiyIDs.append(new_route.getActivity(nextActID))
                    new_route.removeActivity(nextActID)
                index_count = 0
                index_act1 = 0 
                index_act2 = 0 
                for act in new_route.route:
                    if act.getID() == activity1.getID():
                        index_act1 = index_count
                    if act.getID() == activity2.getID():
                        index_act2 = index_count
                    index_count += 1

            
                '''
                Må sortere de, den som skal settes inn på den laveste indeksen kan settes inn på indeksen
                Den som har høyest innsetting indeks plasseres først
                Deretter plasseres den andre, men dersom den skal settes inn bakerst i listen så må den bare appendes

                '''

                 
                new_route.removeActivity(activity1.getID())
                new_route.removeActivity(activity2.getID())
                
                activity1_new = copy.deepcopy(activity1)
                activity2_new = copy.deepcopy(activity2)

                if index_act1 < index_act2:
                    if activity1_new.id == 44 and activity2_new.id == 47: 
                        print("kommerhit 0- feil") 
                    status = new_route.insertOnIndex(activity2_new, index_act1)
                    if status == False: 
                        continue

                    status = new_route.insertOnIndex(activity1_new, index_act2)
                    if status == False: 
                        continue
                
                else: 
                    if activity1_new.id == 44 and activity2_new.id == 74: 
                        print("kommerhit 0")
                    status = new_route.insertOnIndex(activity1_new, index_act2)
                    if status == False: 
                        continue
                    if activity1_new.id == 44 and activity2_new.id == 74: 
                        print("kommerhit 1")

                    status = new_route.insertOnIndex( activity2_new, index_act1)
                    if status == False: 
                        continue
                    if activity1_new.id == 44 and activity2_new.id == 74: 
                        print("kommerhit 2")
         
                
                
                
                if activity1_new.id == 44 and activity2_new.id == 74: 
                    print("NextDependentActivityList", NextDependentActivityList)
                for nextAct in NextDependentActivityList: 
                    status = new_route.addActivity(new_route.getActivity(nextAct))
                    if status == False: 
                        continue
                if activity1_new.id == 44 and activity2_new.id == 74: 
                    print("kommerhit 3")
                #Status er true hvis vi fikk lagt til alle, og false hvis ikke
                #TODO: Det blir ikke riktgi 

                new_route.updateObjective()
                if activity1_new.id == 44 and activity2_new.id == 74: 
                    print("kommerhit 4")
                    print("changed objective old", old_objective, "new objective", new_route.travel_time)
                
                if status == True and new_route.travel_time < best_travel_time:
                    best_travel_time = new_route.travel_time
                    best_found_route = copy.deepcopy(new_route) 
                    print("swap is done", activity1.id, activity2.id)
                    print("changed objective old", old_objective, "new objective", best_travel_time)
                    print("--------------------")
        return best_found_route
  


    def move_activity_in_route(self):
        '''
        Presedens: Hvis denne skal flyttes så må de andre aktivitenene i ruten også flyttes 
        IkkePresdens: Kan flytte på grunn av 

        Bytter ikke ansatt de er i, bare tidspunkt det skjer på

        
        '''
        return self.candidate

    def swap_employee(self, route_plan, day):
        '''
            Skal iterere over alle parr av aktiviteter som skjer på en gitt dag
            Dersom de ikke er i samme rute skal de forsøkes byttes plass på. 
            Henter altså ut ruten og indeksen og forsøker å legge de til der. 
            Dersom begge returnerer true, så har vi en ny løsning 
        '''
    

    
    def change_employee(self, route_plan, day):
        #TODO: Løsningen blir ikke så mye bedre, det er flere grunner til det, se under
        '''
        - Umulig å flytte parr med noder som har same employee activity, fordi det at den ene er fastlåst gjør at den andre ikke kan flyttes
        - Du får bare gjøre et flytt, så det er ikke så rart at utslaget er lavt.
        - ?Synes det er litt rart at vi bare gjør et flytt
        '''
        #TODO: Er rart å bare gjøre flytt på en dag? Skal den heller gjøres på dagsbasis
        #Slik at at alle dager får bedre objektivverdi? 
        best_objective = route_plan.getObjective()
      
        best_found_candidate = route_plan
        
        for route in route_plan.routes[day]: 
            for activity in route.route:
                employee = route_plan.getEmployeeAllocatedForActivity(activity.getID(), day)
                otherEmployees = route_plan.getOtherEmplOnDay(employee, day)
                for othEmpl in otherEmployees: 
                    new_candidate = copy.deepcopy(route_plan)
                    new_candidate.removeActivityFromEmployeeOnDay(employee, activity, day)
        #rETTSKRIVING
                    status = new_candidate.insertActivityInEmployeesRoute(othEmpl, activity, day)
                    new_candidate.updateObjective()
                    if status == False: 
                        break
                    #TODO: Kann hende man i alle insert functinene skal kjøre insert objective 
                    
                    if checkCandidateBetterThanCurrent( new_candidate.objective, best_objective ):
                        best_objective = new_candidate.objective
                        best_found_candidate = new_candidate 
        return best_found_candidate
        
    


                                        
