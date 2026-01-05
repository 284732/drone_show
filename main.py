
# main.py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from models.drone import Drone
from core.assignment_solver import assign_drones_to_targets
from core.formation_generator import line_formation, circle_formation_normal, transform_formation
from core.trajectory_postprocessor import auto_process_trajectories


# ---------- Utility: droni in griglia ----------
def build_grid_swarm(rows, cols, spacing=1.2, z=0.5):
    """
    Crea droni disposti su una griglia (rows x cols) centrata sull'origine, alla quota z.
    Default z=0.5 per vederli bene sopra il piano.
    """
    xs = (np.arange(cols) - (cols - 1) / 2.0) * spacing
    ys = (np.arange(rows) - (rows - 1) / 2.0) * spacing
    XX, YY = np.meshgrid(xs, ys)

    positions = np.column_stack([XX.ravel(), YY.ravel(), np.full(XX.size, z, dtype=float)])
    drones = [
        Drone(drone_id=i + 1, initial_position=positions[i], max_velocity=2.0, max_acceleration=2.0)
        for i in range(positions.shape[0])
    ]
    return drones


# ---------- Utility: esegui una fase ----------
def run_segment(
    drones,
    formation,
    base_duration,
    min_distance,
    dt_check=0.02,
    strategies=("delay", "layer"),
    delay_step=0.2,
    layer_h=0.3,
    max_time_scale_iters=10,
    max_delay_iters=5,
):
    """
    Esegue una fase:
      - Hungarian assignment,
      - auto-process (time-scaling + risoluzione collisioni),
      - ritorna traiettorie, durata, stato, report, assignment, posizioni finali globali.
    """
    assignment = assign_drones_to_targets(drones, formation)

    trajectories, final_duration, status, report = auto_process_trajectories(
        drones, assignment, base_duration,
        min_distance=min_distance, dt=dt_check,
        max_time_scale_iters=max_time_scale_iters, max_delay_iters=max_delay_iters,
        delay_step=delay_step, layer_height=layer_h,
        try_strategies=strategies,
    )

    # posizioni finali globali (t = start_time + duration) per ciascun drone
    end_positions = {}
    for d in drones:
        traj = trajectories[d.drone_id]
        t_end = traj.start_time + traj.duration
        end_positions[d.drone_id] = traj.position(t_end)

    return trajectories, final_duration, status, report, assignment, end_positions


# ---------- Utility: limiti assi e piano terreno ----------
def set_axis_limits(ax, initial_positions, all_assignments, pad=1.0):
    """
    Imposta limiti assi includendo tutte le posizioni iniziali e i target di tutte le fasi.
    Forza l'inclusione del piano z=0 con margine.
    """
    pts = [*initial_positions]
    for assign in all_assignments:
        pts.extend(assign.values())
    pts = np.array(pts)

    xmin, xmax = pts[:, 0].min(), pts[:, 0].max()
    ymin, ymax = pts[:, 1].min(), pts[:, 1].max()
    zmin, zmax = pts[:, 2].min(), pts[:, 2].max()

    zmin = min(zmin, 0.0)  # includi sempre il terreno

    ax.set_xlim(xmin - pad, xmax + pad)
    ax.set_ylim(ymin - pad, ymax + pad)
    ax.set_zlim(zmin - pad, zmax + pad)

    # Proporzioni più equilibrate (se disponibile)
    try:
        ax.set_box_aspect([xmax - xmin + 2*pad, ymax - ymin + 2*pad, zmax - zmin + 2*pad])
    except Exception:
        pass


def draw_ground_plane(ax, xmin, xmax, ymin, ymax, z=0.0, alpha=0.10, color='k'):
    xs = np.linspace(xmin, xmax, 2)
    ys = np.linspace(ymin, ymax, 2)
    XX, YY = np.meshgrid(xs, ys)
    ZZ = np.full_like(XX, z)
    ax.plot_surface(XX, YY, ZZ, alpha=alpha, color=color)


