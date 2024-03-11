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
    def __init__(self, route_plan, patient_df, constructor):
        self.constructor = constructor
      
        self.route_plan = route_plan
      
        self.patient = [list(self.constructor.patients_df)[0]]

        self.patients_df = patient_df

        #Liste over treatments som pasienten skal gjennomgå
        #self.treatments = self.string_or_number_to_int_list(patients_df["treatmentsIds"])
        self.treatments = self.patients_df["treatmentsIds"]
        #Dette er en parameter som settes for å bytte på hvilken vei det iteres over patterns. 
        #TODO: Burde heller gjøres ved å iterere tilfeldig over rekkefølgen på patterns
        self.rev = False

    def insert_patients(self):
        '''
        Funksjonen forsøker å legge til alle treatments for pasienten. 

        Returns: 
        True/False på om det var plass til pasienten på hjemmesykehus eller ikke 
        '''
        
        if self.patient == 7: 
            print("p7 treatments", self.treatments)
                
        #TODO: Treatments bør sorteres slik at de mest kompliserte 
        for treatment in self.treatments: 
            treatStatus = False
            #Henter ut alle visits knyttet til behandlingen og legger de i en visitList
            #stringVisit = self.treatment_df.loc[treatment, 'visitsIds']
            #visitList = self.string_or_number_to_int_list(stringVisit)
            visitList = self.constructor.treatment_df.loc[treatment, 'visitsIds']
            
            #Oppretter en kopi av ruteplanen uten pasienten  
            old_route_plan = copy.deepcopy(self.route_plan)

            '''
            #Reverserer listen annen hver gang for å ikke alltid begynne med pattern på starten av uken
            if self.rev == True:
                patterns =  reversed(pattern[self.constructor.treatment_df.loc[treatment, 'patternType']])
                self.rev = False
            else: 
                patterns = pattern[self.constructor.treatment_df.loc[treatment, 'patternType']]
                self.rev = True
            '''
            #Iterer over alle patterns som er mulige for denne treatmenten
            patterns = pattern[self.constructor.treatment_df.loc[treatment, 'patternType']]
            index_random = [i for i in range(len(patterns))]
            random.shuffle(index_random) #TODO: Hvis du skal feilsøke kan du vurdere å kommentere ut denne linjen. 

            for index in index_random:
                treatPattern = patterns[index]
                #Forsøker å inserte visit med pattern. insertStatus settes til True hvis velykket
                insertStatus = self.insert_visit_with_pattern(visitList, treatPattern) 
                if insertStatus == True:
                    treatStatus = True
                    if self.patient[0] in self.route_plan.allocatedPatients.keys():
                        self.route_plan.allocatedPatients[self.patient[0]].append(treatment)
                    else:
                        self.route_plan.allocatedPatients[self.patient[0]] = [treatment]
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
                if visits == [20, 21, 22, 23, 24]: 
                    print("insert ", visits[visit_index], " on day ", str(day_index+1), " NOT SUCCESS")
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
        #stringActivities = self.visit_df.loc[visit, 'activitiesIds']
        #activitesList = self.string_or_number_to_int_list(stringActivities)
        activitiesList = self.constructor.visit_df.loc[visit, 'activitiesIds']

        #Iterer over alle aktivitere i visitet som må legges til på denne dagen 
        for activityID in activitiesList: 
            #Oppreter et aktivitesobjekt basert på ID-en 
            activity = Activity(self.constructor.activites_df, activityID)
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
       

    