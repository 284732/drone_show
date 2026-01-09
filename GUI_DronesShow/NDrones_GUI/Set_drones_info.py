from GUI_DronesShow.GUI_objects import *
from tkinter import Toplevel

""" 
    In this file will be defined the drones configuration GUI.
    The user can insert:
    - Initial position of the i-th drone (X, Y, Z).
    - Max velocity of the i-th drone.
    - Max acceleration of the i-th drone.
    All the info are packed in a json file to be used for trajectory generation.
    
    The initialPositionList function provides a list of default initial positions
    for the drones, in case the user wants to use them.
"""

global drone_config
drone_config = {}


def initialPositionList(n_drones):
    initial_positions = []
    actual_position = [0.0, 0.0, 2.0]

    for _ in range(n_drones):
        initial_positions.append(actual_position.copy()) # Append a copy of the current position

        if actual_position[0] < 12.0:
            actual_position[0] += 3.0
        else:
            actual_position[1] += 3.0
            actual_position[0] = 0.0

    return initial_positions


class DroneInfoGUI(Toplevel):
    def __init__(self, parent, drone_id, default_X, default_Y):
        super().__init__(parent)  # Initialize the Tkinter root window

        self.drone_id = drone_id
        self.title(f"Drone {self.drone_id} Configuration")
        self.geometry("300x400")
        self.resizable(False, False)
        keyString = f"drone {self.drone_id}"
        drone_config[keyString] = {}

        self.drone_i_frame = tk.LabelFrame(self, text=f'Drone {self.drone_id} Configuration',
                                           padx=5, pady=5)
        self.drone_i_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        self.entry_x = EntryFloat(self.drone_i_frame,
                                  'Initial X position (m):',
                                  0, 0)
        self.entry_x.insert(0, str(default_X))

        self.entry_y = EntryFloat(self.drone_i_frame,
                                  'Initial Y position (m):',
                                  1, 0)
        self.entry_y.insert(0, str(default_Y))

        self.entry_z = EntryFloat(self.drone_i_frame,
                                  'Initial Z position (m):',
                                  2, 0)
        self.entry_z.insert(0, '2.0') # Default value

        self.entry_max_vel = EntryFloat(self.drone_i_frame,
                                        'Max Velocity (m/s):',
                                        3, 0)
        self.entry_max_vel.insert(0, '20.0') # Default value

        self.entry_max_acc = EntryFloat(self.drone_i_frame,
                                        'Max Acceleration (m/s²):',
                                        4, 0)
        self.entry_max_acc.insert(0, '20.0') # Default value

        """ Add to the dictionary the values inserted by the user. """
        self.confirm_button = CommandButton(self.drone_i_frame,
                                            'Confirm',
                                            self.confirm_drone_parameters,
                                            'dark green',
                                            'white',
                                            5, 0)


    def confirm_drone_parameters(self):
        drone_config[f"drone {self.drone_id}"]['initial_position'] = [self.entry_x.get_float(),
                                                                     self.entry_y.get_float(),
                                                                     self.entry_z.get_float()]
        drone_config[f"drone {self.drone_id}"]['max_velocity'] = self.entry_max_vel.get_float()
        drone_config[f"drone {self.drone_id}"]['max_acceleration'] = self.entry_max_acc.get_float()

        self.destroy()