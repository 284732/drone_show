import tkinter as tk
from tkinter import ttk, messagebox

""" 
    In this file will be defined the classes objects to be reported
    in the Drone Configuration GUI.
    gui_objects.py
"""

class SpinBox(tk.Spinbox):
    def __init__(self, root, textLabel, from_, to, row, col):
        super().__init__(root, from_=from_, to=to, width=8)

        # LABELING THE SPINBOX
        self.spinbox_label = tk.Label(root, text=textLabel)
        self.spinbox_label.grid(row=row, column=col, padx=5, pady=15, sticky=tk.W)

        # PLACING THE SPINBOX
        self.grid(row=row, column=col+1, padx=5, pady=15, sticky=tk.W)


class CommandButton(tk.Button):
    def __init__(self, root, text, cmd, color, textColor, row, col):
        super().__init__(root, text=text, command=cmd, bg=color, fg=textColor, width=10, height=1)
        self.row = row
        self.col = col

        self.grid(row=self.row, column=self.col, padx=10, pady=10, sticky=tk.W)


class ComboBox(tk.ttk.Combobox):
    def __init__(self, root, textLabel, valuesList, row, col):
        super().__init__(root, values=valuesList, state='readonly', width=12)

        # LABELING THE COMBOBOX
        self.combobox_label = tk.Label(root, text=textLabel)
        self.combobox_label.grid(row=row, column=col, padx=5, pady=15, sticky=tk.W)

        # PLACING THE COMBOBOX
        self.grid(row=row, column=col+1, padx=5, pady=15, sticky=tk.W)


class EntryFloat(tk.Entry):
    def __init__(self, root, textLabel, row, col):
        # Register the validation function WITHOUT parentheses
        vcmd = root.register(self.validate_float)

        super().__init__(root, width=10, validate='key',
                         validatecommand=(vcmd, '%P'))

        # LABEL
        self.entry_label = tk.Label(root, text=textLabel)
        self.entry_label.grid(row=row, column=col, padx=5, pady=15, sticky=tk.W)

        # PLACING ENTRY
        self.grid(row=row, column=col+1, padx=5, pady=15, sticky=tk.W)

    def validate_float(self, value):
        """Function to validate: receives the new value as string."""
        if value == "" or value == "-":  # Put temporary allow empty or minus sign
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False

    def get_float(self):
        """Retake the value as float, with error message if not valid."""
        try:
            return float(self.get())
        except ValueError:
            messagebox.showerror("Invalid Input",
                                 f"Please enter a valid float value for '{self.entry_label.cget('text')}'")
            return None


class EntryInt(tk.Entry):
    def __init__(self, root, textLabel, row, col):
        # Register the validation function (no parentheses)
        vcmd = root.register(self.validate_int)

        super().__init__(root, width=10, validate='key',
                         validatecommand=(vcmd, '%P'))

        # Label
        self.entry_label = tk.Label(root, text=textLabel)
        self.entry_label.grid(row=row, column=col, padx=5, pady=15, sticky=tk.W)

        # Place the entry
        self.grid(row=row, column=col+1, padx=5, pady=15, sticky=tk.W)

    def validate_int(self, value):
        # Allow empty string or single '-' during editing
        if value == "" or value == "-":
            return True
        # Require a valid integer otherwise
        try:
            int(value)
            return True
        except ValueError:
            return False

    def get_int(self):
        # Return the value as int; show error and return None if invalid
        try:
            return int(self.get())
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                f"Please enter a valid integer value for '{self.entry_label.cget('text')}'"
            )
            return None


class TextBox(tk.Text):
    def __init__(self, root, textLabel, row, col, height=5, width=30):
        super().__init__(root, height=height, width=width)

        # LABEL
        self.textbox_label = tk.Label(root, text=textLabel)
        self.textbox_label.grid(row=row, column=col, padx=5, pady=15, sticky=tk.W)

        # PLACING TEXTBOX
        self.grid(row=row, column=col+1, padx=5, pady=15, sticky=tk.W)

    def get_text(self):
        """Retrieve the text content from the Text widget."""
        return self.get("1.0", tk.END).strip()  # Get all text and strip trailing newline
