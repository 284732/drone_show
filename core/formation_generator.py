import numpy as np
from models.formation import Formation
from utils.geometry import rotate, translate, rotation_matrix_z


def _ensure_exact_points(points, num_points):
    """
    Utility: assicura che l'array abbia esattamente num_points.
    - Se troppi: ne seleziona num_points casuali
    - Se troppo pochi: duplica punti casuali
    """
    points = np.array(points)
    current = len(points)

    if current == num_points:
        return points
    elif current > num_points:
        # Troppi punti: seleziona num_points casuali
        indices = np.random.choice(current, num_points, replace=False)
        return points[indices]
    else:
        # Troppo pochi: duplica punti casuali
        needed = num_points - current
        indices = np.random.choice(current, needed, replace=True)
        extra = points[indices]
        return np.vstack([points, extra])

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




###############
# FORMAZIONI 3D VOLUMETRICHE
###############

def sphere_formation(num_points, radius=1.0, center=(0, 0, 0)):
    """
    Genera una sfera 3D distribuendo i punti sulla superficie usando l'algoritmo di Fibonacci.
    Ottimo per transizioni spettacolari.

    :param num_points: numero di punti
    :param radius: raggio della sfera
    :param center: centro (x, y, z)
    """
    center = np.asarray(center, dtype=float)

    points = []
    phi = np.pi * (3.0 - np.sqrt(5.0))  # golden angle in radianti

    for i in range(num_points):
        y = 1 - (i / float(num_points - 1)) * 2  # y va da 1 a -1
        radius_at_y = np.sqrt(1 - y * y)

        theta = phi * i

        x = np.cos(theta) * radius_at_y
        z = np.sin(theta) * radius_at_y

        points.append([x * radius, y * radius, z * radius])

    points = np.array(points) + center
    points = _ensure_exact_points(points, num_points)
    return Formation(target_positions=points)


def helix_formation(num_points, radius=1.0, height=5.0, turns=2.0, center=(0, 0, 0)):
    """
    Genera un'elica 3D (spirale ascendente).
    Perfetta per transizioni dinamiche e spettacolari.

    :param num_points: numero di punti
    :param radius: raggio dell'elica
    :param height: altezza totale
    :param turns: numero di giri completi
    :param center: centro della base (x, y, z)
    """
    center = np.asarray(center, dtype=float)

    t = np.linspace(0, turns * 2 * np.pi, num_points)

    x = radius * np.cos(t)
    y = radius * np.sin(t)
    z = np.linspace(0, height, num_points)

    points = np.vstack((x, y, z)).T + center
    points = _ensure_exact_points(points, num_points)
    return Formation(target_positions=points)


def cube_formation(num_points, side_length=2.0, center=(0, 0, 0)):
    """
    Genera un cubo con punti distribuiti sulle facce.
    Ottimo per geometrie precise.

    :param num_points: numero di punti
    :param side_length: lunghezza del lato
    :param center: centro (x, y, z)
    """
    center = np.asarray(center, dtype=float)
    half = side_length / 2.0

    points = []
    points_per_face = num_points // 6
    remaining = num_points % 6

    # 6 facce del cubo
    faces = [
        # Faccia +X
        lambda n: np.column_stack([np.full(n, half),
                                   np.random.uniform(-half, half, n),
                                   np.random.uniform(-half, half, n)]),
        # Faccia -X
        lambda n: np.column_stack([np.full(n, -half),
                                   np.random.uniform(-half, half, n),
                                   np.random.uniform(-half, half, n)]),
        # Faccia +Y
        lambda n: np.column_stack([np.random.uniform(-half, half, n),
                                   np.full(n, half),
                                   np.random.uniform(-half, half, n)]),
        # Faccia -Y
        lambda n: np.column_stack([np.random.uniform(-half, half, n),
                                   np.full(n, -half),
                                   np.random.uniform(-half, half, n)]),
        # Faccia +Z (top)
        lambda n: np.column_stack([np.random.uniform(-half, half, n),
                                   np.random.uniform(-half, half, n),
                                   np.full(n, half)]),
        # Faccia -Z (bottom)
        lambda n: np.column_stack([np.random.uniform(-half, half, n),
                                   np.random.uniform(-half, half, n),
                                   np.full(n, -half)]),
    ]

    for i, face_func in enumerate(faces):
        n = points_per_face + (1 if i < remaining else 0)
        if n > 0:
            points.append(face_func(n))

    points = np.vstack(points) + center
    points = _ensure_exact_points(points, num_points)
    return Formation(target_positions=points)


