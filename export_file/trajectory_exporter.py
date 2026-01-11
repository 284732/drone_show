
"""
Exporter CSV delle traiettorie (posizioni + velocità stimate da posizioni).
"""

import csv
import numpy as np
from pathlib import Path


def _safe_filename(drone_id):
    try:
        return f"drone_{int(drone_id):03d}_trajectory.csv"
    except (ValueError, TypeError):
        sid = str(drone_id).strip().replace(" ", "_")
        return f"drone_{sid}_trajectory.csv"


def _central_diff_velocity(get_pos_fn, drone_id, t, dt, t0, t_end):
    """
    Stima v(t) con differenze finite centrali dove possibile, altrimenti forward/backward.
    """
    if dt <= 0:
        return np.array([0.0, 0.0, 0.0], dtype=float)

    # Proviamo centrale se ci sta dentro
    t_prev = t - dt
    t_next = t + dt
    if t_prev >= t0 and t_next <= t_end:
        p_prev = get_pos_fn(drone_id, t_prev)
        p_next = get_pos_fn(drone_id, t_next)
        return (p_next - p_prev) / (2.0 * dt)

    # Bordo iniziale → forward
    if t_next <= t_end:
        p_curr = get_pos_fn(drone_id, t)
        p_next = get_pos_fn(drone_id, t_next)
        return (p_next - p_curr) / dt

    # Bordo finale → backward
    if t_prev >= t0:
        p_prev = get_pos_fn(drone_id, t_prev)
        p_curr = get_pos_fn(drone_id, t)
        return (p_curr - p_prev) / dt

    # Caso degenerato
    return np.array([0.0, 0.0, 0.0], dtype=float)


