from tqdm import tqdm
import pandas as pd
import copy
from insertion_generator import PatientInsertor
import sys
sys.path.append("C:\\Users\\agnesost\\masters-thesis")
from objects.route_plan import RoutePlan

'''
Info: ConstructionHeurstic klassen er selve konstruskjonsheurstikken. 
Den opprettes med et løsning i form av en RoutePlan objekt, objektivverdi og null pasienter
Gjennom construct_inital funksjonen så oppdateres løsningen, objektivverdien og pasientlisten
'''


class ConstructionHeuristic:
    def __init__(self, activities_df,  employees_df, patients_df, treatment_df, visit_df, days):
        
        self.activities_df = activities_df
        self.visit_df = visit_df
        self.treatment_df = treatment_df
        self.patients_df = patients_df
        self.employees_df = employees_df
        self.days = days

        self.route_plan = RoutePlan(days, employees_df) 
        self.current_objective = 0 
        self.listOfPatients = []
        self.unAssignedPatients = []
        
 
    def construct_initial(self): 
        '''
        Funksjonen iterer over alle paienter som kan allokeres til hjemmesykehuset. 
        Rekkefølgen bestemmes av hvor mye aggregert suitability pasienten vil tilføre ojektivet
        '''

        #Lager en liste med pasienter i prioritert rekkefølge. 
        unassigned_patients = df_patients.sort_values(by="aggSuit", ascending=False)
        
        #Iterer over hver pasient i lista. Pasienten vi ser på kalles videre pasient
        for i in tqdm(range(unassigned_patients.shape[0]), colour='#39ff14'):
            #Henter ut raden i pasient dataframes som tilhører pasienten
            patient = unassigned_patients.index[i] 
            patient_request = unassigned_patients.iloc[i]
            
            #Kopierer nåværende ruteplan for denne pasienten 
            route_plan_with_patient = copy.deepcopy(self.route_plan)
            #Oppretter et PatientInsertor objekt, hvor pasient_df og kopien av dagens ruteplan sendes inn
            patientInsertor = PatientInsertor( route_plan_with_patient, patient_request, self.treatment_df, self.visit_df, self.activities_df)
            #patientInsertor forsøker å legge til pasienten, og returnerer True hvis velykket
            state = patientInsertor.generate_insertions()
            
           
            if state == True: 
                #Construksjonsheuristikkens ruteplan oppdateres til å inneholde pasienten
                self.route_plan = patientInsertor.route_plan
                #Objektivverdien oppdateres
                self.current_objective += patient_request["aggSuit"]
                #Pasienten legges til i hjemmsykehusets liste med pasienter
                self.listOfPatients.append(patient)
                
            #Hvis pasienten ikke kan legges inn puttes den i Ikke allokert lista
            if state == False: 
                self.unAssignedPatients.append(patient)
        
'''
Alt som kommer under her er for å teste koden, skal foreløpig kjøres herfra når testes
'''    

#TODO: Endre slik at dataen ikke må hentes på denne måten
df_activities  = pd.read_csv("data/NodesNY.csv").set_index(["id"]) 
df_employees = pd.read_csv("data/EmployeesNY.csv").set_index(["EmployeeID"])
df_patients = pd.read_csv("data/Patients.csv").set_index(["patient"])
df_treatments = pd.read_csv("data/Treatment.csv").set_index(["treatment"])
df_visits = pd.read_csv("data/Visit.csv").set_index(["visit"])


testConsHeur = ConstructionHeuristic(df_activities, df_employees, df_patients, df_treatments, df_visits, 5)
testConsHeur.construct_initial()
testConsHeur.route_plan.printSoultion()
print("Dette er objektivet", testConsHeur.current_objective)
print("Hjemmesykehuspasienter ", testConsHeur.listOfPatients)
print("Ikke allokert ", testConsHeur.unAssignedPatients)
