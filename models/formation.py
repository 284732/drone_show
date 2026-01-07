import numpy as np


class Formation:
    """
    Rappresenta una formazione geometrica astratta.
    Non conosce i droni, solo le posizioni target.
    Formations diverso da uno show -> può essere riutilizzata, trasformata e combinata

    Formazione = set di posizioni target in 3D (shape (N,3)), dove ogni riga è un punto (x,y,z).
    Essa non dipende dai droni: è deliberatamente agnostica rispetto a quanti/come i droni verranno assegnati.
    Riutilizzabile e trasformabile: la stessa formazione può essere traslata, ruotata, scalata combinata in diverse parti dello show.
    """

    # costruttore
    def __init__(self, target_positions, reference_time=0.0):
        """
        :param target_positions: array-like, shape (N, 3)
        :param reference_time: tempo di riferimento della formazione
        """
        self.target_positions = np.asarray(target_positions, dtype=float)   # converte target_positions in np.ndarray float
        self.reference_time = float(reference_time)

        # verifichiamo che target_position sia esattamente una matrice 2D con 3 colonne:
        if self.target_positions.ndim != 2 or self.target_positions.shape[1] != 3:
            raise ValueError("target_positions must be of shape (N, 3)")

    @property
    def size(self):
        """Numero di punti della formazione."""
        return self.target_positions.shape[0]   # ritorna il numero di punti (cioè (N)) -> ovvero quante pos target contiene la formazione


    def get_position(self, index):
        """Restituisce la posizione target i-esima."""
        return self.target_positions[index]     # ritorna la i-esima posizione target, una riga di 3 valori,

    # ritorna una STRINGA compatta e leggibile per log/debug
    def __repr__(self):
        return f"Formation(num_points={self.size}, t_ref={self.reference_time})"
