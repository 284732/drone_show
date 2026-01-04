import numpy as np

from models.drone import Drone
from core.assignment_solver import assign_drones_to_targets
from core.formation_generator import circle_formation
from core.trajectory_generator import generate_trajectories
from core.trajectory_validator import validate_trajectory, validate_swarm_trajectories
from utils.visualization import plot_trajectories

def main():
    # 1) Crea alcuni droni
    drones = [
        Drone(1, [0.0, 0.0, 0.0], 2.0, 2.5),
        Drone(2, [1.0, 0.0, 0.0], 2.0, 2.5),
        Drone(3, [0.5, 1.0, 0.0], 2.0, 2.5),
    ]

    # 2) Genera una formazione (cerchio r=2)
    formation = circle_formation(num_points=len(drones), radius=2.0)

    # 3) Instanzia assignment (Hungarian)
    assignment = assign_drones_to_targets(drones, formation)
    print("Assignment:", assignment)

    # 4) Genera traiettorie minimum-jerk (durata 3 secondi)
    duration = 3.0
    trajectories = generate_trajectories(drones, assignment, duration)

    # 5) Valida ogni traiettoria (velocità/accelerazione)
    print("\nValidazione per-drone:")
    for d in drones:
        stats = validate_trajectory(trajectories[d.drone_id], d, dt=0.02)
        print(f"Drone {d.drone_id}:", stats)

    # 6) Controlla collisioni
    collisions = validate_swarm_trajectories(trajectories, drones, min_distance=0.6, dt=0.02)
    print("\nCollisioni trovate:", collisions[:5], "..." if collisions else "(nessuna)")

    # 7) Visualizza le traiettorie
    plot_trajectories(trajectories, show=True)

if __name__ == "__main__":
    main()
