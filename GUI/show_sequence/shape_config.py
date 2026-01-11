# GUI/ShowSequence_GUI/ConfigurationShape_GUI.py
from GUI.show_sequence.shape_dict import parameters_dict
from GUI.droneShow_obj.obj_GUI import *
from GUI.utils import close_all
import tkinter as tk
from tkinter import Toplevel, messagebox

""" 
    This file will contain the GUI for the shape configuration.
    For each shape there are some parameters that can be configured.
    The user can set these parameters, or use default ones.
"""

class ConfigurationShapeGUI(Toplevel):
    def __init__(self, parent, step_i, actual_shape, shape_dict):
        super().__init__(parent)  # Initialize the Tkinter root window

        self.actual_shape = actual_shape
        self.step_i = step_i
        self.shape_dict = shape_dict
        self.title(f'Shape {actual_shape} Configuration - Step {step_i + 1}')
        self.geometry('400x500')
        self.resizable(False, True)
        self.protocol("WM_DELETE_WINDOW", close_all)

        self.config_frame = tk.LabelFrame(self,
                                          text=f'Configuration of the shape: {actual_shape}',
                                          padx=5, pady=5)
        self.config_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        # Variabile per tenere traccia della riga corrente
        self.current_row = 0

        match(actual_shape):
            case 'Sphere':
                self.add_parameter_sphere()
            case 'Grid':
                self.add_parameter_grid()
            case 'Circle':
                self.add_parameter_circle()
            case 'Line':
                self.add_parameter_line()
            case 'Heart':
                self.add_parameter_heart()
            case 'Wave':
                self.add_parameter_wave()
            case 'Spiral':
                self.add_parameter_spiral()
            case 'Number':
                self.add_parameter_number()

        # Aggiungi sempre i parametri temporali alla fine
        self.add_timing_parameters()

    def add_timing_parameters(self):
        """Aggiunge i parametri temporali (transition_duration e hold_duration)"""
        # Separator
        separator = tk.Frame(self.config_frame, height=2, bd=1, relief=tk.SUNKEN)
        separator.grid(row=self.current_row, column=0, columnspan=2, sticky="ew", pady=10)
        self.current_row += 1

        # Timing label
        timing_label = tk.Label(self.config_frame, text="Timing Parameters", font=("Arial", 10, "bold"))
        timing_label.grid(row=self.current_row, column=0, columnspan=2, pady=5)
        self.current_row += 1

        # Transition duration
        self.entry_transition = EntryFloat(self.config_frame, 'Transition Duration (s):', self.current_row, 0)
        self.entry_transition.insert(0, '5.0')  # Default value
        self.current_row += 1

        # Hold duration
        self.entry_hold = EntryFloat(self.config_frame, 'Hold Duration (s):', self.current_row, 0)
        self.entry_hold.insert(0, '2.0')  # Default value
        self.current_row += 1

    def get_timing_values(self):
        """Recupera i valori dei parametri temporali"""
        try:
            transition = float(self.entry_transition.get())
            hold = float(self.entry_hold.get())
            return transition, hold
        except ValueError:
            tk.messagebox.showerror("Invalid Input", "Please enter valid values for timing parameters.")
            return None, None

    """ Now methods for adding the parameters entries depending on the shape type. """
    def add_parameter_sphere(self):
        self.entry_radius = EntryFloat(self.config_frame, 'Radius:', self.current_row, 0)
        self.current_row += 1
        self.entry_center_x = EntryInt(self.config_frame, 'Center X:', self.current_row, 0)
        self.current_row += 1
        self.entry_center_y = EntryInt(self.config_frame, 'Center Y:', self.current_row, 0)
        self.current_row += 1
        self.entry_center_z = EntryInt(self.config_frame, 'Center Z:', self.current_row, 0)
        self.current_row += 1

        self.confirm_button = CommandButton(self.config_frame,
                                            'Confirm',
                                            self.confirm_sphere,
                                            'dark green',
                                            'white',
                                            100, 0)  # Riga alta per stare in fondo

    def confirm_sphere(self):
        try:
            radius = float(self.entry_radius.get())
            center_x = int(self.entry_center_x.get())
            center_y = int(self.entry_center_y.get())
            center_z = int(self.entry_center_z.get())
        except ValueError:
            tk.messagebox.showerror("Invalid Input", "Please enter valid numeric values for all parameters.")
            return

        transition, hold = self.get_timing_values()
        if transition is None or hold is None:
            return

        parameters = [radius, [center_x, center_y, center_z]]
        couples = list(zip(parameters_dict['Sphere'], parameters))
        self.shape_dict[f'step_{self.step_i}'].update(dict(couples))
        self.shape_dict[f'step_{self.step_i}']['transition_duration'] = transition
        self.shape_dict[f'step_{self.step_i}']['hold_duration'] = hold
        self.destroy()

    def add_parameter_grid(self):
        self.entry_space = EntryFloat(self.config_frame, 'Spacing:', self.current_row, 0)
        self.current_row += 1
        self.entry_center_x = EntryInt(self.config_frame, 'Center X:', self.current_row, 0)
        self.current_row += 1
        self.entry_center_y = EntryInt(self.config_frame, 'Center Y:', self.current_row, 0)
        self.current_row += 1
        self.entry_center_z = EntryInt(self.config_frame, 'Center Z:', self.current_row, 0)
        self.current_row += 1
        self.combobox_plane = ComboBox(self.config_frame,
                                          'Select the normal plane:',
                                          ['XY', 'XZ', 'YZ'],
                                          self.current_row, 0)
        self.current_row += 1

        self.confirm_button = CommandButton(self.config_frame,
                                            'Confirm',
                                            self.confirm_grid,
                                            'dark green',
                                            'white',
                                            100, 0)

    def confirm_grid(self):
        try:
            spacing = float(self.entry_space.get())
            center_x = int(self.entry_center_x.get())
            center_y = int(self.entry_center_y.get())
            center_z = int(self.entry_center_z.get())
            plane = str(self.combobox_plane.get()).lower()
        except ValueError:
            tk.messagebox.showerror("Invalid Input", "Please enter valid numeric values for all parameters.")
            return

        transition, hold = self.get_timing_values()
        if transition is None or hold is None:
            return

        parameters = [spacing, [center_x, center_y, center_z], plane]
        couples = list(zip(parameters_dict['Grid'], parameters))
        self.shape_dict[f'step_{self.step_i}'].update(dict(couples))
        self.shape_dict[f'step_{self.step_i}']['transition_duration'] = transition
        self.shape_dict[f'step_{self.step_i}']['hold_duration'] = hold
        self.destroy()

    def add_parameter_circle(self):
        self.entry_radius = EntryFloat(self.config_frame, 'Radius:', self.current_row, 0)
        self.current_row += 1
        self.entry_center_x = EntryInt(self.config_frame, 'Center X:', self.current_row, 0)
        self.current_row += 1
        self.entry_center_y = EntryInt(self.config_frame, 'Center Y:', self.current_row, 0)
        self.current_row += 1
        self.entry_center_z = EntryInt(self.config_frame, 'Center Z:', self.current_row, 0)
        self.current_row += 1
        self.entry_normal_x = EntryInt(self.config_frame, 'Normal Vector X:', self.current_row, 0)
        self.current_row += 1
        self.entry_normal_y = EntryInt(self.config_frame, 'Normal Vector Y', self.current_row, 0)
        self.current_row += 1
        self.entry_normal_z = EntryInt(self.config_frame, 'Normal Vector Z', self.current_row, 0)
        self.current_row += 1

        self.confirm_button = CommandButton(self.config_frame,
                                            'Confirm',
                                            self.confirm_circle,
                                            'dark green',
                                            'white',
                                            100, 0)

    def confirm_circle(self):
        try:
            radius = float(self.entry_radius.get())
            center_x = int(self.entry_center_x.get())
            center_y = int(self.entry_center_y.get())
            center_z = int(self.entry_center_z.get())
            normal_x = int(self.entry_normal_x.get())
            normal_y = int(self.entry_normal_y.get())
            normal_z = int(self.entry_normal_z.get())
        except ValueError:
            tk.messagebox.showerror("Invalid Input", "Please enter valid numeric values for all parameters.")
            return

        transition, hold = self.get_timing_values()
        if transition is None or hold is None:
            return

        parameters = [radius, [center_x, center_y, center_z], [normal_x, normal_y, normal_z]]
        couples = list(zip(parameters_dict['Circle'], parameters))
        self.shape_dict[f'step_{self.step_i}'].update(dict(couples))
        self.shape_dict[f'step_{self.step_i}']['transition_duration'] = transition
        self.shape_dict[f'step_{self.step_i}']['hold_duration'] = hold
        self.destroy()

    def add_parameter_line(self):
        self.entry_length = EntryFloat(self.config_frame, 'Length:', self.current_row, 0)
        self.current_row += 1
        self.combobox_axis = ComboBox(self.config_frame,
                                          'Select the axis:',
                                          ['X', 'Y', 'Z'],
                                          self.current_row, 0)
        self.current_row += 1

        self.confirm_button = CommandButton(self.config_frame,
                                            'Confirm',
                                            self.confirm_line,
                                            'dark green',
                                            'white',
                                            100, 0)

    def confirm_line(self):
        try:
            length = float(self.entry_length.get())
            axis = str(self.combobox_axis.get()).lower()
        except ValueError:
            tk.messagebox.showerror("Invalid Input", "Please enter valid numeric values for all parameters.")
            return

        transition, hold = self.get_timing_values()
        if transition is None or hold is None:
            return

        parameters = [length, axis]
        couples = list(zip(parameters_dict['Line'], parameters))
        self.shape_dict[f'step_{self.step_i}'].update(dict(couples))
        self.shape_dict[f'step_{self.step_i}']['transition_duration'] = transition
        self.shape_dict[f'step_{self.step_i}']['hold_duration'] = hold
        self.destroy()

    def add_parameter_heart(self):
        self.entry_size = EntryFloat(self.config_frame, 'Size:', self.current_row, 0)
        self.current_row += 1
        self.entry_center_x = EntryInt(self.config_frame, 'Center X:', self.current_row, 0)
        self.current_row += 1
        self.entry_center_y = EntryInt(self.config_frame, 'Center Y:', self.current_row, 0)
        self.current_row += 1
        self.entry_center_z = EntryInt(self.config_frame, 'Center Z:', self.current_row, 0)
        self.current_row += 1
        self.combobox_plane = ComboBox(self.config_frame,
                                          'Select the plane:',
                                          ['XY', 'XZ', 'YZ'],
                                          self.current_row, 0)
        self.current_row += 1

        self.confirm_button = CommandButton(self.config_frame,
                                            'Confirm',
                                            self.confirm_heart,
                                            'dark green',
                                            'white',
                                            100, 0)

    def confirm_heart(self):
        try:
            size = float(self.entry_size.get())
            center_x = int(self.entry_center_x.get())
            center_y = int(self.entry_center_y.get())
            center_z = int(self.entry_center_z.get())
            plane = str(self.combobox_plane.get()).lower()
        except ValueError:
            tk.messagebox.showerror("Invalid Input", "Please enter valid numeric values for all parameters.")
            return

        transition, hold = self.get_timing_values()
        if transition is None or hold is None:
            return

        parameters = [size, [center_x, center_y, center_z], plane]
        couples = list(zip(parameters_dict['Heart'], parameters))
        self.shape_dict[f'step_{self.step_i}'].update(dict(couples))
        self.shape_dict[f'step_{self.step_i}']['transition_duration'] = transition
        self.shape_dict[f'step_{self.step_i}']['hold_duration'] = hold
        self.destroy()

    def add_parameter_wave(self):
        self.entry_wavelength = EntryFloat(self.config_frame, 'Wavelength:', self.current_row, 0)
        self.current_row += 1
        self.entry_amplitude = EntryFloat(self.config_frame, 'Amplitude:', self.current_row, 0)
        self.current_row += 1
        self.entry_length = EntryFloat(self.config_frame, 'Length:', self.current_row, 0)
        self.current_row += 1
        self.entry_center_x = EntryInt(self.config_frame, 'Center X:', self.current_row, 0)
        self.current_row += 1
        self.entry_center_y = EntryInt(self.config_frame, 'Center Y:', self.current_row, 0)
        self.current_row += 1
        self.entry_center_z = EntryInt(self.config_frame, 'Center Z:', self.current_row, 0)
        self.current_row += 1

        self.confirm_button = CommandButton(self.config_frame,
                                            'Confirm',
                                            self.confirm_wave,
                                            'dark green',
                                            'white',
                                            100, 0)

    def confirm_wave(self):
        try:
            wavelength = float(self.entry_wavelength.get())
            amplitude = float(self.entry_amplitude.get())
            length = float(self.entry_length.get())
            center_x = int(self.entry_center_x.get())
            center_y = int(self.entry_center_y.get())
            center_z = int(self.entry_center_z.get())
        except ValueError:
            tk.messagebox.showerror("Invalid Input", "Please enter valid numeric values for all parameters.")
            return

        transition, hold = self.get_timing_values()
        if transition is None or hold is None:
            return

        parameters = [wavelength, amplitude, length, [center_x, center_y, center_z]]
        couples = list(zip(parameters_dict['Wave'], parameters))
        self.shape_dict[f'step_{self.step_i}'].update(dict(couples))
        self.shape_dict[f'step_{self.step_i}']['transition_duration'] = transition
        self.shape_dict[f'step_{self.step_i}']['hold_duration'] = hold
        self.destroy()

    def add_parameter_spiral(self):
        self.entry_radius_start = EntryFloat(self.config_frame, 'Radius Start:', self.current_row, 0)
        self.current_row += 1
        self.entry_radius_end = EntryFloat(self.config_frame, 'Radius End:', self.current_row, 0)
        self.current_row += 1
        self.entry_height = EntryFloat(self.config_frame, 'Height:', self.current_row, 0)
        self.current_row += 1
        self.entry_turns = EntryFloat(self.config_frame, 'Turns:', self.current_row, 0)
        self.current_row += 1
        self.entry_center_x = EntryInt(self.config_frame, 'Center X:', self.current_row, 0)
        self.current_row += 1
        self.entry_center_y = EntryInt(self.config_frame, 'Center Y:', self.current_row, 0)
        self.current_row += 1
        self.entry_center_z = EntryInt(self.config_frame, 'Center Z:', self.current_row, 0)
        self.current_row += 1

        self.confirm_button = CommandButton(self.config_frame,
                                            'Confirm',
                                            self.confirm_spiral,
                                            'dark green',
                                            'white',
                                            100, 0)

    def confirm_spiral(self):
        try:
            radius_start = float(self.entry_radius_start.get())
            radius_end = float(self.entry_radius_end.get())
            height = float(self.entry_height.get())
            turns = float(self.entry_turns.get())
            center_x = int(self.entry_center_x.get())
            center_y = int(self.entry_center_y.get())
            center_z = int(self.entry_center_z.get())
        except ValueError:
            tk.messagebox.showerror("Invalid Input", "Please enter valid numeric values for all parameters.")
            return

        transition, hold = self.get_timing_values()
        if transition is None or hold is None:
            return

        parameters = [radius_start, radius_end, height, turns, [center_x, center_y, center_z]]
        couples = list(zip(parameters_dict['Spiral'], parameters))
        self.shape_dict[f'step_{self.step_i}'].update(dict(couples))
        self.shape_dict[f'step_{self.step_i}']['transition_duration'] = transition
        self.shape_dict[f'step_{self.step_i}']['hold_duration'] = hold
        self.destroy()

    def add_parameter_number(self):
        self.entry_digit = EntryInt(self.config_frame, 'Digit (0-9):', self.current_row, 0)
        self.current_row += 1
        self.entry_size = EntryFloat(self.config_frame, 'Size:', self.current_row, 0)
        self.current_row += 1
        self.entry_center_x = EntryInt(self.config_frame, 'Center X:', self.current_row, 0)
        self.current_row += 1
        self.entry_center_y = EntryInt(self.config_frame, 'Center Y:', self.current_row, 0)
        self.current_row += 1
        self.entry_center_z = EntryInt(self.config_frame, 'Center Z:', self.current_row, 0)
        self.current_row += 1
        self.combobox_plane = ComboBox(self.config_frame,
                                          'Select the plane:',
                                          ['XY', 'XZ', 'YZ'],
                                          self.current_row, 0)
        self.current_row += 1

        self.confirm_button = CommandButton(self.config_frame,
                                            'Confirm',
                                            self.confirm_number,
                                            'dark green',
                                            'white',
                                            100, 0)

    def confirm_number(self):
        try:
            digit = int(self.entry_digit.get())
            size = float(self.entry_size.get())
            center_x = int(self.entry_center_x.get())
            center_y = int(self.entry_center_y.get())
            center_z = int(self.entry_center_z.get())
            plane = str(self.combobox_plane.get()).lower()
            if digit < 0 or digit > 9:
                self.entry_digit.delete(0, tk.END)
                tk.messagebox.showerror("Invalid Input", "Please enter a digit between 0 and 9.")
                return
        except ValueError:
            tk.messagebox.showerror("Invalid Input", "Please enter valid numeric values for all parameters.")
            return

        transition, hold = self.get_timing_values()
        if transition is None or hold is None:
            return

        parameters = [digit, size, [center_x, center_y, center_z], plane]
        couples = list(zip(parameters_dict['Number'], parameters))
        self.shape_dict[f'step_{self.step_i}'].update(dict(couples))
        self.shape_dict[f'step_{self.step_i}']['transition_duration'] = transition
        self.shape_dict[f'step_{self.step_i}']['hold_duration'] = hold
        self.destroy()

    def get_shape_dict(self):
        return self.shape_dict