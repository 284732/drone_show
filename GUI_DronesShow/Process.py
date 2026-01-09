from NDrones_GUI.N_drones_GUI import NDronesGUI
from NDrones_GUI.Set_drones_info import DroneInfoGUI, initialPositionList, drone_config
import tkinter as tk
import json
import os
import time
import coppeliasim_zmqremoteapi_client

""" 
    This file will contain the main process of the Drone Show application. 
"""

mainRoot = tk.Tk()
mainRoot.withdraw()  # Hide the main root window

# Open the NDronesGUI to select the number of drones
nDrones_window = NDronesGUI(mainRoot)
mainRoot.wait_window(nDrones_window)  # Wait until the NDronesGUI window is closed
numberOfDrones = nDrones_window.get_number_of_drones()

initialPosition = initialPositionList(numberOfDrones)

# Open a DroneInfoGUI for each drone to configure its parameters
for i in range(numberOfDrones):
    drone_config_GUI = DroneInfoGUI(mainRoot, i + 1, initialPosition[i][0], initialPosition[i][1])
    mainRoot.wait_window(drone_config_GUI)  # Wait until the DroneInfoGUI window is closed

print(drone_config)





