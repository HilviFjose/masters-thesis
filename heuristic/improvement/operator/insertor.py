import copy
from objects.patterns import pattern
from objects.activity import Activity
import random 


class Insertor:
    def __init__(self, constructor, route_plan):
        self.constructor = constructor
        self.route_plan = copy.deepcopy(route_plan)

        self.rev = False

     
    '''
    Skal prøve å lage insertions på hvert nivå, og å endre slik at vi kan inserte på hvert nivå
    '''


#Konseptet her er at vi skal kunne sende inn all atributter vi vil legge til.
    def insertPatients(self, patientList): 
        for patient in patientList: 
            self.insert_patient(patient)

    def insert_patient(self, patient):
        '''
        Funksjonen forsøker å legge til alle treatments for pasienten. 

        Returns: 
        True/False på om det var plass til pasienten på hjemmesykehus eller ikke 
        '''
        route_test = copy.deepcopy(self.route_plan)
        old_route_plan = copy.deepcopy(route_test)
        #TODO: Treatments bør sorteres slik at de mest kompliserte komme tidligst 
        treamentList = self.constructor.patients_df.loc[patient, 'treatmentsIds']
     
        for treatment in treamentList: 
            
            status = self.insert_treatment(treatment)

            self.updateAllocation(status, patient, treatment)
            if status == False: 
                if patient == 18: 
                    print("pasient", patient, "prøver legge til treatment ", treatment, "får FALSE")
                    self.route_plan.printSolution("TEST18FOR")
                self.route_plan = old_route_plan
                if patient == 18: 
                    self.route_plan.printSolution("TEST18ETTER")
                return False
        #Må ha noe som legger til hvis den er
        if patient in self.route_plan.notAllocatedPatients: 
            self.route_plan.notAllocatedPatients.remove(patient)
        #print("Insertor - Legger til pasient ", patient)
        return True 

    def updateAllocation(self, allocated, patient, treatment): 
        if allocated: 
            if patient in self.route_plan.allocatedPatients.keys():
                self.route_plan.allocatedPatients[patient].append(treatment)
            else:
                self.route_plan.allocatedPatients[patient] = [treatment]
            
        if not allocated and patient in self.route_plan.allocatedPatients.keys(): 
            self.route_plan.illegalNotAllocatedTreatments.append(treatment)

        '''
        Hva vil vi sjekke. 
        Når vi legger til en treatment, 

        Regelen skal vel være at pasienten er allokert allokert eller ikke allokert. 
        Dersom den er allokert, men ikke alt ligger inne, så de treatmentsene, eller andre, lagres i illegal
        Men det ligger en liste over treatments som ikke er 
        '''

    def insert_treatment(self, treatment): 
    
        visitList = self.constructor.treatment_df.loc[treatment, 'visitsIds']

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
        #random.shuffle(index_random) #TODO: Hvis du skal feilsøke kan du vurdere å kommentere ut denne linjen. 

        
        for index in index_random:
            insertStatus = self.insert_visit_with_pattern(visitList, patterns[index]) 
            if insertStatus == True:
                
                self.route_plan.treatments[treatment] = visitList
                return True
            
            self.route_plan = copy.deepcopy(old_route_plan)
        return False
    

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
        activitiesList = self.constructor.visit_df.loc[visit, 'activitiesIds']

        #Iterer over alle aktivitere i visitet som må legges til på denne dagen 
        for activityID in activitiesList: 
            activity = Activity(self.constructor.activities_df, activityID)
            activityStatus = self.route_plan.addActivityOnDay(activity, day)
            if activityStatus == False: 
                return False
        #Dersom alle aktivitene har blitt lagt til returers true  
        self.route_plan.visits[visit] = activitiesList  
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
       

    