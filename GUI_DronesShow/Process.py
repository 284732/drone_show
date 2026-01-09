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

if nDrones_window.get_check():
    # Impose the default configuration and confirm
    for i in range(numberOfDrones):
        keyString = f"drone {i + 1}"
        drone_config[keyString] = {
            "initial_position": [initialPosition[i][0], initialPosition[i][1], 2.0],
            "max_velocity": 20.0,
            "max_acceleration": 20.0
        }
else:
    for i in range(numberOfDrones):
        drone_config_GUI = DroneInfoGUI(mainRoot, i + 1, initialPosition[i][0], initialPosition[i][1])
        mainRoot.wait_window(drone_config_GUI)  # Wait until the DroneInfoGUI window is closed

print(drone_config)





