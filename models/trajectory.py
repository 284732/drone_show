import numpy as np


class Trajectory:
    """
    Traiettoria temporale 3D.
    La traiettoria è definita come funzione del tempo.
    Una traiettoria continua.
    Non è ancora dipendente dal controllore e dal simulatore.
    Non viene ancora definito se utilizzeremo: spline, waypoints o polinomi.

    Viene definita una traiettoria 3D continua nel tempo come funzione di posizione x(t),y(t),z(t).
    E' volutamente agnostica rispetto al controllore e simulatore: fornusce solo posizioni nel tempo senza imporre
    come venga generata.
    """

    # costruttore
    def __init__(self, duration, position_function, start_time=0.0):
        """
        :param duration: durata totale [s]
        :param position_function: callable f(t) -> np.ndarray shape (3,)

        La classe non impone come costruisci position_function: può essere una spline, un polinomio, un'interpolazione
        per waypoints o anche una funzione analitica.
        """
        self.duration = float(duration)     # durata totale della traiettoria in secondi
        self._position_function = position_function     # una callable che, dato un tempo t(float), ritorna un vettore 3d np.ndarray di shape (3,)
        self.start_time = start_time

        if self.duration <= 0:
            raise ValueError("Trajectory duration must be positive")

    def position(self, t):
        """
        Valuta la traiettoria al tempo globale t.
        Tiene conto di start_time.
        """

        # 1. Prima della partenza → fermo all'inizio
        if t < self.start_time:
            local_t = 0.0

        # 2. Dopo la fine → fermo alla fine
        elif t > self.start_time + self.duration:
            local_t = self.duration

        # 3. Durante la traiettoria
        else:
            local_t = t - self.start_time

        pos = np.asarray(self._position_function(local_t), dtype=float)

        if pos.shape != (3,):
            raise ValueError("Position function must return a 3D vector")

        return pos

    def sample(self, num_points):
        """
        Campiona la traiettoria in num_points istanti.

        Genera num_points tempi uniformemente spaziali in [0, duration] con np.linspace,
        e valuta la traiettoria.
        Restituisce:
        -times: array shape (num_points,)
        -positions: array shape (num_points,3)
        """
        times = np.linspace(0.0, self.duration, num_points)
        positions = np.array([self.position(t) for t in times])
        return times, positions

    # Rappresentazione leggibile in STRINGA
    def __repr__(self):
        return f"Trajectory(duration={self.duration}s)"


"""
La classe non decide come calcoli la posizione: gli passi tu la funzione e lei la usa.
Cosa fa davvero ogni metodo:

_init_(duration, position_function):
    .Salva la durata
    .Salva la tua funzione di posizione 
    .Controlla che la durata sia positiva (niente percorsi da 0 secondi o negativi)
    
position(t):
    .Ti da la posizione al tempo t
    .Se chiedi un tempo fuori dalla durata (tipo t=-3 o t=100), lo satura
    .Controlla che la tua funzione ritorni esattamente un vettore 3D (shape (3,)) se no errore
    
sample(num_points):
    .Campiona la traiettoria: sceglie num_points tempi equidisatanti tra 0 e duration e ti restituisce:
        -times: i tempi usati
        -positions: le posizioni corrispondenti
    .Utile per plottare, fare animazioni o verifiche
    
_repr_:
    .Stampa qualcosa di leggibile per log/debug
"""
