import random
import numpy as np
import pandas as pd
from collections import deque


class ChargeSpot:
    def __init__(self, name='charger'):
        self.name = name
        self.schedule_vehicles()

    def step(self, current_time):
        return self.availability[current_time]

    def schedule_vehicles(self, day_type='weekday', parking_type='public'):
        if day_type not in ['weekday', 'weekend']:
            raise ValueError("day_type must be 'weekday' or 'weekend'")
        if parking_type not in ['private', 'public', 'workplace']:
            raise ValueError("parking_type must be 'private', 'public', 'workplace'")

        # Select the correct CSV file based on the day type
        file_path = f'./workplaces/distribution-of-arrival_{day_type}.csv'
        df_arrival = pd.read_csv(file_path, delimiter=',', decimal=',')
        
        # Get the probability distribution for the specified parking type
        column = parking_type
        prob = df_arrival[column].to_numpy() / np.sum(df_arrival[column].to_numpy())
        
        # Create the flipped probability distribution
        new_prob = np.flip(prob).copy()
        new_prob[13*4:] = np.flip(prob[:13*4])[:(24-13)*4]
        
        # Round the probabilities
        prob = np.round(prob, 2)
        new_prob = np.round(new_prob, 2)

        # Normalize the probabilities
        prob /= np.sum(prob)
        new_prob /= np.sum(new_prob)
        
        self.arrival_time = np.inf
        self.departure_time = 0

        # Sample Gaussian distributions for arrival and departure times
        while not ((self.departure_time-self.arrival_time > 6*4) or (0<self.arrival_time-self.departure_time < (24-6)*4)):
            self.arrival_time = np.random.choice(np.arange(len(prob)), 1, p=prob)
            self.departure_time = np.random.choice(np.arange(len(prob)), 1, p=new_prob)
        
        self.availability = np.zeros((24*4,))
        # Create the availability array for 24 hours
        if self.departure_time > self.arrival_time:
            self.availability[self.arrival_time.item():self.departure_time.item()] = 1
        else:
            self.availability[self.arrival_time.item():] = 1
            self.availability[:self.departure_time.item()] = 1
        
    # def schedule_vehicles(self):  
    #         file_path = './workplaces/distribution-of-arrival_weekday.csv'  # Replace with your file path
    #         df_arrival_weekday = pd.read_csv(file_path, delimiter=',', decimal=',')
    #         column='workplace'
    #         prob = df_arrival_weekday[column].to_numpy()/np.sum(df_arrival_weekday[column].to_numpy())

    #         new_prob = np.flip(prob).copy()
    #         new_prob[13*4:] = np.flip(prob[:13*4])[:(24-13)*4]
            
    #         prob = np.round(prob,2)
    #         new_prob = np.round(new_prob,2)

    #         prob /= np.sum(prob)
    #         new_prob /= np.sum(new_prob)
            
    #         self.arrival_time = 0
    #         self.departure_time = 0
    #         # sampling gaussian distributions
    #         while np.abs(self.departure_time-self.arrival_time) < 6*4:
    #             self.arrival_time = np.random.choice(np.arange(len(prob)), 1, p=prob)
    #             self.departure_time = np.random.choice(np.arange(len(prob)), 1, p=new_prob)
            
    #         self.availability = np.zeros((24*4))
    #         # availability array for 24 hours
    #         if self.departure_time > self.arrival_time:
    #             self.availability[self.arrival_time.item():self.departure_time.item()] =  1
    #         else:
    #             self.availability[self.arrival_time.item():] =  1
    #             self.availability[:self.departure_time.item()] =  1


    # def schedule_vehicles(self):
    #     arrival_mean = 10*4
    #     arrival_std = 1*4
    #     departure_mean = 18*4
    #     departure_std = 1*4
    #     # sampling gaussian distributions
    #     self.arrival_time = int(np.random.normal(arrival_mean, arrival_std))
    #     self.departure_time = int(np.random.normal(departure_mean, departure_std))
    #     # availability array for 24 hours
    #     self.availability = np.zeros((24*4,))
    #     self.availability[self.arrival_time:self.departure_time] =  1

class EVParkingLot:
    def __init__(self, num_chargers=4):
        self.num_chargers = num_chargers
        self.chargers = [ChargeSpot(name=f'charger {i}') for i in range(self.num_chargers)]
        # self.arrival_samples = None
        # self.departure_samples = None
        # self.required_powers = None
        # history
        self.max_time = 24*4 # 24 hours of 15 minute intervals
        self.iniialize_buffer()
        self.reset_day()

    def iniialize_buffer(self):
        self.p_grid_history = deque(maxlen=self.max_time)
        self.p_grid_history.extend(np.zeros(self.max_time,))

        self.p_storage_history = deque(maxlen=self.max_time)
        self.p_storage_history.extend(np.zeros(self.max_time,))

        self.p_chargers_history = deque(maxlen=self.max_time)
        self.p_chargers_history.extend(np.zeros((self.max_time,self.num_chargers)))

        self.p_pv_history = deque(maxlen=self.max_time)
        self.p_pv_history.extend(np.zeros(self.max_time,))

        self.price_history = deque(maxlen=self.max_time)
        self.price_history.extend(np.zeros(self.max_time,))

        self.storage_energy = deque(maxlen=self.max_time)
        self.storage_energy.extend(np.ones(self.max_time,)*0.5)

        self.avalability_history = deque(maxlen=self.max_time)
        self.avalability_history.extend(np.zeros((self.max_time,self.num_chargers)))

    def reset_day(self):
        for i in range(self.num_chargers):
            self.chargers[i].schedule_vehicles()

    def step(self, current_time, grid_power, storage_power, charger_powers, pv_power, e_price, storage_energy):
        if current_time >= self.max_time: self.reset_day()
        self.p_grid_history.append(grid_power)
        self.p_storage_history.append(storage_power)
        self.p_chargers_history.append(charger_powers)
        self.p_pv_history.append(pv_power)
        self.price_history.append(e_price)
        self.storage_energy.append(storage_energy)
        self.avalability_history.append([self.chargers[i].step(current_time) for i in range(self.num_chargers)])
        

    def get_histories(self):
        histories = np.hstack(
            [np.array(self.p_chargers_history).reshape(self.max_time,-1),
             np.array(self.p_grid_history).reshape(self.max_time,-1),
             np.array(self.p_storage_history).reshape(self.max_time,-1),
             np.array(self.p_pv_history).reshape(self.max_time,-1),
             np.array(self.storage_energy).reshape(self.max_time,-1),
             np.array(self.price_history).reshape(self.max_time,-1)]
                               )
        return histories


class EvDemandGenerator:
    def __init__(self, data_path='./data/rvo_top_10.xlsx'):
        self.data = pd.read_excel(data_path)
        self.data = self.data[self.data['model'] != 'total']
        # extract the data
        self.models = self.data['model'].to_numpy()
        self.demands = self.data['number'].to_numpy()
        self.probs = self.data['probability'].to_numpy()

    def generate_demand(self, num_vehicles):
        # non-uniform distribution
        idx = np.random.choice(np.arange(len(self.models)), num_vehicles, p=self.probs, replace=False)
        return np.expand_dims(self.demands[idx], 0)/1000
        # [{'model': vehicle_models[i], 'demand':demand[i]} for i in idx]