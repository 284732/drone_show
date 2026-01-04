import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

def plot_trajectories(trajectories, labels=None, show=True):
    """
    Plot 3D delle traiettorie di più droni.

    :param trajectories: dict {drone_id: Trajectory}
    :param labels: dict opzionale {drone_id: label}
    :param show: mostra subito il grafico
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for drone_id, traj in trajectories.items():
        t, pos = traj.sample(50)
        label = labels[drone_id] if labels and drone_id in labels else f"Drone {drone_id}"
        ax.plot(pos[:, 0], pos[:, 1], pos[:, 2], label=label)

    ax.set_xlabel("X [m]")
    ax.set_ylabel("Y [m]")
    ax.set_zlabel("Z [m]")
    ax.legend()
    ax.grid(True)
    ax.set_box_aspect([1,1,0.5])

    if show:
        plt.show()
