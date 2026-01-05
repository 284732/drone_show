from dataclasses import dataclass
import numpy as np


@dataclass
# dataclass semplice, leggibile perfetta per modelli
# trasformando la classe in dataclasse genera automaticamente _init_,_eq_ e una _repr_ di cui io ne fornisco una custom
# è usata per modelli immutabili o quasi, dove vuoi solo contenere dsti senza logica di controllo
class Drone:
    """
    Modello logico di un drone.
    Non contiene alcuna logica di controllo o simulazione.
    """
    drone_id: int
    initial_position: np.ndarray    # posizione iniziale in 3D
    max_velocity: float
    max_acceleration: float

    # validazione, il vettore deve essere 3d:
    def __post_init__(self):
        self.initial_position = np.asarray(self.initial_position, dtype=float)  # trasforma il dato initial_position in np.ndarray in tipo float
        if self.initial_position.shape != (3,):
            raise ValueError("initial_position must be a 3D vector")    #verifichiamo che il vettore sia esattamente 3D

    # utile per debug/logging, leggibile:
    # ritorna una STRINGA compatta e leggibile
    def __repr__(self):
        return (
            f"Drone(id={self.drone_id}, "
            f"pos={self.initial_position}, "
            f"v_max={self.max_velocity}, "
            f"a_max={self.max_acceleration})"
        )
