# GUI/Process.py
from GUI.n_drones.n_drones import NDronesGUI
from GUI.n_drones.set_drones_info import DroneInfoGUI, initialPositionList, drone_config
from GUI.show_sequence.n_steps import numberOfStepsGUI
from GUI.show_sequence.shape_choice import ShapeSelectionGUI
from GUI.show_sequence.shape_config import ConfigurationShapeGUI
from GUI.utils import close_all
from export_file.config_exporter_GUIof_drones import export_drones_config_to_yaml
from export_file.config_exporter_show import export_show_config_to_yaml
import tkinter as tk

""" 
    This file will contain the main process of the Drone Show application. 
"""

mainRoot = tk.Tk()
mainRoot.withdraw()  # Hide the main root window

try:
    icon = tk.PhotoImage(file="GUI/drone_32x32.png")
    mainRoot.iconphoto(True, icon)
except:
    pass  # Ignora se l'icona non esiste

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

# Export drone configuration to YAML
export_drones_config_to_yaml(drone_config, output_path="config/drone_config.yaml")

""" Starts the show sequence configuration. """
showSequence_window = numberOfStepsGUI(mainRoot)
mainRoot.wait_window(showSequence_window)  # Wait until the numberOfStepsGUI window is closed
numberOfSteps = showSequence_window.get_n_ofSteps()

""" Opens the shape configuration window. """
shapeList_window = ShapeSelectionGUI(mainRoot, numberOfSteps, numberOfDrones)
mainRoot.wait_window(shapeList_window)  # Wait until the ShapeSelectionGUI window is closed
shapeList = shapeList_window.get_shape()
shapeList_dict = shapeList_window.get_list_dict()

""" Fills the shape_dict with the selected shapes for each step. """
# IMPORTANTE: Usare una variabile condivisa per shape_dict
shape_dict = shapeList_dict  # Inizializza con il dizionario base

for step_i in range(numberOfSteps):
    # Passa shape_dict che viene aggiornato ad ogni iterazione
    shapeConfig_window = ConfigurationShapeGUI(mainRoot, step_i, shapeList[step_i], shape_dict)
    mainRoot.wait_window(shapeConfig_window)  # Wait until the ConfigurationShapeGUI window is closed
    # Aggiorna shape_dict con i nuovi dati
    shape_dict = shapeConfig_window.get_shape_dict()

# Export show configuration to YAML
export_show_config_to_yaml(shape_dict, output_path="config/show_config.yaml")

print("\n✅ Configurazione completata!")
print("   - Droni: config/drone_config.yaml")
print("   - Show: config/show_config.yaml")

# NON distruggere mainRoot qui - lascia che sia il main.py a farlo
# mainRoot.destroy()