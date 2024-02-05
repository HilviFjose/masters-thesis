from tqdm import tqdm
from insertion_generator import InsertionGenerator
import pandas as pd


class ConstructionHeuristic:
    def __init__(self, activities, patients, employees):
        '''
        #activites og employees er dataframes 
        
        #self.n = len(requests.index)
        self.activites = activities["id"]
        self.employees = employees["id"]
        self.patients = patients["id"]
        #Tror ikke vi skal ha de over. Mulig patients, treatments og visits skal organiseres på en annen måte 
        self.days = 5 

        #Usikker på hva vi skal med denne
        self.num_nodes_and_depot = (activites.count() + 1)*days* employees.count()  
        self.T_ij = self.travel_matrix(self.activites)
        #self.current_objective 
        #Har dataframe for de tre ulike entitene 

        
        self.insertion_generator = InsertionGenerator(self)

        #De lager en liste for alle 
        self.preprocessed = self.preprocess_requests()
        '''
        self.activites = activities
        self.patients = patients
        self.employees = employees
        self.insertion_generator = InsertionGenerator(self)

        #Sender inn dataframes som 

        #Når konstruksjonsheuristikken opprettes så gjøres det en preprossesering i etterpå. 
        #De virker som at de lager en P_ij matrise beskriver hvordan ulike deler ligge ri forhold til hverandr

    def jegFinnes(self):
        print("Konstruktoren finnes")

    #Det først vi gjør etter den er laget 
    def construct_initial(self):
        rid = 1
        unassigned_requests = self.requests.copy()
        self.introduced_vehicles.add(self.vehicles.pop(0))
        route_plan = [[]]
        for i in tqdm(range(unassigned_requests.shape[0]), colour='#39ff14'):
            # while not unassigned_requests.empty:
            request = unassigned_requests.iloc[i]


            route_plan, new_objective = self.insertion_generator.generate_insertions(
                route_plan=route_plan, request=request, rid=rid)

            # update current objective
            self.current_objective = new_objective

            rid += 1
        return route_plan, self.current_objective, self.infeasible_set

    def travel_matrix(self, df):
        #TODO: Lage funksjonen basert på det som Anna og de har gjort 
        return T_ij 