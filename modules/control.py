import cvxpy as cp
import numpy as np
from collections import deque

class MPC:
    def __init__(self, num_chargers=4, sample_time=0.25, storage_capacity=30,
                 capacity_high_limit=0.8, capacity_low_limit=0.2, p_storage_limit=14, p_charger_limit=11):
        self.num_chargers = num_chargers
        self.sample_time = sample_time
        self.storage_capacity = storage_capacity
        self.capacity_high_limit = capacity_high_limit
        self.capacity_low_limit = capacity_low_limit
        self.p_storage_limit = p_storage_limit
        self.p_charger_limit = p_charger_limit

        
        self.shift = 2 * int(1/self.sample_time)  # 2 hours * resolution

    def reset_day(self, p_pv_data,
                    p_grid, 
                    p_storage,
                    ev_demand_initial,
                    storage_energy_initial,
                    p_chargers,
                    charger_availability_data):
        
        self.p_pv_data = np.hstack([np.zeros((1,)), p_pv_data])/1000                 # PV power generation over time in kW
        self.charger_availability_data = np.vstack([np.heaviside(p_chargers,0).reshape(1,self.num_chargers),
                                                    charger_availability_data])      # Charger availability over time in hours
        self.buffer = {
            'p_grid':           p_grid.reshape(1,)/1000,
            'p_storage':        p_storage.reshape(1,)/1000,
            'storage_energy':   storage_energy_initial,
            'p_chargers':       p_chargers.reshape(1,self.num_chargers)/1000,
            'remaining_demand': ev_demand_initial,
        }

    def step(self, current_time, storage_energy_initial):
        # define window data
        p_pv_window = self.p_pv_data[current_time:]
        charger_availability_window = self.charger_availability_data[current_time:]
        horizon = len(p_pv_window)  # 24 hours * resolution

        # Initialize parameters
        self.p_grid_initial = cp.Parameter(1, nonneg=True, value=np.clip(self.buffer['p_grid'][-1:], 0, np.inf))
        self.p_storage_initial = cp.Parameter(1, value=np.clip(self.buffer['p_storage'][-1:], -self.p_storage_limit, self.p_storage_limit))
        self.p_chargers_initial = cp.Parameter(self.num_chargers, nonneg=True, value=np.clip(self.buffer['p_chargers'][-1,:], 0, self.p_charger_limit))
        self.storage_energy_initial = cp.Parameter(1, nonneg=True, value=np.clip(storage_energy_initial, 
                                                                                 self.storage_capacity*self.capacity_low_limit, 
                                                                                 self.storage_capacity*self.capacity_high_limit))

        self.ev_demand = cp.Parameter(self.num_chargers, nonneg=True, value=np.clip(self.buffer['remaining_demand'][-1,:], 0, np.inf))
        self.charger_availability = cp.Parameter((horizon, self.num_chargers), boolean=True, value=charger_availability_window)

        # Initialize decision variables
        self.p_chargers = cp.Variable((horizon, self.num_chargers), nonneg=True)
        self.p_grid = cp.Variable(horizon, nonneg=True)
        self.p_storage = cp.Variable(horizon)
        self.storage_energy = cp.Variable(horizon, nonneg=True)
        self.slack = cp.Variable(horizon)  # Slack variable for power balance constraints

        # Constraints
        constraints = []

        # Charger availability constraints
        constraints.append(self.p_chargers <= self.charger_availability*self.p_charger_limit)

        # Power balance constraints
        constraints.append(p_pv_window + self.p_grid + self.p_storage + self.slack == cp.sum(self.p_chargers, axis=1))

        # Storage constraints
        constraints.append(self.storage_energy <= self.storage_capacity * self.capacity_high_limit)
        constraints.append(self.storage_energy >= self.storage_capacity * self.capacity_low_limit)
        constraints.append(self.p_storage <= self.p_storage_limit)
        constraints.append(self.p_storage >= -self.p_storage_limit)

        # Initial conditions
        constraints.append(self.p_grid[0] == self.p_grid_initial)
        constraints.append(self.p_storage[0] == self.p_storage_initial)
        constraints.append(self.p_chargers[0] == self.p_chargers_initial)
        constraints.append(self.storage_energy[0] == self.storage_energy_initial)
        constraints.append(self.storage_energy[-1] == self.storage_capacity/2)

        constraints.append(self.storage_energy[1:] == self.storage_energy[:-1] - self.p_storage[1:]*self.sample_time)

        # EV demand constraints
        constraints.append(cp.sum(self.p_chargers[1:]*self.sample_time, axis=0) == self.ev_demand)

        # Smoothing constraint to avoid abrupt changes: total variations
        smoothing_penalty = cp.tv(self.p_grid) + 5*cp.tv(self.p_storage) + cp.tv(self.p_chargers)

        # Objective: Minimize total grid power usage
        objective = cp.Minimize(cp.sum(self.p_grid**2) + cp.sum(self.slack**2)*1e3 + smoothing_penalty*10)

        # Problem definition and solving
        problem = cp.Problem(objective, constraints)
        problem.solve(solver=cp.SCS)
        
        # apply dynamics of storage and demands
        storage_energy_samples = self.buffer['storage_energy'][-1] -\
                            np.cumsum(np.array(self.p_storage.value)[1:1+self.shift])*self.sample_time
        ev_demand_samples = self.buffer['remaining_demand'][-1].reshape(1,4) -\
                            np.cumsum(np.array(self.p_chargers.value)[1:1+self.shift,:], axis=0)*self.sample_time

        # Store results
        self.buffer['p_grid'] = np.hstack([self.buffer['p_grid'], np.array(self.p_grid.value)[1:1+self.shift]])
        self.buffer['p_storage'] = np.hstack([self.buffer['p_storage'], np.array(self.p_storage.value)[1:1+self.shift]])
        self.buffer['p_chargers'] = np.vstack([self.buffer['p_chargers'], np.array(self.p_chargers.value)[1:1+self.shift,:]])
        self.buffer['storage_energy'] = np.hstack([self.buffer['storage_energy'], storage_energy_samples])
        self.buffer['remaining_demand'] = np.vstack([self.buffer['remaining_demand'], ev_demand_samples])

        # Output the results
        if problem.status not in ["infeasible", "unbounded"]:
            return {
                "status": problem.status,
                "objective_value": objective.value,
                "p_chargers": np.array(self.p_chargers.value)[1:1+self.shift,:],
                "p_grid": np.array(self.p_grid.value)[1:1+self.shift],
                "p_storage": np.array(self.p_storage.value)[1:1+self.shift],
            }
        else:
            print("The problem is infeasible or unbounded.")