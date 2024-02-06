class DistanceMatrix:
    def __init__(self, days, employeesONday):
        self.routes = [[Route() for d in range(len(days))] for e in range(2)]

    #days er her entall dager, mens employees er en liste over             

    def getRouteEmployeeDay(employee, day): 
        