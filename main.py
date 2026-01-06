import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

from models.drone import Drone
from models.trajectory import Trajectory
from core.trajectory_validator import validate_swarm_trajectories
from core.trajectory_postprocessor import resolve_collisions_with_start_delays_me

def linear_trajectory(p0, pf, duration):
    """Ritorna funzione di traiettoria lineare 3D da p0 a pf in duration secondi."""
    p0 = np.array(p0, dtype=float)
    pf = np.array(pf, dtype=float)
    def traj(t):
        s = np.clip(t / duration, 0, 1)
        return (1 - s) * p0 + s * pf
    return traj

def main():
    # ------------------------------
    # 1. Due droni che si incrociano
    # ------------------------------
    drones = [
        Drone(drone_id=0, initial_position=[0, 0, 0], max_velocity=2.0, max_acceleration=3.0),
        Drone(drone_id=1, initial_position=[0, 1, 0], max_velocity=2.0, max_acceleration=3.0)
    ]
    duration = 10.0

    # Drone 0: va da (0,0,0) a (1,1,0)
    traj0 = Trajectory(duration, linear_trajectory([0,0,0], [1,1,0], duration))
    # Drone 1: va da (0,1,0) a (1,0,0)
    traj1 = Trajectory(duration, linear_trajectory([0,1,0], [1,0,0], duration))

    trajectories = {0: traj0, 1: traj1}

    # ------------------------------
    # 2. Controllo collisioni prima
    # ------------------------------
    violations_before = validate_swarm_trajectories(trajectories, drones, min_distance=0.3, dt=0.05)
    print("Violazioni iniziali:", violations_before)

    # ------------------------------
    # 3. Risoluzione collisioni con ritardi
    # ------------------------------
    trajectories, report = resolve_collisions_with_start_delays_me(
        trajectories, drones,
        min_distance=0.3,
        dt=0.05,
        delay_step=0.5,
        max_iters=5,
        max_total_delay=20.0
    )
    print("Collision resolver report:", report)

    # ------------------------------
    # 4. Animazione 3D
    # ------------------------------
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlim(-0.2, 1.2)
    ax.set_ylim(-0.2, 1.2)
    ax.set_zlim(0, 0.5)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("Two Drones - Collision Avoidance with Start Delays")

    colors = ['r', 'b']
    markers = ['o', '^']

    scatters = {}
    for idx, did in enumerate(trajectories.keys()):
        scat = ax.scatter([], [], [], color=colors[idx % len(colors)],
                          s=80, label=f"Drone {did}", marker=markers[idx % len(markers)])
        scatters[did] = scat

    ax.legend()

    dt_anim = 0.05
    t_max = duration + max(traj.start_time for traj in trajectories.values()) + 1.0
    t_values = np.arange(0, t_max, dt_anim)

    def update(frame):
        t = t_values[frame]
        for did, traj in trajectories.items():
            pos = traj.position(t)
            scatters[did]._offsets3d = ([pos[0]], [pos[1]], [pos[2]])
        return scatters.values()

    ani = FuncAnimation(fig, update, frames=len(t_values), interval=dt_anim*1000, blit=False)
    plt.show()


if __name__ == "__main__":
    main()
