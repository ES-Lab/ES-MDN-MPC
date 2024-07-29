import numpy as np
import pandas as pd
from collections import deque

class PVpanel:
    def __init__(self):
        pass

class PVdata:
    def __init__(self, data_path='./data/timeseries-slimpark-2022.csv'):
        self.PV_data = pd.read_csv(data_path, parse_dates=['Time'], index_col='Time')
        self.day_samples = 24*60*6                                                      # Number of samples per day (every 10 seconds)
        self.sample_time = '15min'                                                      # Resampling interval (every 15 minutes)
        self.max_time = 24*4                                                            # 24 hours of 15 minute intervals
        self.resampled_data = self.resample_data()[self.max_time*200:]
        self.day_num = 1
        self.load_day_measurement()

    def resample_data(self):
        # Resample the data to every 15 minutes, using the mean value for each interval
        return self.PV_data.resample(self.sample_time).mean()
    
    def load_day_measurement(self):
        self.day_data = -self.resampled_data['solar_measurement'].iloc[(self.day_num-1)*self.max_time:self.day_num*self.max_time].to_numpy()

    def next_day(self):
        self.day_num += 1
        self.load_day_measurement()

    def step(self, current_time):
        if current_time >= self.max_time: self.next_day()
        return self.day_data[current_time]
