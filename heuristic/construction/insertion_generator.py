import numpy as np 
import os
import sys
sys.path.append( os.path.join(os.path.split(__file__)[0],'..') )  # Include subfolders
from objects.patterns import pattern
from objects.activity import Activity
import copy
import random 

'''
Info: PatientInsertor prøver å legge til en pasient i ruteplanen som sendes inn
TODO: Skrive mer utfyllende her
'''
# TODO: Må sende inn patientID
class PatientInsertor:
    def __init__(self, route_plan, patients_df, treatment_df, visit_df, activities_df):
        self.treatment_df = treatment_df
        self.route_plan = route_plan
        self.activites_df = activities_df
        self.visit_df = visit_df
        self.patients_df = patients_df
        self.patient = list(self.patients_df)[0]

        #Liste over treatments som pasienten skal gjennomgå
        self.treatments = self.string_or_number_to_int_list(patients_df["treatment"])
        #Dette er en parameter som settes for å bytte på hvilken vei det iteres over patterns. 
        #TODO: Burde heller gjøres ved å iterere tilfeldig over rekkefølgen på patterns
        self.rev = False

    def generate_insertions(self):
        '''
        Funksjonen forsøker å legge til alle treatments for pasienten. 

        Returns: 
        True/False på om det var plass til pasienten på hjemmesykehus eller ikke 
        '''
         
        #TODO: Treatments bør sorteres slik at de mest kompliserte 
        for treatment in self.treatments: 
            treatStatus = False
            stringVisits = self.treatment_df.loc[treatment, 'visit']
            visitList = self.string_or_number_to_int_list(stringVisits)
            old_route_plan = copy.deepcopy(self.route_plan)

            if self.rev == True:
                patterns =  reversed(pattern[self.treatment_df.loc[treatment, 'pattern']])
                self.rev = False
            else: 
                patterns = pattern[self.treatment_df.loc[treatment, 'pattern']]
                self.rev = True
            
            for treatPattern in patterns:
                insertStatus = self.insert_visit_with_pattern(visitList, treatPattern) 
                if insertStatus == True:
                    treatStatus = True
                    if self.patient in self.route_plan.allocatedPatients.keys():
                        self.route_plan.allocatedPatients[self.patient].append(treatment)
                    else:
                        self.route_plan.allocatedPatients[self.patient] = [treatment]
                    self.route_plan.treatments[treatment] = visitList
                    break
                self.route_plan = copy.deepcopy(old_route_plan)
            if treatStatus == False: 
                return False
        return True
    

    def insert_visit_with_pattern(self, visits, pattern):
        '''
        Funksjonen forsøker å legge til alle visits for pasienten. 

        Arg: 
        visits (list): Liste av vists som skal legges til i self.route_plan, eks: [5,6,7]
        pattern (list): Liste som inneholder et pattern, med 1 på dager visits skal gjennomføre, eks: [1,0,1,0,1]

        Returns: 
        True/False på om det var plass til visitene på hjemmesykehuset med dette patternet 
        '''

        visit_index = 0
        #Iterer gjennom alle dagene i patternet 
        for day_index in range(len(pattern)): 
            #hvis patternet på den gitte dagen er 1, så forsøker vi å inserte visittet på den gitte dagen
            #Dersom insert ikke er mulig returerer funkjsonen False
            if pattern[day_index] == 1: 
                insertStatus = self.insert_visit_on_day(visits[visit_index], day_index+1) 
                if insertStatus == False: 
                    return False
                #Øker indeksen for å betrakte neste visit i visitlisten
                visit_index += 1 
        return True   
                

    #Denne 
    def insert_visit_on_day(self, visit, day):  
        '''
        Funksjonen forsøker å legge til alle aktiviter som inngår i et visit ved å oppdatere route_self 

        Arg: 
        visit (int): Et visit som skal legges til i self.route_plan eks: 6
        day (int): Dagen visitet skal gjennomføres, eks: 3

        Returns: 
        True/False på om det var plass til visitet på hjemmesykehuset denn dagen
        '''

        #Henter ut liste med aktiviteter som inngår i vistet 
        stringActivities = self.visit_df.loc[visit, 'nodes']
        activitesList = self.string_or_number_to_int_list(stringActivities)
        
        #Iterer over alle aktivitere i visitet som må legges til på denne dagen 
        for activityID in activitesList: 
            activity = Activity(self.activites_df, activityID)
            activityStatus = self.route_plan.addActivityOnDay(activity, day)
            if activityStatus == False: 
                return False
        #Dersom alle aktivitene har blitt lagt til returers true  
        self.route_plan.visits[visit] = activitesList  
        return True
    
    def string_or_number_to_int_list(self, string_or_int):
        '''
        Denne funksjonen brukes til å lage liste basert på string eller int dataen som kommer fra dataframe

        Return: 
        List of int values 
        '''
        
        if type(string_or_int) == str and "," in string_or_int: 
            stringList = string_or_int.split(',')
        else: 
            stringList = [string_or_int]
        return  [int(x) for x in stringList]
       

    