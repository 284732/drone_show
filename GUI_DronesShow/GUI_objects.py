import tkinter as tk
from tkinter import messagebox

""" 
    In thhis file will be defined the classes objects to be reported
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



class EntryFloat(tk.Entry):
    def __init__(self, root, textLabel, row, col):
        # Registra la funzione di validazione SENZA parentesi
        vcmd = root.register(self.validate_float)

        super().__init__(root, width=10, validate='key',
                         validatecommand=(vcmd, '%P'))

        # LABEL
        self.entry_label = tk.Label(root, text=textLabel)
        self.entry_label.grid(row=row, column=col, padx=5, pady=15, sticky=tk.W)

        # PLACING ENTRY
        self.grid(row=row, column=col+1, padx=5, pady=15, sticky=tk.W)

    def validate_float(self, value):
        """Funzione di validazione: riceve il nuovo valore come stringa."""
        if value == "" or value == "-":  # consenti vuoto o segno meno temporaneo
            return True
        try:
            float(value)
            return True
        except ValueError:
            # Non mostrare subito errori (Tkinter chiama questa funzione ad ogni tasto)
            return False

    def get_float(self):
        """Recupera il valore come float, con messaggio di errore se non valido."""
        try:
            return float(self.get())
        except ValueError:
            messagebox.showerror("Invalid Input",
                                 f"Please enter a valid float value for '{self.entry_label.cget('text')}'")
            return None
