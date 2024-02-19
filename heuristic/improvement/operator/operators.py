import pandas as pd
import copy
import math

import os
import sys
sys.path.append("C:\\Users\\hilvif\\masters-thesis\\heuristic\\improvement\\operators")
#sys.path.append( os.path.join(os.path.split(__file__)[0],'..')  # Include subfolders

# from objects.distances import *
# from config.construction_config import *
# from heuristic.improvement.initial.initial_repair_generator import RepairGenerator

class Operators:
    def __init__(self, alns):
        self.destruction_degree = alns.destruction_degree
        self.constructor = alns.constructor
        #self.T_ij = T_ij #Må T_ij hentes på en smartere måte her?
        # TODO: SE PÅ REPAIR OG INSERTION GENERELT: self.repair_generator = RepairGenerator(self.constructor)

    # Find number of activities to remove based on degree of destruction
    def nodes_to_remove(self, route_plan):
        # Count number of activities in route_plan
        total_visits = 0
        total_patients = 0

        # TODO: Må hente ut unike pasienter og visits fra route_plan 
        for i in route_plan:
            print("i",i)
            #for col in row:
                #if col[0]:
                    #total_visits += 0.5

        # Calculate number of visits to remove
        visits_remove = math.ceil(total_visits * self.destruction_degree)
        # Calculate number of visits to remove
        patients_remove = math.ceil(total_patients * self.destruction_degree)

        return visits_remove, patients_remove
    
#---------- REMOVE OPERATORS ----------
    
#---------- REPAIR OPERATORS ----------