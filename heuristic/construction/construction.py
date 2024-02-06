from tqdm import tqdm
from .insertion_generator import InsertionGenerator
import pandas as pd
from typing import List
import json
import requests
import pandas as pd

'''
INFO:
I denne klassen definerer de mange funksjoner som jeg ikke forstår hva de bruker til senere. Lurer på det
Lurer også på hvorfor de oppretter distanseamatrisen her og ikke senere. Hvordan hentes dette opp igjen senere.
Må forstå mer av strukturen på det. 
'''

class ConstructionHeuristic:
    def __init__(self, activities,  employees, patients):
        
        self.activities = activities
        self.patients = patients
        self.employees = employees
        self.insertion_generator = InsertionGenerator(self)
        self.T_ij = self.travel_matrix(self.activities)
        #OBS: Når ducatin er på denne formen så må alle aktiviteter være stigende direkte fra denne 
        #Tror vi heller skal aksessere den direkte i løpet av bruken av den



        #Sender inn dataframes som 

        #Når konstruksjonsheuristikken opprettes så gjøres det en preprossesering i etterpå. 
        #De virker som at de lager en P_ij matrise beskriver hvordan ulike deler ligge ri forhold til hverandr

        #Kontruksjonsheuristikken må ha en egen distance matrise og duration for alle 

    def getActivities(self):
        return self.activities

    def getDurations(self): 
        return self.D_i

    def getT_ij(self): 
            return self.T_ij

    '''
    Hvordan fungere det med klaser hvor de kaller hverandre. 
    Konstruksjonsheuristikken har ulike løsninger og ruter som benyttes. Disse byttes ut etterhvert og vil variere. 
    Likevel må rutene kunne hente ut datagrunnlaget som hører til selve konstrukjsonen. Nei det kan de ikke 
    Dataen som skal brukes til den spessifikke oprerasjonen må sendes inn i de andre løsningene. 

    Burde derfor bygge det innenfra. Det er 


    Det først vi gjør etter at cosntruction heuristikken er laget. 
    Her konstrueres det et løsningsobjekt, som er route plan
    
    Prove å forstå selve konstruksjonsheurstikk klassen. Den har en ruteplan. Denne må være for hver ansatt på hver dag som jobber. 
    #TODO: Lage et løsningsobjekt som består av ruter. 
    Konstruksjonen har en route plan, som er 
    '''
    def construct_initial(self):
        #Tror rid er request iden, går over alle requests som er gått. Dette blir aktiviteter for oss 
        rid = 1
        unassigned_requests = self.requests.copy()
        #Henter ut en introduced veichles, som er de veiclesenen som igang
        self.introduced_vehicles.add(self.vehicles.pop(0))
        route_plan = [[]]
        for i in tqdm(range(unassigned_requests.shape[0]), colour='#39ff14'):
            # while not unassigned_requests.empty:
            request = unassigned_requests.iloc[i]
            
            #Henter ut hvert request objekt fra unassigned requests. Iterer gjennom alle. 

            #Generate insertion kalles her. Da ønsker vi å putte inn en ny request, gitt den gjeldende ruteplanen 
            route_plan, new_objective = self.insertion_generator.generate_insertions(
                route_plan=route_plan, request=request, rid=rid)

            # update current objective
            self.current_objective = new_objective

            rid += 1
        #TODO: Forstår ikke helt hvorfor infeasible set returneres her? Her har jo ikke blitt gjort noe med 
        return route_plan, self.current_objective, self.infeasible_set
    
    #IDE: Må lage en generate insertion, som kan ta inn en liste med aktiviteter. 
    #Forskjellen på vår og deres er at det blir veldig raskt ugylldig 

    def travel_matrix(self, df):
        coordinate_string_patient = self.get_coordinates_string_from_list(self.activities['location'].tolist())
        return self.get_distance_matrix(coordinate_string_patient)
        #TODO: Lage funksjonen basert på det som Anna og de har gjort 
        
 
    def get_coordinates_string_from_list(self, list):
        coordinates_string = ";".join(str(item) for item in list)
        return coordinates_string.replace("(", "").replace(")", "").replace(" ", "").replace("[","").replace("]","")

    def get_distance_matrix(self, coordinates_string):
        # Documntation for this API: http://project-osrm.org/docs/v5.10.0/api/#general-options
        url = 'http://router.project-osrm.org/table/v1/driving/'+coordinates_string+''
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if 'durations' in data:  # Make sure 'durations' key exists
                # Process and return the durations data as needed
                return data['durations']
            else:
                # 'durations' key does not exist, return a default value or handle the error as appropriate
                print("Durations data not provided in the API response.")
                return None  # You could return an empty list or dict instead, depending on your use case
        else:
            # The API did not return a successful response
            print(f"Error fetching data: {response.status_code}")
            return None

