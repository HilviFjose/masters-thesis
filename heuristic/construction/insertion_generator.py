import numpy as np 
import sys
sys.path.append("C:\\Users\\agnesost\\masters-thesis")
from objects.patterns import pattern
from objects.actitivites import Acitivity
import copy

'''
Insertion generatoren er for en pasient. 
Det lages en insertion generator hvor 8 kommer med og det oppdateres deretter
'''

class InsertionGenerator:
    def __init__(self, construction_heuristic, route_plan, patients_df, treatment_df, visit_df, activities_df):
        #Heuristikken brukes til å hente ut dataframsene. Altså dataverdiene fra de fortåene   
        #Ruteplanen eksisterer ikke i utganspunktet. Den har blitt laget også sendt inn 
        self.treatment_df = treatment_df
        self.route_plan = route_plan
        self.activites_df = activities_df
        self.visit_df = visit_df
        self.patients_df = patients_df
        #TODO:Bruke patient df til å lage en liste over aktiviteter som skal inn 
        self.requestActivities = np.empty(0, dtype=object)
        self.treatments = self.getIntList(patients_df["treatment"])
        
        self.visits = []
        self.activites = None 

        #Den har jo en pasient og en mulig objektivverdi. 
        #Du kan ikke sende en ny pasient inn etterpå, fordi noen av parameterne er endret på 
        #Så objektet er låst til pasienten man ser på

        '''
        Skal vi her lage oss en rekke med aktivitets requests som må oppfylles
        Eller skal vi ta det mer stegvist 


        Her er den dataframen som sendes inn kunn pasient dataframen. 
        Må derfor i InsertionGenerator hente tilbake alle dataframesenen knyttet til visit og aktivtet
        Det kan hende at det er litt meningsløs genrering å hente tilbake,
        Alternativt sende inn hele aktivtetsdataframen til pasienten, også gjøre radopperasjoner for å sortere på viktigheten av rekkefølgen 
        
        Det er noe mer ruteobjektet her som ikke blir riktig. Kategori

        Det er mystisk at alle får sit første pattern. Virker ikke som at de itereres over
        De 
        '''

    def generate_insertions(self):
        #TODO: Her skal treaments sorteres slik at man vet hvilke som er mest. 
        #Nå itereres den over i rekkefølge 
        patStat = True
        for treatment in self.treatments: 
            treatStat = False
            #Inne i en behandling, har hentet alle visits til den 
            strVis = self.treatment_df.loc[treatment, 'visit']
            visitList = self.getIntList(strVis)
            #TODO: Hente ut sett av mulig patterns som kan fungere
            self.route_plan.printSoultion()
            print("tester litt")
            print(pattern[self.treatment_df.loc[treatment, 'pattern']])
            count_patterns = 0
            old_route_plan = copy.deepcopy(self.route_plan)
            for treatPat in pattern[self.treatment_df.loc[treatment, 'pattern']]:
                '''
                Mulige route plans burde generes her. Fordi 
                '''
                count_patterns +=1  
                insertState = self.insert_visit_with_pattern(visitList, treatPat) 
                if treatment == 8: 
                    print("StatusTrea")
                    print("state ",insertState)
                if insertState == True:
                   treatStat = True
                   break
                self.route_plan = copy.deepcopy(old_route_plan)
                #Hvis ikke den første fungerer så vil den bare returnere false
                #Dette er det samme problemet som det andre. Return False skal være
                #Hvis det er siste mulige pattern så blir det false 
            if treatStat == False: 
                #Hvis den er false så må self.route_plan settes tilbake til det den var
                return False
        
        #Det er noe med true og false her
        #Jeg tror vi må returne status her. Og sette det på en ny måte
        
        return True
    '''
    Det er noe her med route plan, hvordan det oppdateres. Hvor skal det være
    Construction har en routeplan som lages når det oppdateres 
    Construct kaller en construct initial 
    '''

    #TODO: Visits skal sorteres her for å legge de i prioritert rekkefølge
    #TODO: Det må også velges dag for når det skal gjennomføres 
    #TODO: Her skal en pasient puttes inn i planen. Ma sjekke om det går 

    

    #Denne må returnere False med en gang en ikke fungerer 
    #Det virker som at denne altid returnerer True 
    def insert_visit_with_pattern(self, visits, pattern):
        print(visits)
        print(pattern)
        visit_count = 0
        for day_index in range(len(pattern)): 
            if pattern[day_index] == 1: 
                state = self.insert_visit_on_day(visits[visit_count], day_index+1) 
                if state == False: 
                    return False
                visit_count += 1 
        return True   
                

    #Denne funksjonen oppdatere route_self helt til det ikke går lenger
    def insert_visit_on_day(self, visit, day):  
        strAct = self.visit_df.loc[visit, 'nodes']
        activites = self.getIntList(strAct)
        if visit == 13 or visit == 14: 
            print("activites", activites)
        #print(activites)
        for act in activites: 
            #TODO: Her må det lages en aktivitet objekt 
            acitvity = Acitivity(self.activites_df, act)
            if act == 17: 
                print("test17-1", acitvity.getEarliestStartTime())
            #Sørger for at same employee aktiviteter gjennomføres av samma ansatt
            if acitvity.getSameEmployeeActID() != 0 and acitvity.getSameEmployeeActID() < act: 
                emplForAct = self.route_plan.getEmployeeAllocatedForActivity(acitvity.getSameEmployeeActID(), day)
                otherEmplOnDay = self.route_plan.getOtherEmplOnDay(emplForAct, day)
                acitvity.updateEmployeeRes(otherEmplOnDay) 
                
            for prevNode in acitvity.getPrevNode(): 
                #Finne aktivitetsobjektet 
                print("problemer med denne", acitvity.getID())
                print("prevNode exists ", self.route_plan.checkAcitivyInRoutePlan(prevNode,day))
                prevNodeAct = self.route_plan.getActivity(prevNode, day)
                acitvity.setEarliestStartTime(prevNodeAct.getStartTime()+prevNodeAct.getDuration())

            for PrevNodeInTime in acitvity.getPrevNodeInTime(): 
                prevNodeAct = self.route_plan.getActivity(PrevNodeInTime[0], day)
                acitvity.setLatestStartTime(prevNodeAct.getStartTime()+PrevNodeInTime[1])


            state = self.route_plan.addNodeOnDay(acitvity, day)
            if act == 17: 
                print("test17-2", acitvity.getEarliestStartTime())
                print("start", self.route_plan.routes[day][0].start_time)
                print("slutt", self.route_plan.routes[day][0].end_time)
                #print("dette er status nummer 30", str(state))
            if state == False: 
                return False
        return True
    
    #Problemet her er at vi legger til alle før vi oppdager at det ikke går lenger


    
    #AddNodeOnDay vil bare legge til aktiviteter dersom det går. 
    #Dette er kun et problem i forhold til patterns. For her legger den til i første ierasjo
    
    '''
    Det er bestemt at det skal skje på denne dagen. Hvordan sjekker vi
    Ønsker vi å sjekke om patterns fungerer. Det kan sjekkes ved å slå opp
    '''

    
    def getIntList(self, string):
        if "," in string: 
            stringList = string.split(',')
        else: 
            stringList = [string]
        return  [int(x) for x in stringList]

