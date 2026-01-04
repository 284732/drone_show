import numpy as np


def minimum_jerk_1d(p0, pf, T):
    """
    Genera una funzione di traiettoria minimum jerk 1D.

    :param p0: posizione iniziale
    :param pf: posizione finale
    :param T: durata
    :return: funzione f(t)
    """
    if T <= 0:
        raise ValueError("Duration T must be positive")

    def trajectory(t):
        t = np.clip(t, 0.0, T)
        tau = t / T
        return p0 + (pf - p0) * (
            10 * tau**3 - 15 * tau**4 + 6 * tau**5
        )

    return trajectory


def minimum_jerk_3d(p0, pf, T):
    """
    Traiettoria minimum jerk 3D.

    :param p0: array-like (3,)
    :param pf: array-like (3,)
    :param T: durata
    :return: funzione f(t) -> np.ndarray (3,)
    """
    p0 = np.asarray(p0, dtype=float)
    pf = np.asarray(pf, dtype=float)

    fx = minimum_jerk_1d(p0[0], pf[0], T)
    fy = minimum_jerk_1d(p0[1], pf[1], T)
    fz = minimum_jerk_1d(p0[2], pf[2], T)

    def trajectory(t):
        return np.array([fx(t), fy(t), fz(t)])

    return trajectory


def numerical_derivative(f, dt=1e-3):
    """
    Derivata numerica centrale di una funzione f(t).
    """
    def df(t):
        return (f(t + dt) - f(t - dt)) / (2 * dt)

    return df
