import numpy as np


def validate_trajectory(traj, drone, dt=0.01):
    """
    Controlla velocità e accelerazione massima di un drone.

    :param traj: oggetto Trajectory
    :param drone: oggetto Drone
    :param dt: passo di campionamento [s]
    :return: dict con max_velocity e max_acceleration
    """
    t_samples = np.arange(0, traj.duration + dt, dt)
    positions = np.array([traj.position(t) for t in t_samples])

    # Calcolo velocità
    velocities = np.diff(positions, axis=0) / dt
    speed = np.linalg.norm(velocities, axis=1)
    max_speed = np.max(speed)

    # Calcolo accelerazione
    accelerations = np.diff(velocities, axis=0) / dt
    accel = np.linalg.norm(accelerations, axis=1)
    max_accel = np.max(accel)

    valid_speed = max_speed <= drone.max_velocity
    valid_accel = max_accel <= drone.max_acceleration

    return {
        "max_speed": max_speed,
        "max_acceleration": max_accel,
        "valid_speed": valid_speed,
        "valid_acceleration": valid_accel
    }


def validate_swarm_trajectories(trajectories, drones, min_distance=0.5, dt=0.01):
    """
    Controlla distanza minima tra tutti i droni lungo la traiettoria.

    :param trajectories: dict {drone_id: Trajectory}
    :param drones: lista di oggetti Drone
    :param min_distance: distanza minima consentita [m]
    :param dt: passo campionamento
    :return: lista di violazioni (tupla drone_id1, drone_id2, t)
    """
    drone_ids = list(trajectories.keys())
    violations = []

    t_samples = np.arange(0, list(trajectories.values())[0].duration + dt, dt)

    for t in t_samples:
        positions = np.array([trajectories[did].position(t) for did in drone_ids])
        for i in range(len(drone_ids)):
            for j in range(i + 1, len(drone_ids)):
                dist = np.linalg.norm(positions[i] - positions[j])
                if dist < min_distance:
                    violations.append((drone_ids[i], drone_ids[j], t))

    return violations
