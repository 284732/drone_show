from dataclasses import dataclass
import numpy as np


@dataclass
# dataclass semplice, leggibile perfetta per modelli
class Drone:
    """
    Modello logico di un drone.
    Non contiene alcuna logica di controllo o simulazione.
    """
    drone_id: int
    initial_position: np.ndarray
    max_velocity: float
    max_acceleration: float

    # validazione, il vettore deve essere 3d:
    def __post_init__(self):
        self.initial_position = np.asarray(self.initial_position, dtype=float)
        if self.initial_position.shape != (3,):
            raise ValueError("initial_position must be a 3D vector")

    # utile per debug/logging, leggibile:
    def __repr__(self):
        return (
            f"Drone(id={self.drone_id}, "
            f"pos={self.initial_position}, "
            f"v_max={self.max_velocity}, "
            f"a_max={self.max_acceleration})"
        )
