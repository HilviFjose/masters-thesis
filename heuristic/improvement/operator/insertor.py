import copy
from objects.patterns import pattern
from objects.activity import Activity
import random 


class Insertor:
    def __init__(self, constructor, route_plan):
        self.constructor = constructor
        #self.route_plan = copy.deepcopy(route_plan)
        self.route_plan = route_plan
        self.rev = False

     
    '''
    Insertor skal ikke gjøre noen oppdatering av matrisene. Det skal kunn skje i constructor og operators

    Her må altså alle oppdateringer flyttes ut til operators. Denne inserter bare, så vil aldri fjerne elemener 

    Mulig insertPatients må fjernes. Fordi den vil bare legge inn, også oppdateres det ikke basert på hva som skjer 
    '''

    '''
#Konseptet her er at vi skal kunne sende inn all atributter vi vil legge til.
    def insertPatients(self, patientList): 
        for patient in patientList: 
            self.insert_patient(patient)
        return self.route_plan
    '''

    def insert_patient(self, patient):
        old_route_plan = copy.deepcopy(self.route_plan)
        #TODO: Treatments bør sorteres slik at de mest kompliserte komme tidligst
        treamentList = self.constructor.patients_df.loc[patient, 'treatmentsIds']
        inAllocation = False 
        if (self.constructor.patients_df.loc[patient, 'allocation'] == 1): 
            inAllocation = True 
     
        for treatment in treamentList: 
            status = self.insert_treatment(treatment)
            if status == False: 
                self.route_plan = old_route_plan
                return False
            
        #Nå har den kommet hit så da er det 
        '''
        Har fjernet de hvis de ligger i listen. Må legge de til hvs
        '''
        if patient in self.route_plan.notAllocatedPatients: 
            self.route_plan.notAllocatedPatients.remove(patient)
        
        if patient in self.route_plan.illegalNotAllocatedPatients: 
            self.route_plan.illegalNotAllocatedPatients.remove(patient)
        
        self.route_plan.allocatedPatients[patient] = treamentList
        
        return True 

    #TODO: Sjekke denne funksjonen. Finne ut hvor denne funksjonaliteten skal ligge, for i de andre illegal funksjonene så er det 
    
    '''
    def updateAllocation(self, allocated, patient, treatment): 
        if allocated: 
            if patient in self.route_plan.allocatedPatients.keys():
                self.route_plan.allocatedPatients[patient].append(treatment)
            else:
                self.route_plan.allocatedPatients[patient] = [treatment]
            
        if not allocated and patient in self.route_plan.allocatedPatients.keys(): 
            self.route_plan.illegalNotAllocatedTreatments.append(treatment)

        
        Hva vil vi sjekke. Vi forsøker å legge til en pasient. Den er altså helt utenfor allokeringen. 
        
        Jeg forstår ikke hvorfor allokeringen gjøres gradvis her. det er vel feil? 



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
        random.shuffle(index_random) #TODO: Hvis du skal feilsøke kan du vurdere å kommentere ut denne linjen. 

        for index in index_random:
            self.route_plan = copy.deepcopy(old_route_plan)
            insertStatus = self.insert_visit_with_pattern(visitList, patterns[index]) 
            if insertStatus == True:
                return True
            
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
                

    def insert_visit_on_day(self, visit, day):  
        activitiesList = self.constructor.visit_df.loc[visit, 'activitiesIds']
        old_route_plan = copy.deepcopy(self.route_plan)
        #Iterer over alle aktivitere i visitet som må legges til på denne dagen 
        for activityID in activitiesList: 
            activity = Activity(self.constructor.activities_df, activityID)
            activityStatus = self.route_plan.addActivityOnDay(activity, day)
            if activityStatus == False: 
                self.route_plan = old_route_plan
                return False
        #Dersom alle aktivitene har blitt lagt til returers true  
        return True
    



    