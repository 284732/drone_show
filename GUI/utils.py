# GUI/utils.py
import sys
import tkinter as tk
from tkinter import messagebox


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