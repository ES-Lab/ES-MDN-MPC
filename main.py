from modules.parking import EVParkingLot
from modules.parking import EvDemandGenerator
from modules.solar import PVdata
from modules.economy import ElecPrice
from modules.storage import Battery
from modules.control import MPC
from assets.GUI import MainWindow
from assets.clock import Clock

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
import numpy as np
import threading
import time

# THREADS
def GUI_plot_thread_fcn():
    current_time = clock.get_time()
    # time_list = clock.get_time_list()
    # x_ticks = [(i, str(j)) for i,j in zip(dash_board.x[::16], time_list[::16])]
    # dash_board.x = clock.get_time_list()
    histories = parking_lot.get_histories()
    for i in range(9):
        dash_board.curves[i].setData(dash_board.x, histories[:,i])
        dash_board.fills[i].setCurves(dash_board.curves[i], pg.PlotCurveItem(dash_board.x, np.zeros_like(dash_board.x)))
        dash_board.v_lines[i].setPos(24-current_time/4)
    # dash_board.plot_items[0].getAxis('bottom').setTicks([x_ticks])

    dash_board.update_demands(mpc.buffer['remaining_demand'][current_time])

def parking_thread_fcn():
    while True:
        current_time = clock.get_time()
        if current_time==0:
            PV_panel.next_day()
            elec_price.next_day()
            parking_lot.reset_day()
            ev_demand_initial = ev_demand_generator.generate_demand(4)
            storage_energy_initial = np.array([battery.capacity]) / 2
            charger_availability_data = np.hstack([parking_lot.chargers[i].availability.reshape(-1,1) for i in range(parking_lot.num_chargers)])
            mpc.reset_day(PV_panel.day_data, 
                          parking_lot.p_grid_history[-1],
                          parking_lot.p_storage_history[-1],
                          ev_demand_initial, 
                          storage_energy_initial, 
                          parking_lot.p_chargers_history[-1],
                          charger_availability_data)

        if current_time%mpc.shift == 0:
            storage_energy = np.array([battery.SOC*battery.capacity])
            mpc.step(current_time, storage_energy)
        
        pv_power_t = PV_panel.step(current_time)
        e_price_t = elec_price.step(current_time)
        SoC_t = battery.step(mpc.buffer['p_storage'][current_time+1])
        parking_lot.step(current_time, 
                         mpc.buffer['p_grid'][current_time+1]*1000, 
                         mpc.buffer['p_storage'][current_time+1]*1000,
                         mpc.buffer['p_chargers'][current_time+1]*1000, 
                         pv_power_t, 
                         e_price_t,
                         SoC_t)

        clock.tick()
        time.sleep(0.1)  # Perform other tasks every second
  
# def MPC_thread_fcn():
#     while True:
#         current_time = clock.get_time()
#         if current_time==0:
#             PV_panel.next_day()
#             parking_lot.reset_day()
#             ev_demand_initial = np.array([[55, 50, 35, 65]]) # Example EV demand
#             storage_energy_initial = np.array([battery.capacity]) / 2
#             charger_availability_data = np.hstack([parking_lot.chargers[i].availability.reshape(-1,1) for i in range(parking_lot.num_chargers)])
#             mpc.reset_day(PV_panel.day_data, ev_demand_initial, storage_energy_initial, charger_availability_data)

#         if current_time%mpc.shift == 0:
#             mpc.step(current_time)
#         time.sleep(0.1)  # Perform other tasks every second

# Initialize the parking lot
clock = Clock()
parking_lot = EVParkingLot()
pv_data_path = './data/timeseries-slimpark-2022.csv'
price_data_path='./data/day_ahead_prices_2022.csv'
PV_panel = PVdata(pv_data_path)
elec_price = ElecPrice(price_data_path)
battery = Battery(SOC=0.5)
ev_demand_generator = EvDemandGenerator()
mpc = MPC()


# Initialize the dashboard
app = QApplication(sys.argv)
dash_board = MainWindow()
dash_board.show()

# Set up a timer to update the plots
timer = QTimer()
timer.setInterval(50)  # update every 50 ms
timer.timeout.connect(GUI_plot_thread_fcn)
timer.start()

# # Here you can run other tasks in parallel
# MPC_thread = threading.Thread(target=MPC_thread_fcn)
# MPC_thread.daemon = True  # Ensure thread exits when the application does
# MPC_thread.start()

# Here you can run other tasks in parallel
parking_thread = threading.Thread(target=parking_thread_fcn)
parking_thread.daemon = True  # Ensure thread exits when the application does
parking_thread.start()



sys.exit(app.exec_())