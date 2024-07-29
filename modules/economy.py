import numpy as np
import pandas as pd

class ElecPrice:
    def __init__(self, data_path='./data/day_ahead_prices_2022.csv'):
        self.price_data = pd.read_csv(data_path)
        self.max_time = 24*4           # 24 hours of 15 minute intervals
        self.day_num = 1
        self.load_day_measurement()
    
    def load_day_measurement(self):
        self.day_price_data = self.price_data['Day-ahead Price [EUR/MWh]'].iloc[(self.day_num-1)*self.max_time:self.day_num*self.max_time].to_numpy()
        self.day_price_data = np.repeat(self.day_price_data, 4)

    def next_day(self):
        self.day_num += 1
        self.load_day_measurement()

    def step(self, current_time):
        if current_time >= self.max_time: self.next_day()
        return self.day_price_data[current_time]