def export_trajectories_to_csv(
    sequencer,
    drones,
    total_duration,
    output_dir="trajectories_csv",
    fps=30,
    include_endpoint=False,
    delimiter=","
):
    """
    Esporta file per-drone con t,x,y,z + vx,vy,vz (velocità stimate da posizioni).
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    dt = 1.0 / fps if fps > 0 else 0.0
    num_samples = int(total_duration * fps) + (1 if include_endpoint else 0)
    num_samples = max(num_samples, 1)  # garantisce almeno 1 campione
    timestamps = np.linspace(0, total_duration, num_samples)

    created_files = {}

    print(f"\n📊 Esportazione traiettorie in CSV...")
    print(f"   • Cartella di output: {output_path}/")
    print(f"   • Campionamento: {fps} FPS (dt = {dt:.4f} s) — include_endpoint={include_endpoint}")
    print(f"   • Durata: {total_duration:.3f} s")
    print(f"   • Campioni per drone: {len(timestamps)}")
    print("-" * 60)

    for drone in drones:
        drone_id = drone.drone_id
        filename = _safe_filename(drone_id)
        filepath = output_path / filename

        rows = []
        for t in timestamps:
            pos = np.asarray(sequencer.get_position(drone_id, float(t)), dtype=float)
            if not np.all(np.isfinite(pos)):
                pos = np.array([np.nan, np.nan, np.nan], dtype=float)

            vel = _central_diff_velocity(
                get_pos_fn=sequencer.get_position,
                drone_id=drone_id,
                t=float(t),
                dt=dt,
                t0=0.0,
                t_end=float(total_duration)
            )
            if not np.all(np.isfinite(vel)):
                vel = np.array([np.nan, np.nan, np.nan], dtype=float)

            rows.append({
                "t": float(t),
                "x": float(pos[0]),
                "y": float(pos[1]),
                "z": float(pos[2]),
                "vx": float(vel[0]),
                "vy": float(vel[1]),
                "vz": float(vel[2]),
            })

        # scrittura
        with open(filepath, "w", newline="") as csvfile:
            fieldnames = ["t", "x", "y", "z", "vx", "vy", "vz"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=delimiter)
            writer.writeheader()
            writer.writerows(rows)

        created_files[drone_id] = str(filepath)

        # statistiche
        if len(rows) >= 2:
            positions = np.array([[r["x"], r["y"], r["z"]] for r in rows], dtype=float)
            velocities = np.array([[r["vx"], r["vy"], r["vz"]] for r in rows], dtype=float)
            max_speed = np.nanmax(np.linalg.norm(velocities, axis=1))
            total_distance = np.nansum(np.linalg.norm(np.diff(positions, axis=0), axis=1))
        else:
            max_speed = 0.0
            total_distance = 0.0

        print(f"   ✅ Drone {drone_id}: {filename}")
        print(f"      • Velocità max: {max_speed:.2f} m/s")
        print(f"      • Distanza totale: {total_distance:.2f} m")

    print("-" * 60)
    print(f"✅ Esportati {len(created_files)} file CSV in {output_path}/")

    return created_files


def export_summary_csv(
    sequencer,
    drones,
    total_duration,
    output_dir="trajectories_csv",
    fps=30,
    include_endpoint=False,
    delimiter=","
):
    """
    Esporta un file unico (t,drone_id,x,y,z,vx,vy,vz) con v stimata da posizioni.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filepath = output_path / "all_drones_trajectory.csv"

    dt = 1.0 / fps if fps > 0 else 0.0
    num_samples = int(total_duration * fps) + (1 if include_endpoint else 0)
    num_samples = max(num_samples, 1)
    timestamps = np.linspace(0, total_duration, num_samples)

    print(f"\n📊 Esportazione file riassuntivo...")
    print(f"   • Righe previste: {len(drones) * len(timestamps)}")

    with open(filepath, "w", newline="") as csvfile:
        fieldnames = ["t", "drone_id", "x", "y", "z", "vx", "vy", "vz"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()

        for t in timestamps:
            for drone in drones:
                did = drone.drone_id
                pos = np.asarray(sequencer.get_position(did, float(t)), dtype=float)
                if not np.all(np.isfinite(pos)):
                    pos = np.array([np.nan, np.nan, np.nan], dtype=float)

                vel = _central_diff_velocity(
                    get_pos_fn=sequencer.get_position,
                    drone_id=did,
                    t=float(t),
                    dt=dt,
                    t0=0.0,
                    t_end=float(total_duration)
                )
                if not np.all(np.isfinite(vel)):
                    vel = np.array([np.nan, np.nan, np.nan], dtype=float)

                writer.writerow({
                    "t": float(t),
                    "drone_id": did,
                    "x": float(pos[0]),
                    "y": float(pos[1]),
                    "z": float(pos[2]),
                    "vx": float(vel[0]),
                    "vy": float(vel[1]),
                    "vz": float(vel[2]),
                })

    print(f"   ✅ File riassuntivo: {filepath}")
    print(f"      • {len(drones)} droni × {len(timestamps)} campioni = {len(drones) * len(timestamps)} righe")

    return str(filepath)


def export_trajectories_full(
    sequencer,
    drones,
    total_duration,
    output_dir="trajectories_csv",
    fps=30,
    include_summary=True,
    include_endpoint=False,
    delimiter=","
):
    """
    Export completo: file per-drone + opzionale riassuntivo.
    """
    individual_files = export_trajectories_to_csv(
        sequencer=sequencer,
        drones=drones,
        total_duration=total_duration,
        output_dir=output_dir,
        fps=fps,
        include_endpoint=include_endpoint,
        delimiter=delimiter
    )

    result = {
        "individual_files": individual_files,
        "output_dir": str(Path(output_dir)),
        "num_drones": len(drones),
        "num_samples": int(total_duration * fps) + (1 if include_endpoint else 0),
        "duration": float(total_duration),
        "dt": (1.0 / fps) if fps > 0 else np.nan
    }

    if include_summary:
        result["summary_file"] = export_summary_csv(
            sequencer=sequencer,
            drones=drones,
            total_duration=total_duration,
            output_dir=output_dir,
            fps=fps,
            include_endpoint=include_endpoint,
            delimiter=delimiter
        )

    return result
