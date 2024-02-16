import numpy as np 
import sys
sys.path.append("C:\\Users\\agnesost\\masters-thesis")
from objects.patterns import pattern
from objects.actitivites import Acitivity
import copy
import random 

'''
Info: PatientInsertor prøver å legge til en pasient i ruteplanen som sendes inn
TODO: Skrive mer utfyllende her
'''

class PatientInsertor:
    def __init__(self, route_plan, patients_df, treatment_df, visit_df, activities_df):
        self.treatment_df = treatment_df
        self.route_plan = route_plan
        self.activites_df = activities_df
        self.visit_df = visit_df
        self.patients_df = patients_df

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
            #Henter ut alle visits knyttet til behandlingen og legger de i en visitList
            stringVisits = self.treatment_df.loc[treatment, 'visit']
            visitList = self.string_or_number_to_int_list(stringVisits)
            
            #Oppretter en kopi av ruteplanen uten pasienten  
            old_route_plan = copy.deepcopy(self.route_plan)

            
            #Reverserer listen annen hver gang for å ikke alltid begynne med pattern på starten av uken
            if self.rev == True:
                patterns =  reversed(pattern[self.treatment_df.loc[treatment, 'pattern']])
                self.rev = False
            else: 
                patterns = pattern[self.treatment_df.loc[treatment, 'pattern']]
                self.rev = True
            
            #Iterer over alle patterns som er mulige for denne treatmenten
            for treatPattern in patterns:
                #Forsøker å inserte visit med pattern. insertStatus settes til True hvis velykket
                insertStatus = self.insert_visit_with_pattern(visitList, treatPattern) 
                #Hvis insertet av visit med pattern er velykkt settes treatStaus til True. 
                #Deretter breakes løkken fordi vi ikke trenger å sjekke for flere pattern.
                if insertStatus == True:
                   treatStatus = True
                   break
                #Kommer hit dersom patternet ikke fungerte. 
                #Gjennoppretter da routePlanen til å være det den var før vi la til visits. 
                self.route_plan = copy.deepcopy(old_route_plan)
                
            #Returnerer False hvis det ikke var mulig å legge til treatmentet med noen av patterne
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
            #Oppreter et aktivitesobjekt basert på ID-en 
            activity = Acitivity(self.activites_df, activityID)
            
            #Her håndteres pick up and delivery
            #PickUpAcitivy er aktiviteten som tilsvarer pick up noded dersom denne aktiviteten er delivery
            if activity.getPickUpActivityID() != 0 and activity.getPickUpActivityID() < activityID: 
                #Henter ut den ansatte som skal gjennomføre PickUp aktiviteten 
                employeeAllocatedToAcitivy = self.route_plan.getEmployeeAllocatedForActivity(activity.getPickUpActivityID(), day)
                #Henter ut de ansatte som jobber den gitte dagen og ikke er allokert til å utføre pickup aktiviten 
                otherEmplOnDay = self.route_plan.getOtherEmplOnDay(employeeAllocatedToAcitivy, day)
                #Legger til de ansatte som ikke allokert til å gjøre pick up noden til delivery aktivteten employee restictions
                activity.addEmployeeRes(otherEmplOnDay) 

            #Her håndteres presedens.   
            #Aktivitetns earliests starttidspunkt oppdateres basert på starttidspunktet til presedens aktiviten
            for prevNode in activity.getPrevNode(): 
                prevNodeAct = self.route_plan.getActivity(prevNode, day)
                activity.setEarliestStartTime(prevNodeAct.getStartTime()+prevNodeAct.getDuration())

            #Her håndteres presedens med tidsvindu
            #aktivitetens latest start time oppdateres til å være seneste starttidspunktet til presedensnoden
            for PrevNodeInTime in activity.getPrevNodeInTime(): 
                prevNodeAct = self.route_plan.getActivity(PrevNodeInTime[0], day)
                activity.setLatestStartTime(prevNodeAct.getStartTime()+PrevNodeInTime[1])
                #TODO: Noe galt med denne funksjonen 
            
            #Prøver å legge til aktivten til ruteplanen på den gitte dagen.
            activityStatus = self.route_plan.addNodeOnDay(activity, day)
            #Dersom aktiviten ikk kan legges til returers False
            if activityStatus == False: 
                return False
        #Dersom alle aktivitene har blitt lagt til returers true    
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
       

    