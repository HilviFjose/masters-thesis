import numpy as np 
import sys
sys.path.append("C:\\Users\\agnesost\\masters-thesis")
from objects.patterns import pattern
from objects.actitivites import Acitivity


class InsertionGenerator:
    def __init__(self, construction_heuristic, route_plan, patients_df):
        #Heuristikken brukes til å hente ut dataframsene. Altså dataverdiene fra de fortåene
        self.heuristic = construction_heuristic   
        #Ruteplanen eksisterer ikke i utganspunktet. Den har blitt laget også sendt inn 
        self.route_plan = route_plan

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
        '''

    def generate_insertions(self):
        state = True
        #TODO: Her skal treaments sorteres slik at man vet hvilke som er mest. 
        #Nå itereres den over i rekkefølge 
        for treatment in self.treatments: 
            #Inne i en behandling, har hentet alle visits til den 
            strVis = self.heuristic.treatment_df.loc[treatment, 'visit']
            visitList = self.getIntList(strVis)
            #TODO: Hente ut sett av mulig patterns som kan fungere
            for treatPat in pattern[self.heuristic.treatment_df.loc[treatment, 'pattern']]: 
                self.insert_visit_with_pattern(visitList, treatPat)

           
            '''
            Første omgang få det til å fungere. 
            Sende inn et sett av paterns. Har pattern 1 
            '''



            #TODO: Visits skal sorteres her for å legge de i prioritert rekkefølge
            #TODO: Det må også velges dag for når det skal gjennomføres 
        #TODO: Her skal en pasient puttes inn i planen. Ma sjekke om det går 
        

        #Nå legger vi til alle mulige aktiviteter i en liste. Det er ikke mulig.
        #Må sende inn et visit med en gitt dag det burde gjøres 
        #De må jo prøve alle mulig patterns. Prøver først et, og hvis det ikke fungerer prøve nytt
        #Det er mulig å printe objekter fra denne klassen 
        return self.route_plan, 0
    
    def insert_visit_with_pattern(self, visits, pattern):
        state = False
        val_day = 1
        for visit in visits: 
            for val in pattern: 
                if val == 1: 
                    self.insert_visit_on_day( visit, val_day)
                    if val_day < 5:
                        val_day += 1
                    break
                if val_day < 5:
                    val_day += 1
        print(visits)
        print(pattern)
        return True 

    def insert_visit_on_day(self, visit, day): 
        print("inserter visit"+str(visit)+"on day"+str(day))
        state = True
        #Hente ut alle de 
        strAct = self.heuristic.visit_df.loc[visit, 'nodes']
        activites = self.getIntList(strAct)
        print(activites)
        for act in activites: 
            #TODO: Her må det lages en aktivitet objekt 
            acitvity = Acitivity(self.heuristic.activities_df, act)
            state = self.route_plan.addNodeOnDay(acitvity, day)
        return state

    def getTreatments(self): 
        return self.treatments
    
    def getPatientDF(self): 
        return self.patients_df
    
    def getIntList(self, string):
        if "," in string: 
            stringList = string.split(',')
        else: 
            stringList = [string]
        return  [int(x) for x in stringList]

'''
Lurer på: hva er selve insertion objektet? Hvorfor er ikke dette en metode i construksjonen? 
Er det fordi den er så stor, så de har lagt den utenfor? Eller er det en egen enhet

Burde tenke litt over hva slags egenskaper den insertionene skal ha.
Vil vi ha det på en spessiell måte. 

Alternativ til slik de har det. Det generes en inserter for hver pasient som skal inn
Insertern har en egen struktur som tar varer på alle de ulike

Kategorisere hva som er metode og hva som er tilstand: 
Vil ha en metode som legger til en pasient 
Det må igjen ha metode som legger til treatments
Legger til visits 
Må ha tilstand i form av at man vet om pasienten kan legges til, og hva som er nåværende ruteplan

Hvor skal ruteplanen inn, den må være en egen enitet som oppdateres 


#TODO: Finne ut om patterns, treatments som er vnaskeligst å plassere skal først. 
Må lage en liste på det for å bestemme hvem som skal insertes når

'''