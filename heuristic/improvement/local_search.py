from objects.route_plan import RoutePlan
from helpfunctions import *
import copy

#TODO: Tenke mer over hvike operatorer vi har innad på en dag i vår struktur. 
#Det må være noen operatorer for alle typer aktiviteter.

class LocalSearch:
    def __init__(self, candidate): 
        #Får inn en kandidatløsning som er et route_plan objekt 
        self.candidate = candidate
        self.candidate.updateObjective()
     
    
    def do_local_search(self):
        new_candidate = self.change_employee(self.candidate)
        return new_candidate
    
    def swap_activities_in_route(self):
        return self.candidate

    def move_activity_in_route(self):
        return self.candidate

    def swap_employee(self, route_plan, day):
        '''
            Skal iterere over alle parr av aktiviteter som skjer på en gitt dag
            Dersom de ikke er i samme rute skal de forsøkes byttes plass på. 
            Henter altså ut ruten og indeksen og forsøker å legge de til der. 
            Dersom begge returnerer true, så har vi en ny løsning 
        '''
    

    
    def change_employee(self, route_plan):
        #TODO: Løsningen blir ikke så mye bedre, det er flere grunner til det, se under
        '''
        - Umulig å flytte parr med noder som har same employee activity, fordi det at den ene er fastlåst gjør at den andre ikke kan flyttes
        - Du får bare gjøre et flytt, så det er ikke så rart at utslaget er lavt.
        - ?Synes det er litt rart at vi bare gjør et flytt
        '''
        #TODO: Er rart å bare gjøre flytt på en dag? Skal den heller gjøres på dagsbasis
        #Slik at at alle dager får bedre objektivverdi? 
        best_objective = route_plan.objective
        org_route_plan = route_plan
        best_found_candidate= None
        for day in range(1, route_plan.days + 1):
            for route in route_plan.routes[day]: 
                for activity in route.route:
                    employee = route_plan.getEmployeeAllocatedForActivity(activity.getID(), day)
                    otherEmployees = route_plan.getOtherEmplOnDay(employee, day)
                    for othEmpl in otherEmployees: 
                        new_candidate = copy.deepcopy(org_route_plan)
                        new_candidate.removeActivityFromEmployeeOnDay(employee, activity, day)
           
                        status = new_candidate.insertAcitivyInEmployeesRoute(othEmpl, activity, day)
                        new_candidate.updateObjective()
                        if status == False: 
                            break
                        #TODO: Kann hende man i alle insert functinene skal kjøre insert objective 
                        
                        if checkCandidateBetterThanCurrent( new_candidate.objective, best_objective ):
                            best_objective = new_candidate.objective
                            best_found_candidate = new_candidate 
        if best_found_candidate != org_route_plan:
            return best_found_candidate
        return route_plan
    


                                        
