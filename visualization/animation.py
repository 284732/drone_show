import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def sample_bounds(trajectories, t_start, t_end, dt=0.05):
    xs, ys, zs = [], [], []
    t_values = np.arange(t_start, t_end + dt, dt)
    for t in t_values:
        for traj in trajectories.values():
            p = traj.position(t)
            xs.append(p[0]); ys.append(p[1]); zs.append(p[2])
    return (min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs))

def animate_3d(all_trajectories, meta, dt_anim=0.05, margin=0.5):
    total_duration = meta.get("total_duration", 0.0)
    t_values = np.arange(0, total_duration, dt_anim)

    (xmin, xmax), (ymin, ymax), (zmin, zmax) = sample_bounds(all_trajectories, 0.0, total_duration, dt=0.1)
    xmin -= margin; xmax += margin
    ymin -= margin; ymax += margin
    zmin = max(0.0, zmin - margin); zmax += margin

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_zlim(zmin, zmax)
    ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z")
    ax.set_title("Drone Show Animation")

    colors = ['r', 'g', 'b', 'm', 'c', 'y', 'k']
    markers = ['o', '^', 's', 'D', 'v', '*', 'p']

    scatters = {}
    for idx, did in enumerate(sorted(all_trajectories.keys())):
        scat = ax.scatter([], [], [], color=colors[idx % len(colors)],
                          s=50, label=f"Drone {did}", marker=markers[idx % len(markers)])
        scatters[did] = scat

    ax.legend()

    def update(frame):
        t = t_values[frame]
        for did, traj in all_trajectories.items():
            pos = traj.position(t)
            scatters[did]._offsets3d = ([pos[0]], [pos[1]], [pos[2]])
        return scatters.values()

    FuncAnimation(fig, update, frames=len(t_values), interval=dt_anim * 1000, blit=False)
    plt.show()
