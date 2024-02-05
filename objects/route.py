import numpy as np

class Route:
    def __init__(self, employee):
        self.travel_time = 0
        self.start_time = employee.getShiftStart() 
        self.end_time = employee.getShiftEnd()
        self.route = np.array([(0, employee.getShiftStart()),(0, employee.getShiftEnd())])
        self.skillreq = employee.getSkillreq()


    def add_node(activity):  
        for i in range(len(self.route)-1): 
            before_node = self.route[i]
            after_node = self.route[i+1]
            if before_node[1] + Duration[before_node[0]] + T_ij[before_node[0]][activity] + Duration[activity] + T_ij[activity][after_node[0]] <= after_node[1]:
                self.route = np.insert(self.route, i, (activity, Duration[activity]))
                return True
        return False 

#Du må rekke å begynne på aktiviteten før 

#TODO: Er aktivtet et objekt eller en
#TODO: Må finne ut hvordanman aksesserer duration og T_ij herfra 
#TODO: Legge til skillrequirement 
        

'''
Uganspunkt for klassen: Dette er rute for en spessifikk ansatt, med starttidspunkt og slutttidspunkt. 
Det er allerde gitt 


Skal vi her anta at vi allerde har sjekket om noden skal settes inn? 
Hvor skal det sjekkes hvorvidt noe skal legges inn eller ikke? 



'''
