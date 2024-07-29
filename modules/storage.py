import numpy as np
from collections import deque

class Battery:
    def __init__(self, SOC):
        # Parameters
        self.eta_charge = 0.95
        self.eta_discharge = 0.95
        self.capacity = 30 # kWh
        # Constraints
        self.Pbatt_max = 14 # kW
        self.SOC_min = 0.2
        self.SOC_max = 0.9
        # Variables
        self.SOC = np.clip(SOC, self.SOC_min, self.SOC_max)
        self.sample_time = 1/4 # 15 minutes
        # Buffer
        self.max_time = 24 * 4 # 24 hours of 15 minute intervals

    def reset(self):
        self.SOC = 0.5

    def step(self, Pbatt):
        # if current_time >= self.max_time: self.reset()

        self.SOC -= (1/self.eta_discharge/self.capacity)*np.maximum(0, Pbatt)*self.sample_time +\
                    (self.eta_charge/self.capacity)*np.minimum(0, Pbatt)*self.sample_time
                    
        self.SOC = np.clip(self.SOC, self.SOC_min, self.SOC_max)
        return self.SOC