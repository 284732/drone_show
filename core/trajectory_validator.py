import numpy as np


def validate_trajectory(traj, drone, dt=0.01, eps=1e-9):
    """
    Controlla velocità e accelerazione massima di un drone lungo la traiettoria.
    Usa una piccola tolleranza eps per evitare falsi positivi numerici.
    """
    # Campionamento locale sulla durata della traiettoria (tempo interno, gestito da Trajectory.position)
    t_samples = np.arange(0, traj.duration + dt, dt)
    positions = np.array([traj.position(t) for t in t_samples]) # valuta la posizione della traiettoria a ciascun tempo -> ottieni una matrice di dimensione (N,d) dove d è la dimensione spaziale (3D)

    # Velocità (derivata prima discretizzata)
    velocities = np.diff(positions, axis=0) / dt    # calcola pos[i+1] - pos[]i
    speed = np.linalg.norm(velocities, axis=1)  # calcola la norma Euclidea ad ogni passo
    max_speed = np.max(speed) if len(speed) > 0 else 0.0

    # Accelerazione (derivata seconda discretizzata)    # stesso concetto ma applicato alla velocità
    accelerations = np.diff(velocities, axis=0) / dt
    accel = np.linalg.norm(accelerations, axis=1)
    max_accel = np.max(accel) if len(accel) > 0 else 0.0

    # Validazione con tolleranza
    valid_speed = max_speed <= (drone.max_velocity + eps)
    valid_acceleration = max_accel <= (drone.max_acceleration + eps)

    return {
        "max_speed": float(max_speed),
        "max_acceleration": float(max_accel),
        "valid_speed": bool(valid_speed), #true se la velocità max calcolata lungo la traiettoria non supera il limite più il margine
        "valid_acceleration": bool(valid_acceleration),
    }


def validate_swarm_trajectories(trajectories, drones, min_distance=0.5, dt=0.01):
    """
    Controlla distanza minima tra tutti i droni lungo la traiettoria.
    Considera l'orizzonte temporale GLOBALE (start_time + duration) per ciascun drone.
    Ritorna lista di violazioni [(drone_id1, drone_id2, t), ...].
    """
    drone_ids = list(trajectories.keys())   # estrai ID dei droni dello sciame
    violations = []

    # Tempo globale di fine (considera ritardi)
    T_end = max(trajectories[did].start_time + trajectories[did].duration for did in drone_ids)
    t_samples = np.arange(0, T_end + dt, dt)    # crea campioni temporali da t=0 a t_end incluso

    for t in t_samples: # per ogni tempo, calcola le posizioni di tutti i droni
        positions = np.array([trajectories[did].position(t) for did in drone_ids])
        # Controlla tutte le coppie i<j
        for i in range(len(drone_ids)):
            for j in range(i + 1, len(drone_ids)):
                dist = np.linalg.norm(positions[i] - positions[j]) # calcolo la distanza euclidea tra le posizioni
                if dist < min_distance:
                    violations.append((drone_ids[i], drone_ids[j], float(t)))

    return violations


def check_constraints_and_collisions(trajectories, drones, min_distance=0.5, dt=0.01, eps=1e-9):
    """
    Punto unico di verità:
      - verifica vincoli dinamici per ogni drone (vel/acc),
      - verifica collisioni nello sciame (distanza minima).
    """
    per_drone = {}
    any_dyn_violation = False

    for drone in drones:
        res = validate_trajectory(trajectories[drone.drone_id], drone, dt=dt, eps=eps)
        per_drone[drone.drone_id] = res
        if (not res["valid_speed"]) or (not res["valid_acceleration"]):
            any_dyn_violation = True

    swarm_violations = validate_swarm_trajectories(trajectories, drones, min_distance=min_distance, dt=dt)

    return {
        "dynamic_ok": (not any_dyn_violation),
        "swarm_ok": (len(swarm_violations) == 0),
        "per_drone": per_drone,
        "swarm_violations": swarm_violations,
    }


'''def summarize_swarm_violations(violations):
    """
    Riassume gli eventi di collisione:
      - droni coinvolti (offenders),
      - primo istante di collisione (earliest_time),
      - mappa (did1, did2) -> lista di tempi,
      - numero totale di eventi.
    """
    offenders = set()
    earliest_time = None
    pairs = {}

    for did1, did2, t in violations:
        offenders.update([did1, did2])
        if (earliest_time is None) or (t < earliest_time):
            earliest_time = t
        key = (min(did1, did2), max(did1, did2))
        pairs.setdefault(key, []).append(t)

    return {
        "offenders": sorted(offenders),
        "earliest_time": earliest_time,
        "pairs": pairs,
        "num_events": len(violations),
    }'''
