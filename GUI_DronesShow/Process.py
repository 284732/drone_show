from NDrones_GUI.N_drones_GUI import NDronesGUI
from NDrones_GUI.Set_drones_info import DroneInfoGUI, initialPositionList, drone_config
from ShowSequence_GUI.numberOfSteps_GUI import numberOfStepsGUI
from ShowSequence_GUI.ShapeChoice_GUI import ShapeSelectionGUI
from ShowSequence_GUI.ConfigurationShape_GUI import ConfigurationShapeGUI
from utils import close_all
import tkinter as tk
import coppeliasim_zmqremoteapi_client

""" 
    This file will contain the main process of the Drone Show application. 
"""


mainRoot = tk.Tk()
mainRoot.withdraw()  # Hide the main root window
icon = tk.PhotoImage(file="drone_32x32.png")
mainRoot.iconphoto(True, icon)
mainRoot.protocol("WM_DELETE_WINDOW", close_all)

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

""" Starts the show sequence configuration. """
showSequence_window = numberOfStepsGUI(mainRoot)
mainRoot.wait_window(showSequence_window)  # Wait until the numberOfStepsGUI window is closed
numberOfSteps = showSequence_window.get_n_ofSteps()

""" Opens the shape configuration window. """
shapeList_window = ShapeSelectionGUI(mainRoot, numberOfSteps, numberOfDrones)
mainRoot.wait_window(shapeList_window)  # Wait until the ConfigurationShapeGUI window is closed
shapeList = shapeList_window.get_shape()
shapeList_dict = shapeList_window.get_list_dict()

""" Fills the shape_dict with the selected shapes for each step. """
for step_i in range(numberOfSteps):
    shapeConfig_window = ConfigurationShapeGUI(mainRoot, step_i, shapeList[step_i], shapeList_dict)
    mainRoot.wait_window(shapeConfig_window)  # Wait until the ConfigurationShapeGUI window is closed

shape_dict = shapeConfig_window.get_shape_dict() # Get the final shape_dict from the last shapeConfig_window
print(shape_dict)