# ---------- Animazione: concatena fasi ----------
def animate_show(drones, segments, titles, dt_anim=0.02):
    """
    segments: lista di dict, ciascuno con:
        {
            "trajectories": dict {drone_id: Trajectory},
            "assignment": dict {drone_id: target_position},
            "t0": float (offset di inizio segmento, globale),
            "t_end": float (fine globale del segmento),
        }
    """
    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111, projection="3d")

    # Limiti assi e piano terreno
    initial_positions = np.array([d.initial_position for d in drones])
    set_axis_limits(ax, initial_positions, [seg["assignment"] for seg in segments], pad=1.0)
    draw_ground_plane(ax, ax.get_xlim()[0], ax.get_xlim()[1], ax.get_ylim()[0], ax.get_ylim()[1], z=0.0)

    ax.set_xlabel("X [m]")
    ax.set_ylabel("Y [m]")
    ax.set_zlabel("Z [m]")

    # Timeline globale
    T_total = segments[-1]["t_end"]
    ts = np.arange(0, T_total + dt_anim, dt_anim)

    # Scatter iniziale (t=0)
    colors = plt.cm.tab20(np.linspace(0, 1, len(drones)))
    sizes = np.full(len(drones), 80)
    scat = ax.scatter(initial_positions[:, 0], initial_positions[:, 1], initial_positions[:, 2], s=sizes, c=colors, label="Droni")

    # Tracce (una per drone)
    lines = [ax.plot([], [], [], lw=1.5, c=colors[i])[0] for i in range(len(drones))]

    # Target del segmento attivo (grigi)
    tgt = np.array([segments[0]["assignment"][d.drone_id] for d in drones])
    tgt_scatter = ax.scatter(tgt[:, 0], tgt[:, 1], tgt[:, 2], c="gray", s=30, marker="o", label=f"Target (fase 1: {titles[0]})")

    ax.set_title(f"Show — Fase 1: {titles[0]}")

    def init():
        for ln in lines:
            ln.set_data([], [])
            ln.set_3d_properties([])
        return [scat, *lines, tgt_scatter]

    def get_positions_at_time(t):
        """Posizioni globali al tempo t, valutando il segmento attivo."""
        active_idx = None
        for i, seg in enumerate(segments):
            if seg["t0"] <= t <= seg["t_end"]:
                active_idx = i
                break

        if active_idx is None:
            last_seg = segments[-1]
            positions = np.array([
                last_seg["trajectories"][d.drone_id].position(last_seg["t_end"])
                for d in drones
            ])
        else:
            seg = segments[active_idx]
            positions = np.array([
                seg["trajectories"][d.drone_id].position(t)
                for d in drones
            ])
        return positions, active_idx

    def update(frame_idx):
        t = ts[frame_idx]
        pos, active_idx = get_positions_at_time(t)

        # Droni
        scat._offsets3d = (pos[:, 0], pos[:, 1], pos[:, 2])

        # Tracce cumulative fino a t
        for i, d in enumerate(drones):
            path = np.array([get_positions_at_time(tt)[0][i] for tt in ts[:frame_idx + 1]])
            lines[i].set_data(path[:, 0], path[:, 1])
            lines[i].set_3d_properties(path[:, 2])

        # Aggiorna target e titolo in base alla fase attiva
        if active_idx is not None:
            tgt = np.array([segments[active_idx]["assignment"][d.drone_id] for d in drones])
            tgt_scatter._offsets3d = (tgt[:, 0], tgt[:, 1], tgt[:, 2])
            tgt_scatter.set_label(f"Target (fase {active_idx + 1}: {titles[active_idx]})")
            ax.set_title(f"Show — Fase {active_idx + 1}: {titles[active_idx]}")

        # Rotazione lenta della camera (estetica)
        ax.view_init(elev=25, azim=(frame_idx * 0.4) % 360)
        return [scat, *lines, tgt_scatter]

    ani = FuncAnimation(fig, update, frames=len(ts), init_func=init, interval=1, blit=False)
    plt.legend()
    plt.tight_layout()
    plt.show()


def main():
    # ---------------- Parametri dello show ----------------
    rows, cols = 3, 4                 # griglia 3x4 → 12 droni
    spacing = 1.2                     # passo griglia
    z0 = 0.5                          # quota iniziale per vederli subito
    base_duration = 5.0               # durata desiderata per ogni fase (scalata se serve)
    min_distance = 0.35               # soglia di distanza minima
    dt_check = 0.02                   # passo di verifica/animazione

    # Strategie per risolvere collisioni: prima delay, poi layer
    strategies = ("delay", "layer")
    delay_step = 0.2
    layer_h = 0.3

    # ---------------- 1) Sciame in griglia ----------------
    drones = build_grid_swarm(rows, cols, spacing=spacing, z=z0)
    print("Droni (griglia):")
    for d in drones:
        print("  ", d)

    # ---------------- 2) Fase: Griglia → Linea (asse X a quota 6 m, lunga 12 m) ----------------
    line = line_formation(num_points=len(drones), length=12.0, axis='x')
    line = transform_formation(line, translation_vec=(0.0, 0.0, 6.0))  # porta a z=6

    traj_line, dur_line, status_line, report_line, assign_line, end_line = run_segment(
        drones, line, base_duration, min_distance, dt_check=dt_check,
        strategies=strategies, delay_step=delay_step, layer_h=layer_h
    )
    print(f"\n[Fase 1: Griglia→Linea] Durata finale: {dur_line:.2f}s | Stato: {status_line}")

    # Aggiorna le posizioni iniziali con le posizioni finali della fase 1
    for d in drones:
        d.initial_position = end_line[d.drone_id]

    # ---------------- 3) Fase: Linea → Cerchio (piano XY a quota 10 m, raggio 5) ----------------
    circle = circle_formation_normal(
        num_points=len(drones),
        radius=5.0,
        center=(0.0, 0.0, 10.0),
        normal=(0.0, 0.0, 1.0),
    )

    traj_circle, dur_circle, status_circle, report_circle, assign_circle, end_circle = run_segment(
        drones, circle, base_duration, min_distance, dt_check=dt_check,
        strategies=strategies, delay_step=delay_step, layer_h=layer_h
    )
    print(f"[Fase 2: Linea→Cerchio] Durata finale: {dur_circle:.2f}s | Stato: {status_circle}")

    # ---------------- 4) Costruisci timeline globale e anima ----------------
    # Offset tempi globali
    t0_1 = 0.0
    t_end_1 = max(traj_line[did].start_time + traj_line[did].duration for did in traj_line.keys())
    for did in traj_line.keys():
        traj_line[did].start_time += t0_1

    t0_2 = t_end_1
    t_end_2 = t0_2 + max(traj_circle[did].start_time + traj_circle[did].duration for did in traj_circle.keys())
    for did in traj_circle.keys():
        traj_circle[did].start_time += t0_2

    segments = [
        {"trajectories": traj_line,   "assignment": assign_line,   "t0": t0_1, "t_end": t_end_1},
        {"trajectories": traj_circle, "assignment": assign_circle, "t0": t0_2, "t_end": t_end_2},
    ]
    titles = ["Linea (z=6 m)", "Cerchio (z=10 m, r=5 m)"]

    animate_show(drones, segments, titles, dt_anim=dt_check)


if __name__ == "__main__":
    main()
