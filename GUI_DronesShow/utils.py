import sys
import tkinter as tk
from tkinter import messagebox
import yaml

def close_all():
    """
    Closes all Tkinter windows and exits the program.
    Can be used for the X button on any window.
    """
    root = tk._default_root  # get the main Tk root
    if root:
        try:
            root.destroy()  # closes all windows
        except Exception:
            pass
    sys.exit()


def toYAML(dictionary):
    """ This method converts a dictionary to a YAML file. """
    try:
        with open('drone_show_config.yaml', 'w') as file:
            yaml.dump(dictionary, file)
    except Exception as e:
        tk.messagebox.showerror("Error", str(e))