import numpy as np

from core.trajectory_generator import generate_trajectories
from core.trajectory_validator import (
    validate_trajectory,
    validate_swarm_trajectories,
    check_constraints_and_collisions,
    #summarize_swarm_violations,
)


def time_scale_trajectories(drones, assignment, duration, max_iterations=3, dt_check=0.01, eps=1e-6):
    """
    Rigenera le traiettorie aumentando la durata se violano velocità o accelerazione massima.
    Miglioria: scala la durata con il fattore PEGGIORE (massimo tra tutti i droni) ad ogni iterazione,
    per convergere più velocemente e ridurre violazioni residue.
    Usa eps come tolleranza numerica.
    """
    current_duration = float(duration)

    for _ in range(max_iterations):
        trajectories = generate_trajectories(drones, assignment, current_duration)

        # calcolo del fattore di scala globale necessario
        global_scale = 1.0
        for drone in drones:
            res = validate_trajectory(trajectories[drone.drone_id], drone, dt=dt_check, eps=eps)
            if res["max_speed"] > (drone.max_velocity + eps):   # se la velocità massima misurata supera il limite, calcola il fattore per azzerare la violazione
                scale_v = res["max_speed"] / drone.max_velocity
                global_scale = max(global_scale, scale_v)
            if res["max_acceleration"] > (drone.max_acceleration + eps):
                scale_a = (res["max_acceleration"] / drone.max_acceleration) ** 0.5
                global_scale = max(global_scale, scale_a)

        if global_scale > (1.0 + eps):
            current_duration *= global_scale + eps
        else:
            # tutti i droni rispettano i vincoli con la durata corrente
            return trajectories, current_duration

    # se esce per max_iterations, restituisci l'ultima versione
    return trajectories, current_duration


import numpy as np
from core.trajectory_validator import validate_swarm_trajectories


def resolve_collisions_with_start_delays_me(
    trajectories, drones, *, min_distance=0.5, dt=0.05,
    delay_step=5, max_iters=5, max_total_delay=8.0
):
    # Non azzerare: mantieni eventuali start_time esistenti
    start_delays = {did: getattr(traj, "start_time", 0.0)
                    for did, traj in trajectories.items()}

    for it in range(max_iters):
        violations = validate_swarm_trajectories(
            trajectories, drones, min_distance=min_distance, dt=dt
        )
        if not violations:
            return trajectories, {"status": "OK", "iterations": it, "start_delays": start_delays}

        # collisione più precoce
        did1, did2, t_collision = min(violations, key=lambda v: v[2])

        # ritarda quello con meno delay accumulato
        new_delay = start_delays[did2] + delay_step

        # cap ai ritardi totali
        if new_delay > max_total_delay:
            return trajectories, {"status": "UNRESOLVED_COLLISION_MAX_DELAY",
                                  "iterations": it+1, "start_delays": start_delays}

        start_delays[did2] = new_delay
        trajectories[did2].start_time = new_delay

    return trajectories, {"status": "UNRESOLVED_COLLISION",
                          "iterations": max_iters, "start_delays": start_delays}



################################################
###OLD
def resolve_collisions_with_start_delays(
    trajectories,
    drones,
    *,
    min_distance=0.5,
    dt=0.01,
    delay_step=4,
    max_iters=10,
):
    """
    Risolve collisioni introducendo ritardi di partenza sui droni coinvolti.

    Strategia:
      - se esiste almeno una collisione allo stesso tempo t,
        ritarda uno dei droni coinvolti
      - ripete fino a risoluzione o max_iters

    Modifica SOLO traj.start_time.
    """
    # inizializza tutti i ritardi a zero
    start_delays = {did: 0.0 for did in trajectories.keys()}
    for traj in trajectories.values():
        traj.start_time = 0.0

    for it in range(max_iters):
        violations = validate_swarm_trajectories(
            trajectories, drones, min_distance=min_distance, dt=dt
        )

        # nessuna collisione → OK
        if not violations:
            return trajectories, {
                "status": "OK",
                "iterations": it,
                "start_delays": start_delays,
            }

        # prendi la prima collisione trovata
        did1, did2, t_collision = violations[0]

        # strategia semplice: ritarda il secondo drone
        start_delays[did2] += delay_step
        trajectories[did2].start_time = start_delays[did2]

    # se esce dal loop → non risolto
    return trajectories, {
        "status": "UNRESOLVED_COLLISION",
        "iterations": max_iters,
        "start_delays": start_delays,
    }

# Applica ritardi per salita in cascata
def apply_start_delays(trajectories, delay_step=0.5):
    """
    Applica un ritardo progressivo ai droni (ordinati per drone_id).
    Nota: i ritardi NON modificano velocità/accelerazione interne alla traiettoria.
    """
    for i, drone_id in enumerate(sorted(trajectories.keys())):
        trajectories[drone_id].start_time = i * delay_step
    return trajectories


def apply_altitude_layers(assignment, layer_height=0.3):
    """
    Applica separazione verticale ai target per ridurre collisioni.

    In pratica prende l'assegnazione "assignment" (mappa drone_id -> target_position) e sposta in alto
    il target del drone in base al suo indice, creando "layer" di quota (Z) distanziati di "layer_heigh".
    Cambia il target finale !!!! da non usare
    """
    new_assignment = {}
    for i, drone_id in enumerate(sorted(assignment.keys())):
        target = np.array(assignment[drone_id], dtype=float)
        target[2] += i * layer_height
        new_assignment[drone_id] = target
    return new_assignment


