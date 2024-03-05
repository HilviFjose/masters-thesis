import pandas as pd
import copy
import math
import numpy.random as rnd 

import os
import sys
sys.path.append( os.path.join(os.path.split(__file__)[0],'..','..','..'))  # Include subfolders

from helpfunctions import checkCandidateBetterThanCurrent
from objects.distances import *
from config.construction_config import *
from heuristic.improvement.operator.repair_generator import RepairGenerator

class Operators:
    def __init__(self, alns):
        self.destruction_degree = alns.destruction_degree # TODO: Skal vi ha dette?
        self.constructor = alns.constructor
        self.repair_generator = RepairGenerator(self.constructor)

    # Uses destruction degree to set max cap for removal
    def activities_to_remove(self, activities_remove):
        return activities_remove
    
#---------- REMOVE OPERATORS ----------
    """
   
    def random_route_removal(self, current_route_plan):
        destroyed_route_plan = copy.deepcopy(current_route_plan)
        routes = destroyed_route_plan.routes

        if destroyed_route_plan:
            index_list = list(range(len(routes)))
            selected_index = rnd.choice(index_list)
            removed_route = routes[selected_index]
            destroyed_route_plan.remove(removed_route)
       
        removed_activities = []
        for act in removed_route:
            removed_activities.add(act)
     
        return destroyed_route_plan, removed_activities, True
    
    def worst_route_removal(self, current_route_plan):
        destroyed_route_plan = copy.deepcopy(current_route_plan)
        routes = destroyed_route_plan.routes
        worst_route = None
        current_worst_objective = current_route_plan.objective

        for route in routes:
            route_plan_holder = copy.deepcopy(current_route_plan)
            removed_route = route_plan_holder.routes.pop(route)
            objective_removed_route = route_plan_holder.objective
            
            # If current worst objective is better than candidate, then candidate is the new current worst
            if checkCandidateBetterThanCurrent(current_worst_objective, objective_removed_route):
                worst_route = removed_route
                current_worst_objective = objective_removed_route
                destroyed_route_plan = route_plan_holder
            
        removed_activities = []
        for act in worst_route:
            removed_activities.add(act)

        return destroyed_route_plan, removed_activities, True
         """
    def random_treatment_removal(self, current_route_plan):
        # TODO: Må oppdatere routeplan.allocatedPatients dersom alle pasientens treatments fjernes
        destroyed_route_plan = copy.deepcopy(current_route_plan)
        selected_treatment = rnd.choice(destroyed_route_plan.treatments.keys())
        removed_activities = []
        for visit in destroyed_route_plan.treatments[selected_treatment]:
            removed_activities += destroyed_route_plan.visits[visit]
        for day in range(1, self.days +1): 
            for route in self.routes[day]: 
                for act in route: 
                    if act.id in removed_activities:
                        route.removeActivityID(act.id)
        
        return destroyed_route_plan, removed_activities, True

    

# TODO: Finne ut om vi i det hele tatt skal ha removal operatorer på aktivitetsnivå? Repair vil bli veldig conditioned i så fall. 
    def worst_activity_removal_on_day():
    #Removes the worst activity on a "locked" day, being the one contributing the least to the objective. (Can possibly later be used on several days, given conditional repair operators.)
    #Only relevant objective is    
        """
    for day in current_route_plan:
            for route in current_route_plan.routes[day]: 
                for activity in route:

                self.objective1[4] += route.updateObjective()
        removed_activity = current_infeasible_set
        destroyed = []
        return destroyed_route_plan, removed_activity, destroyed, destroyed_on_day
      
        destroyed = []
        destroyed_on_day = None
        """
        return None
    
    def worst_leg_removal_on_day():
    #Removes one leg (etappe, two activities) in a route on a "locked" day. (Can possibly later be used on several days, given conditional repair operators.)
        return None
    
    def random_activity_removal_on_day():
    #Removes one random activity on a "locked" day. (Can possibly later be used on several days, given conditional repair operators.)
        return None

    def random_leg_removal_on_day():
    #Removes one leg (etappe, two activities) in a route on a "locked" day. (Can possibly later be used on several days, given conditional repair operators.)
        return None
    
    
#---------- REPAIR OPERATORS ----------
    def greedy_repair(self, destroyed_route_plan, removed_activities):
        route_plan = copy.deepcopy(destroyed_route_plan)
        must_insert_activities = []
        # Må sjekke om aktiviteter i removed_activities har samme pasient som noen aktiviteter i route plan.allocatedpatients (hvis denne hadde flere treatments). 
        # I så fall må alle aktiviteter i hele treatmentet som ble fjernet prioriteres til å legges inn.
        # Vil kjøre insertion på treatment-nivå (TreatmentInsertions-klasse kanskje? Agnes er usikker) for å legge inn disse som har denne sammenhengen
        # Så kjøre vanlig grådig PatientInsertion

        while not removed_activities.empty:
            route_plan, new_objective = self.repair_generator.generate_insertions(
                route_plan=route_plan, activity=activity, rid=rid, infeasible_set=infeasible_set, initial_route_plan=current_route_plan, index_removed=index_removal, objectives=0)

            # update current objective
            current_objective = new_objective

        return route_plan, current_objective