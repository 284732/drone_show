# main_offline.py

import yaml
from models.drone import Drone
from core.formation_generator import circle_formation, line_formation, grid_formation
from core.assignment_solver import assign_drones_to_targets
from core.trajectory_generator import generate_trajectories
from core.trajectory_validator import validate_trajectory, validate_swarm_trajectories
from utils.visualization import plot_trajectories

# -----------------------
# 1. Carica configurazioni
# -----------------------
with open("config/drone_config.yaml") as f:
    drones_conf = yaml.safe_load(f)
drones = [Drone(**d) for d in drones_conf["drones"]]

with open("config/show_config.yaml") as f:
    show_conf = yaml.safe_load(f)
show_params = show_conf["show"]
duration = show_params["duration"]
formation_type = show_params["formation"]

# -----------------------
# 2. Genera formazione direttamente in memoria
# -----------------------
if formation_type == "circle":
    formation = circle_formation(len(drones), radius=show_params["formation_radius"])
elif formation_type == "line":
    formation = line_formation(len(drones), length=show_params.get("formation_length", 4.0))
elif formation_type == "grid":
    formation = grid_formation(show_params["formation_rows"], show_params["formation_cols"],
                               spacing=show_params.get("formation_spacing", 1.0))
else:
    raise ValueError("Tipo formazione non valido")

# -----------------------
# 3. Assegna droni ai target
# -----------------------
assignment = assign_drones_to_targets(drones, formation)

# -----------------------
# 4. Genera traiettorie
# -----------------------
trajectories = generate_trajectories(drones, assignment, duration)

# -----------------------
# 5. Validazione
# -----------------------
print("\n--- Validazione singolo drone ---")
for d in drones:
    result = validate_trajectory(trajectories[d.drone_id], d)
    print(f"Drone {d.drone_id}: {result}")

violations = validate_swarm_trajectories(trajectories, drones, min_distance=show_params["min_distance"])
if violations:
    print("\nAttenzione! Collisioni previste tra droni:")
    for v in violations:
        print(v)
else:
    print("\nNessuna collisione prevista tra droni.")

# -----------------------
# 6. Visualizzazione offline
# -----------------------
plot_trajectories(trajectories)

print("\nSimulazione offline completata.")
