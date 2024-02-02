        
class InsertionGenerator:
    def __init__(self, construction_heuristic):
        self.heuristic = construction_heuristic
    
    def generate_insertions(self, activity):
        #Her skal på en måte alle restriksjonene inn
        possible_insertions = {}
        
        