###############
# FORMAZIONI 2D AVANZATE
###############

def grid_formation(num_points, spacing=1.0, center=(0, 0, 0), plane='xy'):
    """
    Genera una griglia 2D regolare su un piano specificato.
    Ottima come formazione di partenza o arrivo.

    :param num_points: numero di punti
    :param spacing: spaziatura tra i punti
    :param center: centro (x, y, z)
    :param plane: 'xy', 'xz', o 'yz'
    """
    center = np.asarray(center, dtype=float)

    # Calcola dimensioni griglia
    cols = int(np.ceil(np.sqrt(num_points)))
    rows = int(np.ceil(num_points / cols))

    points = []
    idx = 0

    for i in range(rows):
        for j in range(cols):
            if idx >= num_points:
                break

            x_offset = (j - cols / 2.0) * spacing
            y_offset = (i - rows / 2.0) * spacing

            if plane == 'xy':
                points.append([x_offset, y_offset, 0])
            elif plane == 'xz':
                points.append([x_offset, 0, y_offset])
            elif plane == 'yz':
                points.append([0, x_offset, y_offset])

            idx += 1

    points = np.array(points) + center
    return Formation(target_positions=points)


def heart_formation(num_points, size=1.0, center=(0, 0, 0), plane='xy'):
    """
    Genera una forma a cuore 2D.
    Perfetta per show romantici o creativi!

    :param num_points: numero di punti
    :param size: dimensione del cuore
    :param center: centro (x, y, z)
    :param plane: 'xy', 'xz', o 'yz'
    """
    center = np.asarray(center, dtype=float)

    # Equazione parametrica del cuore
    t = np.linspace(0, 2 * np.pi, num_points)

    x = size * 16 * np.sin(t) ** 3
    y = size * (13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t))

    # Normalizza
    x = x / 16.0
    y = y / 16.0

    if plane == 'xy':
        points = np.column_stack([x, y, np.zeros(num_points)])
    elif plane == 'xz':
        points = np.column_stack([x, np.zeros(num_points), y])
    elif plane == 'yz':
        points = np.column_stack([np.zeros(num_points), x, y])

    points = points + center
    return Formation(target_positions=points)


def star_formation(num_points, outer_radius=2.0, inner_radius=1.0,
                   num_spikes=5, center=(0, 0, 0), plane='xy'):
    """
    Genera una stella 2D con numero di punte configurabile.

    :param num_points: numero di punti
    :param outer_radius: raggio esterno (punte)
    :param inner_radius: raggio interno (insenature)
    :param num_spikes: numero di punte della stella
    :param center: centro (x, y, z)
    :param plane: 'xy', 'xz', o 'yz'
    """
    center = np.asarray(center, dtype=float)

    points = []
    points_per_spike = num_points // (num_spikes * 2)

    for i in range(num_spikes * 2):
        # Alterna tra raggio esterno e interno
        if i % 2 == 0:
            radius = outer_radius
        else:
            radius = inner_radius

        angle_start = i * np.pi / num_spikes
        angle_end = (i + 1) * np.pi / num_spikes

        n = points_per_spike if i < (num_spikes * 2 - 1) else (num_points - len(points))
        angles = np.linspace(angle_start, angle_end, n)

        x = radius * np.cos(angles)
        y = radius * np.sin(angles)

        if plane == 'xy':
            pts = np.column_stack([x, y, np.zeros(n)])
        elif plane == 'xz':
            pts = np.column_stack([x, np.zeros(n), y])
        elif plane == 'yz':
            pts = np.column_stack([np.zeros(n), x, y])

        points.append(pts)

    points = np.vstack(points) + center
    points = _ensure_exact_points(points, num_points)
    return Formation(target_positions=points)


