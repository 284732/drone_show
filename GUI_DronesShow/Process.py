from GUI_DronesShow.NDrones_GUI.N_drones_GUI import NDronesGUI
from GUI_DronesShow.NDrones_GUI.Set_drones_info import DroneInfoGUI, initialPositionList, drone_config
from export_file.config_exporter_GUIof_drones import export_drones_config_to_yaml
import tkinter as tk

""" 
    This file will contain the main process of the Drone Show application. 
"""
icon_path = "GUI_DronesShow/drone_32x32.png"
mainRoot = tk.Tk()
mainRoot.withdraw()  # Hide the main root window
icon = tk.PhotoImage(file=icon_path)
mainRoot.iconphoto(True, icon)

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
            "initial_position": initialPosition[i],
            "max_velocity": 20.0,
            "max_acceleration": 20.0
        }
else:
    for i in range(numberOfDrones):
        drone_config_GUI = DroneInfoGUI(mainRoot, i + 1, initialPosition[i][0], initialPosition[i][1])
        mainRoot.wait_window(drone_config_GUI)  # Wait until the DroneInfoGUI window is closed

# Esporta nella cartella config/ principale
export_drones_config_to_yaml(drone_config, "config/drone_config.yaml")

mainRoot.destroy()