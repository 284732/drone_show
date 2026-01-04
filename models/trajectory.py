import numpy as np


class Trajectory:
    """
    Traiettoria temporale 3D.
    La traiettoria è definita come funzione del tempo.
    Una traiettoria continua.
    Non è ancora dipendente dal controllore e dal simulatore.
    Non viene ancora definito se utilizzeremo: spline, waypoints o polinomi.
    """

    def __init__(self, duration, position_function):
        """
        :param duration: durata totale [s]
        :param position_function: callable f(t) -> np.ndarray shape (3,)
        """
        self.duration = float(duration)
        self._position_function = position_function

        if self.duration <= 0:
            raise ValueError("Trajectory duration must be positive")

    def position(self, t):
        """
        Valuta la traiettoria al tempo t.
        Se t è fuori intervallo, viene saturato.
        """
        t_clamped = np.clip(t, 0.0, self.duration)
        pos = np.asarray(self._position_function(t_clamped), dtype=float)

        if pos.shape != (3,):
            raise ValueError("Position function must return a 3D vector")

        return pos

    def sample(self, num_points):
        """
        Campiona la traiettoria in num_points istanti.
        """
        times = np.linspace(0.0, self.duration, num_points)
        positions = np.array([self.position(t) for t in times])
        return times, positions

    def __repr__(self):
        return f"Trajectory(duration={self.duration}s)"