###############
# FORMAZIONI DINAMICHE/CREATIVE
###############

def wave_formation(num_points, wavelength=2.0, amplitude=1.0,
                   length=10.0, center=(0, 0, 0)):
    """
    Genera un'onda sinusoidale 3D.
    Ottima per effetti fluidi.

    :param num_points: numero di punti
    :param wavelength: lunghezza d'onda
    :param amplitude: ampiezza dell'onda
    :param length: lunghezza totale
    :param center: centro (x, y, z)
    """
    center = np.asarray(center, dtype=float)

    x = np.linspace(-length / 2, length / 2, num_points)
    y = amplitude * np.sin(2 * np.pi * x / wavelength)
    z = np.zeros(num_points)

    points = np.column_stack([x, y, z]) + center
    return Formation(target_positions=points)


def pyramid_formation(num_points, base_size=3.0, height=3.0, center=(0, 0, 0)):
    """
    Genera una piramide con base quadrata.

    :param num_points: numero di punti
    :param base_size: dimensione della base
    :param height: altezza della piramide
    :param center: centro della base (x, y, z)
    """
    center = np.asarray(center, dtype=float)

    # Numero di livelli
    num_levels = int(np.sqrt(num_points))
    points = []

    for level in range(num_levels):
        z = (level / (num_levels - 1)) * height if num_levels > 1 else 0
        current_size = base_size * (1 - level / num_levels)

        # Punti per questo livello
        points_this_level = max(1, num_points // num_levels)

        if current_size > 0:
            # Crea un quadrato per questo livello
            half = current_size / 2
            side_points = int(np.sqrt(points_this_level))

            for i in range(side_points):
                for j in range(side_points):
                    x = -half + (i / max(1, side_points - 1)) * current_size if side_points > 1 else 0
                    y = -half + (j / max(1, side_points - 1)) * current_size if side_points > 1 else 0
                    points.append([x, y, z])

    # Prendi solo num_points punti
    points = np.array(points[:num_points]) + center
    points = _ensure_exact_points(points, num_points)
    return Formation(target_positions=points)


def spiral_formation(num_points, radius_start=0.5, radius_end=3.0,
                     height=5.0, turns=3.0, center=(0, 0, 0)):
    """
    Genera una spirale conica (radius cresce mentre sale).
    Molto spettacolare per transizioni.

    :param num_points: numero di punti
    :param radius_start: raggio iniziale (in basso)
    :param radius_end: raggio finale (in alto)
    :param height: altezza totale
    :param turns: numero di giri
    :param center: centro della base (x, y, z)
    """
    center = np.asarray(center, dtype=float)

    t = np.linspace(0, turns * 2 * np.pi, num_points)
    z = np.linspace(0, height, num_points)

    # Raggio cresce linearmente
    radius = np.linspace(radius_start, radius_end, num_points)

    x = radius * np.cos(t)
    y = radius * np.sin(t)

    points = np.column_stack([x, y, z]) + center
    return Formation(target_positions=points)


def number_formation(num_points, digit, size=3.0, center=(0, 0, 0), plane='xy'):
    """
    Genera la forma di un numero (1-9) in 2D.

    :param num_points: numero di punti
    :param digit: numero da 1 a 9
    :param size: dimensione del numero
    :param center: centro (x, y, z)
    :param plane: 'xy', 'xz', o 'yz'
    """
    center = np.asarray(center, dtype=float)

    if digit < 1 or digit > 9:
        raise ValueError("digit must be between 1 and 9")

    # Definizione dei segmenti per ogni numero (coordinate normalizzate 0-1)
    # Ogni numero è definito come lista di linee [x1, y1, x2, y2]
    number_segments = {
        1: [
            [0.5, 0.0, 0.5, 1.0],  # Linea verticale centrale
            [0.3, 0.8, 0.5, 1.0],  # Diagonale in alto a sinistra
        ],
        2: [
            [0.0, 1.0, 1.0, 1.0],  # Top
            [1.0, 1.0, 1.0, 0.5],  # Right top
            [1.0, 0.5, 0.0, 0.5],  # Middle
            [0.0, 0.5, 0.0, 0.0],  # Left bottom
            [0.0, 0.0, 1.0, 0.0],  # Bottom
        ],
        3: [
            [0.0, 1.0, 1.0, 1.0],  # Top
            [1.0, 1.0, 1.0, 0.5],  # Right top
            [0.3, 0.5, 1.0, 0.5],  # Middle
            [1.0, 0.5, 1.0, 0.0],  # Right bottom
            [1.0, 0.0, 0.0, 0.0],  # Bottom
        ],
        4: [
            [0.0, 1.0, 0.0, 0.5],  # Left top
            [0.0, 0.5, 1.0, 0.5],  # Middle
            [1.0, 1.0, 1.0, 0.0],  # Right full
        ],
        5: [
            [1.0, 1.0, 0.0, 1.0],  # Top
            [0.0, 1.0, 0.0, 0.5],  # Left top
            [0.0, 0.5, 1.0, 0.5],  # Middle
            [1.0, 0.5, 1.0, 0.0],  # Right bottom
            [1.0, 0.0, 0.0, 0.0],  # Bottom
        ],
        6: [
            [1.0, 1.0, 0.0, 1.0],  # Top
            [0.0, 1.0, 0.0, 0.0],  # Left full
            [0.0, 0.5, 1.0, 0.5],  # Middle
            [1.0, 0.5, 1.0, 0.0],  # Right bottom
            [1.0, 0.0, 0.0, 0.0],  # Bottom
        ],
        7: [
            [0.0, 1.0, 1.0, 1.0],  # Top
            [1.0, 1.0, 0.5, 0.0],  # Diagonal
        ],
        8: [
            [0.0, 1.0, 1.0, 1.0],  # Top
            [0.0, 1.0, 0.0, 0.5],  # Left top
            [1.0, 1.0, 1.0, 0.5],  # Right top
            [0.0, 0.5, 1.0, 0.5],  # Middle
            [0.0, 0.5, 0.0, 0.0],  # Left bottom
            [1.0, 0.5, 1.0, 0.0],  # Right bottom
            [0.0, 0.0, 1.0, 0.0],  # Bottom
        ],
        9: [
            [0.0, 1.0, 1.0, 1.0],  # Top
            [0.0, 1.0, 0.0, 0.5],  # Left top
            [1.0, 1.0, 1.0, 0.0],  # Right full
            [0.0, 0.5, 1.0, 0.5],  # Middle
            [0.0, 0.0, 1.0, 0.0],  # Bottom
        ],
    }

    segments = number_segments[digit]

    # Calcola la lunghezza totale di tutti i segmenti
    segment_lengths = []
    for seg in segments:
        x1, y1, x2, y2 = seg
        length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        segment_lengths.append(length)

    total_length = sum(segment_lengths)

    # Distribuisci i punti proporzionalmente alla lunghezza di ogni segmento
    points = []

    for seg, seg_length in zip(segments, segment_lengths):
        x1, y1, x2, y2 = seg

        # Numero di punti per questo segmento
        n_seg = max(1, int(num_points * seg_length / total_length))

        # Genera punti lungo il segmento
        t = np.linspace(0, 1, n_seg)
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)

        for xi, yi in zip(x, y):
            # Scala e centra
            x_scaled = (xi - 0.5) * size
            y_scaled = (yi - 0.5) * size

            if plane == 'xy':
                points.append([x_scaled, y_scaled, 0])
            elif plane == 'xz':
                points.append([x_scaled, 0, y_scaled])
            elif plane == 'yz':
                points.append([0, x_scaled, y_scaled])

    points = np.array(points) + center
    points = _ensure_exact_points(points, num_points)

    return Formation(target_positions=points)