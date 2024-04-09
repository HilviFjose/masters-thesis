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

        self.InsertionFound_BestInsertVisit = False
        

     
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
        #random.shuffle(index_random) #TODO: Hvis du skal feilsøke kan du vurdere å kommentere ut denne linjen. 

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
                insertStatus = self.best_insert_visit_on_day(visits[visit_index], day_index+1)
                #insertStatus = self.insert_visit_on_day(visits[visit_index], day_index+1) 
                if insertStatus == False: 
                    return False
                #Øker indeksen for å betrakte neste visit i visitlisten
                visit_index += 1 
        return True   
                

    def insert_visit_on_day(self, visit, day):  
        activitiesList = self.constructor.visit_df.loc[visit, 'activitiesIds']
        old_route_plan = copy.deepcopy(self.route_plan)
        #Iterer over alle aktivitere i visitet som må legges til på denne dagen 
        # Create a list of activity objects
        activities = [Activity(self.constructor.activities_df, activityID) for activityID in activitiesList]
        for activity in activities: 
            activityStatus = self.route_plan.addActivityOnDay(activity, day)
            if activityStatus == False: 
                self.route_plan = old_route_plan
                return False
        #Dersom alle aktivitene har blitt lagt til returers true  
        return True
    
    '''
    Det er to feil: 

    1 - Følgefeil ved innsetting, tar med seg innsettingen fra forrige ruteplan 
    2 - Feil i presendens ved innsetting, den klarer ikke varsle de andre tilstrekkelig

    84 legger seg til på 518, det er ikke riktig fordi den har tidsvindu 534

    Det er veldig rart med tidsviduene hvorfor de er feil når vi ser på de

    1) Gå gjennom for å sjekke om de manipuleres ved en feil noe sted 
    '''

    def best_insert_visit_on_day(self, visit, day):
        self.InsertionFound_BestInsertVisit = False 


        activitiesList = self.constructor.visit_df.loc[visit, 'activitiesIds']
        test_route_plan = copy.deepcopy(self.route_plan)

        
        activities = [Activity(self.constructor.activities_df, activityID) for activityID in activitiesList]
        activity = activities[0]
        rest_acitivites = activities[1:]
      
        old_route_plan = copy.deepcopy(test_route_plan)
        for route in test_route_plan.routes[day].values():
            if self.InsertionFound_BestInsertVisit == True: 
                break 
            for index_place in range(len(route.route)+1): 
            
                test_route_plan = copy.deepcopy(old_route_plan)
              

                if self.InsertionFound_BestInsertVisit == False: 
                    self.flytt(activity, rest_acitivites, test_route_plan, day, route.employee.id, index_place)
                    if self.InsertionFound_BestInsertVisit == True: 
                        break
                else: 
                    break
        
        return self.InsertionFound_BestInsertVisit



    def flytt(self, activity, rest_acitivites, route_plan, day, employeeID, index_place):
        print("inserter", activity.id, " og har disse på rest ", rest_acitivites)
        #print("restactivites.id", [a.id for a in rest_acitivites])
        if activity.id == 86: 
            print("FØR - getNewEarliestStartTime", activity.getNewEarliestStartTime()) 
      
            route_plan.routes[1][1].printSoultion()
        #TODO: Den henter starttidspunkt fra feil rute_plan. Se på imorgen
        route_plan.updateActivityBasedOnRoutePlanOnDay0904(activity, day)

        if activity.id == 86: 
            print("ETTER - getNewEarliestStartTime", activity.getNewEarliestStartTime()) 
            print("86 - prevNode ", activity.PrevNode)
            print("86 - PrevNodeInTime ", activity.PrevNodeInTime)
        insertStatus = route_plan.routes[day][employeeID].insertActivityOnIndex(activity, index_place)
        
        if insertStatus == False: 
            return
        
        #TODO: Dette kan skje flere ganger fordi det er mange veier som kan nå helt nederst i treet 
        if not isinstance(rest_acitivites, list):
            rest_acitivites = [rest_acitivites]

        #Vet at vi har klart å legge til aktiviteten 

        if len(rest_acitivites) == 0: 
            self.route_plan = route_plan
            self.InsertionFound_BestInsertVisit = True
            print("finner løsning")
            return
            
        
        next_actitivy = rest_acitivites[0]
        rest_acitivites = rest_acitivites[1:] 
        
       
        old_route_plan = copy.deepcopy(route_plan)
        for route in route_plan.routes[day].values(): 
            if self.InsertionFound_BestInsertVisit == True: 
                break
            for index_place in range(len(route.route)+1): 
                route_plan = copy.deepcopy(old_route_plan)
    
                if self.InsertionFound_BestInsertVisit == False: 
                    self.flytt(next_actitivy, rest_acitivites, route_plan, day, route.employee.id, index_place)
                    if self.InsertionFound_BestInsertVisit == True: 
                        break
                else: 
                    break

          
             
            
    

    
    '''
    Blir dette et bredde først søk? Nei fordi den søker seg

    Den komme seg ned, finner løsningen. Men på vei opp så må den gjøre alle de andre 
    
    Må ha en form for while, slik at den bare kjører hvis den forrige ikke fill true 
    Begynne på laveste nivå

    Hva skal true returnere. Den setter ruteplanen og den setter den globale verdien, så vi trenger ikke ha de andre true/false lenger? 

    Må ha en eller annen global variabel som sier om vi har funnet dette punktet 


    Teste med å printe hvert steg når en aktivitet legges til. 

    Videre arbeid: 
    Dette er ikke en best insertion. 
    Hvordan skulle man laget best insertion: Kan bruke mye av det samme som nå, bare at man endrer til at den går gjennom alle muligheter, og velger den som gir best resultat. 
    Jeg er veldig usikker på hvor lang tid det tar å kjøre disse insertionene.
    '''