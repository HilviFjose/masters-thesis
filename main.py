import pandas as pd
import numpy.random as rnd
import os
import sys

import parameters
from config.main_config import *
from heuristic.construction.construction import ConstructionHeuristic
from heuristic.improvement.simulated_annealing import SimulatedAnnealing
from heuristic.improvement.alns import ALNS
from heuristic.improvement.operator.operators import Operators
from heuristic.improvement.local_search import LocalSearch

import cProfile
import pstats
from pstats import SortKey

def main():
    #TODO: Burde legge til sånn try og accept kriterier her når vi er ferdig. Men Bruker ikke det enda fordi letter å jobbe uten

    #INPUT DATA
    df_employees = parameters.df_employees
    df_patients = parameters.df_patients
    df_treatments = parameters.df_treatments
    df_visits = parameters.df_visits
    df_activities = parameters.df_activities

    #CONSTRUCTION HEURISTIC
    constructor = ConstructionHeuristic(df_activities, df_employees, df_patients, df_treatments, df_visits, 5)
    print("Constructing Initial Solution")
    constructor.construct_initial()
    
    constructor.route_plan.printSolution("initial")

    initial_objective = constructor.route_plan.objective
    initial_route_plan = constructor.route_plan 
    initial_infeasible_set = constructor.unAssignedPatients #Usikker på om dette blir riktig. TODO: Finn ut mer om hva infeasible_set er.

    #IMPROVEMENT OF INITAL SOLUTION 
    #Parameterne er hentet fra config. 
    criterion = SimulatedAnnealing(start_temperature, end_temperature, cooling_rate)

    #Gjør et lokalsøk før ALNS. TODO: Har lite hensikt (?), så det kan fjernes slik at det bare gjøres lokalsøk inne i ALNS-en
    localsearch = LocalSearch(initial_route_plan)
    initial_route_plan = localsearch.do_local_search()
    initial_route_plan.printSolution("initialLS")
   
    alns = ALNS(weights, reaction_factor, initial_route_plan, initial_objective, initial_infeasible_set, criterion,
                    destruction_degree, constructor, rnd_state=rnd.RandomState())

    operators = Operators(alns)

    alns.set_operators(operators)

    #RUN ALNS 
    best_route_plan = alns.iterate(
            iterations)
    
    best_route_plan.printSolution("final")
         


if __name__ == "__main__":
    #main()
    # Profiler hele programmet ditt
    cProfile.run('main()', 'program_profile')

    # Last inn og analyser profildata, fokusert på dine funksjoner
    p = pstats.Stats('program_profile')
    p.strip_dirs().sort_stats(SortKey.TIME).print_stats()

