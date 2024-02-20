import pandas as pd
import copy
import math

import os
import sys
#sys.path.append("C:\\Users\\hilvif\\masters-thesis\\heuristic\\improvement\\operators")
sys.path.append( os.path.join(os.path.split(__file__)[0],'..','..','..'))  # Include subfolders

from objects.distances import *
from config.construction_config import *
#from heuristic.improvement.initial.initial_repair_generator import RepairGenerator

class Operators:
    def __init__(self, alns):
        self.destruction_degree = alns.destruction_degree
        self.constructor = alns.constructor
        self.T_ij = T_ij #Må T_ij hentes på en smartere måte her?
        # TODO: SE PÅ REPAIR OG INSERTION GENERELT: self.repair_generator = RepairGenerator(self.constructor)

    # TODO: Lage en funksjon som finner number of activities/visits/treatments/patients to remove based on degree of destruction
    def activities_to_remove(self, route_plan):
        # Count number of activities in route_plan
        num_activities = 0

        # TODO: Må hente ut unike pasienter og visits fra route_plan 
        num_activities = []
        for route in route_plan:
            for activity in route: 
                if activity not in num_activities:
                    num_activities.append(activity)

        # Calculate number of activities to remove
        activities_remove = math.ceil(num_activities * self.destruction_degree)

        return activities_remove
    
#---------- REMOVE OPERATORS ----------
    def random_activity_removal_on_day():
    #Removes one random activity on a "locked" day. (Can possibly later be used on several days, given conditional repair operators.)
        return None
    
    def random_route_removal_on_day():
    #Removes a random whole route on a "locked" day. (Can possibly later be used on several days, given conditional repair operators.)
        return None
    
    def random_leg_removal_on_day():
    #Removes one leg (etappe, two activities) in a route on a "locked" day. (Can possibly later be used on several days, given conditional repair operators.)
        return None
    
    def worst_activity_removal_on_day():
    #Removes the worst activity on a "locked" day, being the one contributing the least to the objective. (Can possibly later be used on several days, given conditional repair operators.)
        return None
    
    def worst_route_removal_on_day():
    #Removes the worst whole route on a "locked" day. (Can possibly later be used on several days, given conditional repair operators.)
        return None
    
    def worst_leg_removal_on_day():
    #Removes one leg (etappe, two activities) in a route on a "locked" day. (Can possibly later be used on several days, given conditional repair operators.)
        return None
    
    
#---------- REPAIR OPERATORS ----------