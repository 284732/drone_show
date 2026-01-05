from models.trajectory import Trajectory
from utils.math_tools import minimum_jerk_3d


def generate_trajectories(drones, assignment, duration):
    """
    Genera una traiettoria per ciascun drone assegnato.

    :param drones: lista di oggetti Drone
    :param assignment: dict {drone_id: target_position}
    :param duration: durata totale della traiettoria [s]
    :return: dict {drone_id: Trajectory}
    """
    trajectories = {}

    for drone in drones:
        drone_id = drone.drone_id
        p0 = drone.initial_position
        pf = assignment[drone_id]

        traj_func = minimum_jerk_3d(p0, pf, duration)   # costruisce la funzione f(t) tale che f(0) = p0 e f(duration) = pf e andamento "smooth"
        trajectories[drone_id] = Trajectory(duration, traj_func)    # creo l'istanza (l'oggetto) Trajectory

    return trajectories     # ritorno il dizionario creato
