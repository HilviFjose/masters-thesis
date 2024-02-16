

class SimulatedAnnealing:
    def __init__(self, start_temperature, end_temperature, cooling_rate):
        self.start_temperature = start_temperature
        self.end_temperature = end_temperature
        self.cooling_rate = cooling_rate
        self.temperature = start_temperature