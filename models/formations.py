import numpy as np


class Formation:
    """
    Rappresenta una formazione geometrica astratta.
    Non conosce i droni, solo le posizioni target.
    Formations diverso da uno show -> può essere riutilizzata, trasformata e combinata
    """

    def __init__(self, target_positions, reference_time=0.0):
        """
        :param target_positions: array-like, shape (N, 3)
        :param reference_time: tempo di riferimento della formazione
        """
        self.target_positions = np.asarray(target_positions, dtype=float)
        self.reference_time = float(reference_time)

        if self.target_positions.ndim != 2 or self.target_positions.shape[1] != 3:
            raise ValueError("target_positions must be of shape (N, 3)")

    @property
    def size(self):
        """Numero di punti della formazione."""
        return self.target_positions.shape[0]

    def get_position(self, index):
        """Restituisce la posizione target i-esima."""
        return self.target_positions[index]

    def __repr__(self):
        return f"Formation(num_points={self.size}, t_ref={self.reference_time})"
