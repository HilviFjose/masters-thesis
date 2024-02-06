class RoutePlan:
    def __init__(self, days, employeesONday):
        self.routes = [[Route() for d in range(len(days))] for e in range(2)]

    #days er her entall dager, mens employees er en liste over    
    #Jeg tror vi skal ha rutene mer, med tilhørende score for alle rutene her. 
    #Hvis en rute legges til så økes scoren her         

    def getRouteEmployeeDay(employee, day): 
        

'''

Jobber alle ansatte alle dager? 
Nei det gjør de ikke. Så det må bli konstuert av 
I konstuktøren så lages alle parameterne

Skal denne oppdateres jevnlig, eller skal det konstureres nye underveid. 

Den må nesten være indeksert med alle ansatte alle dager. 
Det er ikke en effektiv måte å gjøre det på dersom de har veldig ulike arbeidstimer. 


Alt 1) Dictionary hvor de indekseres med ulike dager og ansatte 
Alt 2) To dimesjonal liste med ruteobjektet. Da må vi ha for alle kombinasjoner 
'''