def _apply_target_z_offsets_for_offenders(assignment, offenders, layer_height):
    """
    Aggiunge offset verticale SOLO ai droni offensori (lista di drone_id).
    Alterna +h / -h per ridurre sovrapposizioni.
    Cambia il target finale !!!! da non usare
    """
    new_assignment = dict(assignment)
    sign = +1.0
    for did in sorted(offenders):
        target = np.array(new_assignment[did], dtype=float)
        target[2] += sign * layer_height
        new_assignment[did] = target
        sign *= -1.0  # alterna
    return new_assignment


'''def auto_process_trajectories(
    drones,
    assignment,
    base_duration,
    *,
    min_distance=0.5,
    dt=0.01,
    max_time_scale_iters=10,
    max_delay_iters=5,
    delay_step=0.2,
    layer_height=0.2,
    try_strategies=("delay", "layer"),
    eps=1e-6,
):
    """
    Pipeline automatica:
      1) Time-scaling per rispettare v_max/a_max.
      2) Se dinamica OK -> controllo collisioni.
      3) Se collisioni -> prova 'delay' (ritardi mirati sui droni offensori) e/o 'layer'
         (separazione verticale mirata), nell'ordine indicato.
      4) Se non risolvibile -> UNRESOLVED_DYNAMIC o UNRESOLVED_COLLISION.

    Ritorna:
      trajectories, final_duration, status, report
    """
    report = {"steps": []}

    # --- Step 1: time-scaling (vincoli dinamici) ---
    trajectories, duration = time_scale_trajectories(
        drones, assignment, base_duration,
        max_iterations=max_time_scale_iters, dt_check=dt, eps=eps
    )

    # partenza simultanea per default; i ritardi si applicheranno SOLO se necessari
    for traj in trajectories.values():
        traj.start_time = 0.0

    check = check_constraints_and_collisions(trajectories, drones, min_distance=min_distance, dt=dt, eps=eps)
    report["steps"].append({"phase": "post-timescaling", "check": check})

    # Extra pass (opzionale): se dinamica al pelo, ritenta un giro
    if not check["dynamic_ok"]:
        trajectories, duration = time_scale_trajectories(
            drones, assignment, duration,
            max_iterations=max_time_scale_iters, dt_check=dt, eps=eps
        )
        for traj in trajectories.values():
            traj.start_time = 0.0
        check = check_constraints_and_collisions(trajectories, drones, min_distance=min_distance, dt=dt, eps=eps)
        report["steps"].append({"phase": "post-timescaling-second-pass", "check": check})

    # Se dinamica NON ok -> non si risolve con ritardi/layer (sono strategie anti-collisione)
    if not check["dynamic_ok"]:
        status = "UNRESOLVED_DYNAMIC"
        report["warning"] = "Limiti di velocità/accelerazione non risolti con il time-scaling."
        report["final_check"] = check
        return trajectories, duration, status, report

    # Se non ci sono collisioni -> OK
    if check["swarm_ok"]:
        status = "OK"
        return trajectories, duration, status, report

    # --- Step 2: risolvi collisioni secondo le strategie in ordine ---
    unresolved = True
    current_assignment = dict(assignment)
    start_delays = {did: 0.0 for did in trajectories.keys()}

    for strategy in try_strategies:
        if strategy == "delay":
            # ritardi mirati SOLO per i droni offensori
            summary = summarize_swarm_violations(check["swarm_violations"])
            offenders = summary["offenders"]

            for it in range(max_delay_iters):
                # incrementa ritardi solo per offenders
                for did in offenders:
                    start_delays[did] += delay_step

                # rigenera traiettorie con stessi target/durata e applica ritardi
                trajectories = generate_trajectories(drones, current_assignment, duration)
                for did, delay in start_delays.items():
                    trajectories[did].start_time = delay

                # ricontrolla
                check = check_constraints_and_collisions(trajectories, drones, min_distance=min_distance, dt=dt, eps=eps)
                report["steps"].append({
                    "phase": f"delay_iter_{it+1}",
                    "offenders": offenders,
                    "start_delays": dict(start_delays),
                    "check": check
                })

                if check["swarm_ok"] and check["dynamic_ok"]:
                    unresolved = False
                    status = "RESOLVED_WITH_DELAY"
                    return trajectories, duration, status, report

        elif strategy == "layer":
            # separazione verticale mirata sui target degli offenders
            summary = summarize_swarm_violations(check["swarm_violations"])
            offenders = summary["offenders"]

            current_assignment = _apply_target_z_offsets_for_offenders(
                current_assignment, offenders, layer_height=layer_height
            )

            trajectories = generate_trajectories(drones, current_assignment, duration)
            # mantieni eventuali ritardi già introdotti nella fase precedente
            for did, delay in start_delays.items():
                trajectories[did].start_time = delay

            # ricontrolla
            check = check_constraints_and_collisions(trajectories, drones, min_distance=min_distance, dt=dt, eps=eps)
            report["steps"].append({
                "phase": "layer_applied",
                "offenders": offenders,
                "layer_height": layer_height,
                "check": check
            })

            if check["swarm_ok"] and check["dynamic_ok"]:
                unresolved = False
                status = "RESOLVED_WITH_LAYER"
                return trajectories, duration, status, report

    # --- Nessuna strategia ha risolto ---
    status = "UNRESOLVED_COLLISION" if unresolved else "OK"
    if unresolved:
        report["warning"] = "Collisioni non risolvibili con le strategie configurate."
        report["final_check"] = check

    return trajectories, duration, status, report'''



