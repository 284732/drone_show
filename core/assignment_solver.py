import numpy as np
from scipy.optimize import linear_sum_assignment


def compute_cost_matrix(drone_positions, target_positions):
    """
    Calcola la matrice dei costi basata sulla distanza euclidea.

    :param drone_positions: array-like (N, 3)
    :param target_positions: array-like (N, 3)
    :return: cost_matrix (N, N)
    """
    drone_positions = np.asarray(drone_positions, dtype=float)
    target_positions = np.asarray(target_positions, dtype=float)

    if drone_positions.shape[0] != target_positions.shape[0]:
        raise ValueError("Number of drones and targets must be equal")

    N = drone_positions.shape[0]
    cost_matrix = np.zeros((N, N))

    for i in range(N):
        for j in range(N):
            cost_matrix[i, j] = np.linalg.norm(
                drone_positions[i] - target_positions[j]
            )

    return cost_matrix


def assign_drones_to_targets(drones, formation):
    """
    Assegna ogni drone a una posizione target della formazione.

    :param drones: lista di oggetti Drone
    :param formation: oggetto Formation
    :return: dict {drone_id: target_position}
    """
    drone_positions = np.array([d.initial_position for d in drones])
    target_positions = formation.target_positions

    cost_matrix = compute_cost_matrix(drone_positions, target_positions)

    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    assignment = {}
    for i, j in zip(row_ind, col_ind):
        assignment[drones[i].drone_id] = target_positions[j]

    return assignment
