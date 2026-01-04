import time

class TrajectorySender:
    """
    Invia le traiettorie calcolate ai droni in CoppeliaSim.
    """
    def __init__(self, client, drone_handles):
        """
        :param client: istanza CoppeliaClient
        :param drone_handles: dict {drone_id: handle CoppeliaSim}
        """
        self.client = client
        self.drone_handles = drone_handles

    def send_trajectories(self, trajectories, dt=0.05):
        """
        Invia le traiettorie campionate ai droni.
        Nota: questa è una simulazione “a passo discreto”,
        il vero tracking è gestito dal drone script Lua.
        """
        duration = max(traj.duration for traj in trajectories.values())
        t_samples = int(duration / dt) + 1

        for step in range(t_samples):
            t = step * dt
            for drone_id, traj in trajectories.items():
                pos = traj.position(t)
                handle = self.drone_handles[drone_id]
                self.client.set_drone_position(handle, pos)
            self.client.step(dt)
