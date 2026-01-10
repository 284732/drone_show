from GUI_DronesShow.droneShow_GUI_obj.GUI_objects import *
from GUI_DronesShow.ShowSequence_GUI.shapeDictionary import *
from GUI_DronesShow.utils import close_all
import tkinter as tk
from tkinter import Toplevel, messagebox

""" 
    This file will contain the GUI for the shape selection.
    The user can select the shape for each step of the show sequence.
"""

class ShapeSelectionGUI(Toplevel):
    def __init__(self, parent, n_steps, n_ofDrones):
        super().__init__(parent)  # Initialize the Tkinter root window

        self.shape = []
        self.n_steps = n_steps
        self.n_ofDrones = n_ofDrones
        self.list_dict = {}
        self.title(f'Shape Configuration')
        self.geometry('300x300')
        self.resizable(False, True)
        self.protocol("WM_DELETE_WINDOW", close_all)

        self.config_frame = tk.LabelFrame(self,
                                          text=f'Configuration of the shape sequence',
                                          padx=5, pady=5)
        self.config_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        """ Create the Combobox for selecting shape type. """
        self.comboBox_list = [] # List to hold comboboxes for each step
        for step in range(self.n_steps):
            combobox_shape_i = ComboBox(self.config_frame,
                                           f'Select the shape {step + 1} type:',
                                           SHAPES,
                                           step, 0)
            self.comboBox_list.append(combobox_shape_i)



        self.confirm_button = CommandButton(self.config_frame,
                                            'Confirm',
                                            self.confirm_shape,
                                            'dark green',
                                            'white',
                                            self.n_steps, 0)


    def confirm_shape(self):
        self.shape = [combobox.get() for combobox in self.comboBox_list]

        if None in self.shape or '' in self.shape:
            tk.messagebox.showerror('Error', 'Shape Selection Error')
            return # Do not close the window if there is an error

        elif self.n_ofDrones < 3 and 'Sphere' in self.shape:
            ans = tk.messagebox.askyesno('Warning',
                                         'Sphere shape requires at least 3 drones to be visible effective. Do you want to proceed?')
            if not ans:
                return # Do not close the window if the user chooses No

        elif self.n_ofDrones < 3 and 'Circle' in self.shape:
            ans = tk.messagebox.askyesno('Warning',
                                         'Circle shape requires at least 3 drones to be visible effective. Do you want to proceed?')
            if not ans:
                return  # Do not close the window if the user chooses No

        for i in range(self.n_steps):
            keyString = f'step_{i}'
            self.list_dict[keyString] = {'shape' : self.shape[i].lower()}

        self.destroy()

    def get_shape(self):
        return self.shape

    def get_list_dict(self):
        return self.list_dict