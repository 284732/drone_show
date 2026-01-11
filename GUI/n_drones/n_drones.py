from GUI.droneShow_obj.obj_GUI import *
from GUI.utils import close_all
from tkinter import Toplevel

""" 
    In this file will be defined the drones configuration GUI.
    It will allow the user to select the number of drones and configure them.
    In case the user doesn't select any value, default values will be used. 
"""

class NDronesGUI(Toplevel):
    def __init__(self, parent):
        super().__init__(parent) # Initialize the Tkinter root window

        self.title("Drone Show")
        self.geometry("300x100")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", close_all)

        self.config_frame = tk.Frame(self)
        self.config_frame.grid(row=0, column=0, sticky="nsew")
        self.n_ofDrones = 0
        self.check = False

        """ Create the Spinbox for selecting number of drones. """
        self.nDrones_spinbox = SpinBox(self.config_frame,
                                'Select the number of drones:',
                                       1, 200,
                                        0, 0)

        self.button_frame = tk.Frame(self.config_frame)
        self.button_frame.grid(row=1, column=0, sticky="nsew")

        """ Create the Confirm button. """
        self.configuration_button = CommandButton(self.button_frame,
                                            'Configure',
                                            self.confirm_number_of_drones,
                                            'light grey',
                                            'black',
                                            0, 1)

        """ Confirm button. """
        self.confirm_button = CommandButton(self.button_frame,
                                            'Confirm',
                                            self.confirm_configuration,
                                            'dark green',
                                            'white',
                                            0, 0)

    def confirm_number_of_drones(self):
        self.n_ofDrones = int(self.nDrones_spinbox.get())
        self.destroy()

    def confirm_configuration(self):
        self.n_ofDrones = int(self.nDrones_spinbox.get())
        self.check = True
        self.destroy()

    def get_number_of_drones(self):
        return self.n_ofDrones

    def get_check(self):
        return self.check