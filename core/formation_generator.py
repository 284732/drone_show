import numpy as np
from models.formation import Formation
from utils.geometry import rotate, translate, rotation_matrix_z


def line_formation(num_points, length=1.0, axis='x'):
    """
    Genera una formazione su una linea retta centrata nell'origine.

    :param num_points: numero di punti, anche numero di droni ovviamente
    :param length: lunghezza totale della linea
    :param axis: 'x', 'y' o 'z'
    """
    if num_points < 2:
        raise ValueError("num_points must be >= 2")

    coords = np.linspace(-length / 2, length / 2, num_points)   # genera n valori equidistanti tra a e b

    points = np.zeros((num_points, 3))  # mi crea un array 3D dei punti -> una matrice tutta zero di dimensioni num_points righe x 3 colonne (x,y,z)
    if axis == 'x':
        points[:, 0] = coords
    elif axis == 'y':
        points[:, 1] = coords
    elif axis == 'z':
        points[:, 2] = coords
    else:
        raise ValueError("axis must be 'x', 'y' or 'z'")

    #funzionava return Formation(points)    # la classe Formation prende questi punti e li salva come formazione geometrica
    return Formation(target_positions=points)



'''def circle_formation(num_points, radius=1.0):
    """
    Genera una formazione circolare nel piano XY.

    :param num_points: numero di punti
    :param radius: raggio del cerchio
    """
    angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)  # crea n numeri equidistanti fra a e b
    # quindi da 0 a 2pi genera num_points angoli. endpoint=False significa non includere 2pi come ultimo valore, cosi primo punto (0) e l'ultimo (360) non si sovrappongono

    x = radius * np.cos(angles)
    y = radius * np.sin(angles)
    z = np.zeros(num_points)
    # il cerchio è nel piano XY

    points = np.vstack((x, y, z)).T
    return Formation(points)'''


def circle_formation_normal(num_points, radius=1.0, center=(0,0,0), normal=(0,0,1)):
    """
    Genera un cerchio su un piano definito dal vettore normale 'normal'.
    Il cerchio è centrato in `center`, raggio `radius`.
    Se normal=(0,0,1), è nel piano XY. Altrimenti viene ruotato di conseguenza.

    :param num_points: numero di punti (>=3)
    :param radius: raggio
    :param center: centro (x,y,z)
    :param normal: normale del piano (nx, ny, nz)

    La funzione genera N punti disposti a cerchio su un piano arbitrario dello spazio, tale piano
    è definito dal suo vettore normale (verso perprendicolare al piano).
    """
    if num_points < 3:
        raise ValueError("num_points must be >= 3")

    center = np.asarray(center, dtype=float)
    normal = np.asarray(normal, dtype=float)

    if center.shape != (3,):
        raise ValueError("center must be a 3D vector")
    if normal.shape != (3,):
        raise ValueError("normal must be a 3D vector")
    if np.linalg.norm(normal) < 1e-12:
        raise ValueError("normal must be non-zero")

    # 1) Genera cerchio nel piano XY -> base
    angles = np.linspace(0, 2*np.pi, num_points, endpoint=False)
    x = radius * np.cos(angles)
    y = radius * np.sin(angles)
    z = np.zeros(num_points)
    points_xy = np.vstack((x, y, z)).T  # shape (N, 3) -> è una matrice (N,3) con il cerchio centrato in [0,0,0] nel piano XY

    # 2) Calcola rotazione che porta il vettore [0,0,1] (asse Z) → normal
    z_axis = np.array([0.0, 0.0, 1.0])
    n = normal / np.linalg.norm(normal)

    # Se n ~ z_axis, non ruotare
    if np.allclose(n, z_axis):
        R = np.eye(3)
    elif np.allclose(n, -z_axis):
        # 180° attorno all'asse X (o qualunque asse perpendicolare)
        R = np.array([[1,0,0],[0,-1,0],[0,0,-1]], dtype=float)
    else:
        v = np.cross(z_axis, n)
        s = np.linalg.norm(v)
        c = np.dot(z_axis, n)
        # Matrice di rotazione con formula di Rodrigues
        vx = np.array([[0,    -v[2],  v[1]],
                       [v[2],  0,    -v[0]],
                       [-v[1], v[0],  0   ]], dtype=float)
        R = np.eye(3) + vx + (vx @ vx) * ((1 - c) / (s**2))

    # 3) Applica rotazione e traslazione
    points_rot = points_xy @ R.T
    points = points_rot + center

    return Formation(target_positions=points)


def transform_formation(formation, translation_vec=None, rotation_angle_z=None):
    """
    Applica trasformazioni rigide a una formazione.

    :param formation: oggetto Formation
    :param translation_vec: array-like (3,)
    :param rotation_angle_z: angolo in radianti

    La funzione prende una Formation esistente (un insieme di punti 3D)
    un vettore 3D per traslare i punti -> opzionale
    e un angolo in radianti per ruotare attorno all'asse z
    Obiettivo: restituire una nuova formazione con i punti ruotati/traslati
    """
    points = formation.target_positions.copy()  # prende i punti originali (N,3) e li copia, così non viene modificato l'oggetto formation passato

    if rotation_angle_z is not None:
        R = rotation_matrix_z(rotation_angle_z)     # matrice di rotazione attorno all'asse z
        points = rotate(points, R)

    if translation_vec is not None:
        points = translate(points, translation_vec)

    return Formation(target_positions=points, reference_time=formation.reference_time)
