import numpy as np


def translate(points, translation):
    """
    Trasla punti 3D.

    :param points: array-like (..., 3)
    :param translation: array-like (3,)
    :return: punti traslati
    """
    points = np.asarray(points, dtype=float)
    translation = np.asarray(translation, dtype=float)

    return points + translation


def scale(points, factor):
    """
    Scala punti 3D rispetto all'origine.

    :param points: array-like (..., 3)
    :param factor: float
    """
    points = np.asarray(points, dtype=float)
    return points * factor


def rotation_matrix_z(angle_rad):
    """
    Matrice di rotazione attorno all'asse Z.
    """
    c = np.cos(angle_rad)
    s = np.sin(angle_rad)

    return np.array([
        [c, -s, 0.0],
        [s,  c, 0.0],
        [0.0, 0.0, 1.0]
    ])


def rotate(points, rotation_matrix):
    """
    Applica una rotazione a punti 3D.

    :param points: array-like (..., 3)
    :param rotation_matrix: array-like (3, 3)
    """
    points = np.asarray(points, dtype=float)
    R = np.asarray(rotation_matrix, dtype=float)

    return points @ R.T
