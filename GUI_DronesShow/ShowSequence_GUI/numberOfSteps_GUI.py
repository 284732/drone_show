from GUI_DronesShow.droneShow_GUI_obj.GUI_objects import *
from tkinter import Toplevel

""" 
    In this file will be defined the main GUI for showing the sequence
    of the drones show.
"""

class numberOfStepsGUI(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)  # Initialize the Tkinter root window

        self.title('Number of steps - Show configuration')
        self.geometry("300x100")
        self.resizable(False, False)
        self.n_ofSteps = 0

        self.config_frame = tk.Frame(self)
        self.config_frame.grid(row=0, column=0, sticky="nsew")

        """ Create the Spinbox for selecting number of steps. """
        self.nSteps_spinbox = SpinBox(self.config_frame,
                                       'Select the number of steps:',
                                        1, 5,
                                        0, 0)

        self.button_frame = tk.Frame(self.config_frame)
        self.button_frame.grid(row=1, column=0, sticky="nsew")

        """ Create the Confirm button. """
        self.confirm_button = CommandButton(self.button_frame,
                                            'Confirm',
                                            self.confirm_shape,
                                            'dark green',
                                            'white',
                                            1, 0)


    def confirm_shape(self):
        self.n_ofSteps = int(self.nSteps_spinbox.get())
        self.destroy()

    def get_n_ofSteps(self):
        return self.n_ofSteps