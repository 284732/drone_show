import numpy as np
from models.formation import Formation
from utils.geometry import rotate, translate, rotation_matrix_z


def line_formation(num_points, length=1.0, axis='x'):
    """
    Genera una formazione su una linea retta centrata nell'origine.

    :param num_points: numero di punti
    :param length: lunghezza totale della linea
    :param axis: 'x', 'y' o 'z'
    """
    if num_points < 2:
        raise ValueError("num_points must be >= 2")

    coords = np.linspace(-length / 2, length / 2, num_points)

    points = np.zeros((num_points, 3))
    if axis == 'x':
        points[:, 0] = coords
    elif axis == 'y':
        points[:, 1] = coords
    elif axis == 'z':
        points[:, 2] = coords
    else:
        raise ValueError("axis must be 'x', 'y' or 'z'")

    return Formation(points)


def circle_formation(num_points, radius=1.0):
    """
    Genera una formazione circolare nel piano XY.

    :param num_points: numero di punti
    :param radius: raggio del cerchio
    """
    angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)

    x = radius * np.cos(angles)
    y = radius * np.sin(angles)
    z = np.zeros(num_points)

    points = np.vstack((x, y, z)).T
    return Formation(points)


def grid_formation(rows, cols, spacing=1.0):
    """
    Genera una griglia 2D nel piano XY.

    :param rows: numero di righe
    :param cols: numero di colonne
    :param spacing: distanza tra punti
    """
    xs = np.linspace(-(cols - 1) / 2, (cols - 1) / 2, cols) * spacing
    ys = np.linspace(-(rows - 1) / 2, (rows - 1) / 2, rows) * spacing

    points = []
    for y in ys:
        for x in xs:
            points.append([x, y, 0.0])

    return Formation(np.array(points))


def transform_formation(formation, translation_vec=None, rotation_angle_z=None):
    """
    Applica trasformazioni rigide a una formazione.

    :param formation: oggetto Formation
    :param translation_vec: array-like (3,)
    :param rotation_angle_z: angolo in radianti
    """
    points = formation.target_positions.copy()

    if rotation_angle_z is not None:
        R = rotation_matrix_z(rotation_angle_z)
        points = rotate(points, R)

    if translation_vec is not None:
        points = translate(points, translation_vec)

    return Formation(points, reference_time=formation.reference_time)
