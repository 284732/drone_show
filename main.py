'''
PER LINEA
import yaml
import numpy as np
from models.drone import Drone
from core.formation_generator import line_formation, circle_formation_normal
from core.trajectory_generator import generate_trajectories
from core.assignment_solver import assign_drones_to_targets
from core.trajectory_validator import check_constraints_and_collisions
from core.trajectory_postprocessor import time_scale_trajectories, resolve_collisions_with_start_delays_me
import matplotlib.pyplot as plt
from matplotlib import animation


###############
#   LETTURA YAML DRONI  #
###############
with open("config/drone_config.yaml", "r") as f:
    data = yaml.safe_load(f)

# Creiamo oggetti Drone
drones = []
for drone_info in data["drones"]:
    drone = Drone(
        drone_id=drone_info["drone_id"],
        initial_position=drone_info["initial_position"],
        max_velocity=drone_info["max_velocity"],
        max_acceleration=drone_info["max_acceleration"]
    )
    drones.append(drone)

# Verifica
print("Print dei droni istanziati:")
for d in drones:
    print(d)


###############
#   GENERAZIONE FORMAZIONE  #
###############
num_drones = len(drones)
formation_line = line_formation(num_points=num_drones, length=10, axis='y')


###############
#   ASSEGNAZIONE DRONE->TRGET   #
###############
assignment_line = assign_drones_to_targets(drones=drones, formation=formation_line) # dizionario
for d_id, final_pos in assignment_line.items():     # .items() ci restituisce una tupla (chiave, valore)
    print(f"Drone {d_id} -> Target {final_pos}")


###############
#   CREAZIONE TRAIETTORIE NON CONTROLLATE   #
###############
time_duration = 5.0     # secondi
# ogni traiettoria è un oggetto Trajectory, trajectories sarà un dizionario
trajectories_line = generate_trajectories(drones=drones, assignment=assignment_line, duration=time_duration)


###############
#   POST PROCESSING: TIME SCALED   #
###############
trajectories_line, time_duration_scaled_line = time_scale_trajectories(
    drones=drones,
    assignment=assignment_line,
    duration=time_duration,
    max_iterations=5,
    dt_check=0.01)
print(f"Durata finale dopo scaling: {time_duration_scaled_line:.2f} s")


###############
#   POST PROCESSING: RISOLUZIONE EVENTUALI COLLISIONI -> TRAMITE RITARDI   #
###############
trajectories_line, collision_info = resolve_collisions_with_start_delays_me(
    trajectories=trajectories_line,
    drones=drones,
    min_distance=0.5,
    dt=0.01,
    delay_step=3,
    max_iters=5,
    max_total_delay=10)
print("Collision info:", collision_info)


###############
#   FINAL VALIDATION   #
###############
validation_line = check_constraints_and_collisions(
    trajectories=trajectories_line,
    drones=drones,
    min_distance=0.5,
    dt=0.01)
print("Validazione finale linea: ", validation_line["dynamic_ok"], validation_line["swarm_ok"])


###############
#   PLOT    #
###############
fig = plt.figure(figsize=(10,8))
ax = fig.add_subplot(111, projection='3d')

# Imposta limiti asse
all_positions = np.vstack([d.initial_position for d in drones] + [formation_line.target_positions])
xyz_min = all_positions.min(axis=0) - 1
xyz_max = all_positions.max(axis=0) + 1
ax.set_xlim(xyz_min[0], xyz_max[0])
ax.set_ylim(xyz_min[1], xyz_max[1])
ax.set_zlim(xyz_min[2], xyz_max[2])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title("Animazione droni verso formazione")

# Plot target
ax.scatter(formation_line.target_positions[:,0], formation_line.target_positions[:,1], formation_line.target_positions[:,2],
           color='red', s=50, label='Target')

# Crea punti dei droni
points = [ax.plot([], [], [], 'o', label=f"Drone {d.drone_id}")[0] for d in drones]

# Numero frame e timestep
fps = 20
num_frames = int(time_duration_scaled_line * fps)
times = np.linspace(0, time_duration_scaled_line, num_frames)

def init():
    for p in points:
        p.set_data([], [])
        p.set_3d_properties([])
    return points

def animate(i):
    t = times[i]
    for idx, d in enumerate(drones):
        pos = trajectories_line[d.drone_id].position(t)
        points[idx].set_data([pos[0]], [pos[1]])
        points[idx].set_3d_properties([pos[2]])
    return points


ani = animation.FuncAnimation(fig, animate, frames=num_frames, init_func=init, blit=True)

plt.legend()
plt.show()'''

'''
PER CERCHIO
import yaml
import numpy as np
from models.drone import Drone
from core.formation_generator import circle_formation_normal
from core.trajectory_generator import generate_trajectories
from core.assignment_solver import assign_drones_to_targets
from core.trajectory_validator import check_constraints_and_collisions
from core.trajectory_postprocessor import time_scale_trajectories, resolve_collisions_with_start_delays_me
import matplotlib.pyplot as plt
from matplotlib import animation

###############
#   LETTURA YAML DRONI  #
###############
with open("config/drone_config.yaml", "r") as f:
    data = yaml.safe_load(f)

# Creiamo oggetti Drone
drones = []
for drone_info in data["drones"]:
    drone = Drone(
        drone_id=drone_info["drone_id"],
        initial_position=drone_info["initial_position"],
        max_velocity=drone_info["max_velocity"],
        max_acceleration=drone_info["max_acceleration"]
    )
    drones.append(drone)

# Verifica
print("Print dei droni istanziati:")
for d in drones:
    print(d)

###############
#   GENERAZIONE FORMAZIONE CERCHIO  #
###############
num_drones = len(drones)
formation_circle = circle_formation_normal(
    num_points=num_drones,
    radius=3.0,              # puoi aumentare/ridurre il raggio
    center=(0, 0, 0),
    normal=(0, 0, 1)         # piano XY
)

###############
#   ASSEGNAZIONE DRONE->TARGET  #
###############
assignment_circle = assign_drones_to_targets(drones=drones, formation=formation_circle)
for d_id, final_pos in assignment_circle.items():
    print(f"Drone {d_id} -> Target {final_pos}")

###############
#   CREAZIONE TRAIETTORIE NON CONTROLLATE  #
###############
time_duration = 0.1
trajectories_circle = generate_trajectories(
    drones=drones,
    assignment=assignment_circle,
    duration=time_duration
)

###############
#   POST PROCESSING: TIME SCALED  #
###############
trajectories_circle, time_duration_scaled_circle = time_scale_trajectories(
    drones=drones,
    assignment=assignment_circle,
    duration=time_duration,
    max_iterations=5,
    dt_check=0.01
)
print(f"Durata finale dopo scaling: {time_duration_scaled_circle:.2f} s")

###############
#   RISOLUZIONE EVENTUALI COLLISIONI  #
###############
trajectories_circle, collision_info = resolve_collisions_with_start_delays_me(
    trajectories=trajectories_circle,
    drones=drones,
    min_distance=0.5,
    dt=0.01,
    delay_step=3,
    max_iters=5,
    max_total_delay=10
)
print("Collision info:", collision_info)

###############
#   VALIDAZIONE FINALE  #
###############
validation_circle = check_constraints_and_collisions(
    trajectories=trajectories_circle,
    drones=drones,
    min_distance=0.5,
    dt=0.01
)
print("Validazione finale cerchio: ", validation_circle["dynamic_ok"], validation_circle["swarm_ok"])

###############
#   PLOT ANIMATO  #
###############
fig = plt.figure(figsize=(10,8))
ax = fig.add_subplot(111, projection='3d')

# Limiti asse
all_positions = np.vstack([d.initial_position for d in drones] + [formation_circle.target_positions])
xyz_min = all_positions.min(axis=0) - 1
xyz_max = all_positions.max(axis=0) + 1
ax.set_xlim(xyz_min[0], xyz_max[0])
ax.set_ylim(xyz_min[1], xyz_max[1])
ax.set_zlim(xyz_min[2], xyz_max[2])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title("Animazione droni verso formazione cerchio")

# Plot target
ax.scatter(formation_circle.target_positions[:,0],
           formation_circle.target_positions[:,1],
           formation_circle.target_positions[:,2],
           color='red', s=50, label='Target')

# Crea punti dei droni
points = [ax.plot([], [], [], 'o', label=f"Drone {d.drone_id}")[0] for d in drones]

# Frame e timestep
fps = 20  # meno frame per animazione più veloce e fluida
num_frames = int(time_duration_scaled_circle * fps)
times = np.linspace(0, time_duration_scaled_circle, num_frames)

def init():
    for p in points:
        p.set_data([], [])
        p.set_3d_properties([])
    return points

def animate(i):
    t = times[i]
    for idx, d in enumerate(drones):
        pos = trajectories_circle[d.drone_id].position(t)
        points[idx].set_data([pos[0]], [pos[1]])
        points[idx].set_3d_properties([pos[2]])
    return points

ani = animation.FuncAnimation(fig, animate, frames=num_frames, init_func=init, blit=True)

plt.legend()
plt.show()
'''

import yaml
import numpy as np
from models.drone import Drone
from core.formation_generator import circle_formation_normal
from core.trajectory_generator import generate_trajectories
from core.assignment_solver import assign_drones_to_targets
from core.trajectory_validator import check_constraints_and_collisions
from core.trajectory_postprocessor import time_scale_trajectories, resolve_collisions_with_start_delays_me
import matplotlib.pyplot as plt
from matplotlib import animation

###############
#   LETTURA YAML DRONI  #
###############
with open("config/drone_config.yaml", "r") as f:
    data = yaml.safe_load(f)

# Creiamo oggetti Drone
drones = []
for drone_info in data["drones"]:
    drone = Drone(
        drone_id=drone_info["drone_id"],
        initial_position=drone_info["initial_position"],
        max_velocity=drone_info["max_velocity"],
        max_acceleration=drone_info["max_acceleration"]
    )
    drones.append(drone)

num_drones = len(drones)  # numero di droni
print("Droni istanziati:")
for d in drones:
    print(d)

###############
#   FORMAZIONE 1: cerchio grande
###############
formation1 = circle_formation_normal(
    num_points=num_drones,
    radius=3.0,
    center=(0, 0, 0),
    normal=(0, 0, 1)
)

assignment1 = assign_drones_to_targets(drones, formation1)
trajectories1 = generate_trajectories(drones, assignment1, duration=5.0)
trajectories1, duration1 = time_scale_trajectories(drones, assignment1, 5.0)
trajectories1, _ = resolve_collisions_with_start_delays_me(trajectories1, drones)

###############
#   FORMAZIONE 2: cerchio piccolo spostato
###############
# Usare fine traiettoria 1 come inizio
start_positions2 = {d.drone_id: trajectories1[d.drone_id].position(duration1) for d in drones}

# Creiamo nuovi Drone temporanei per assegnazione
drones_start2 = [Drone(d.drone_id, start_positions2[d.drone_id], d.max_velocity, d.max_acceleration) for d in drones]

formation2 = circle_formation_normal(
    num_points=num_drones,
    radius=1.5,
    center=(5, 0, 0),
    normal=(0, 0, 1)
)

assignment2 = assign_drones_to_targets(drones_start2, formation2)
trajectories2 = generate_trajectories(drones, assignment2, duration=5.0)
trajectories2, duration2 = time_scale_trajectories(drones_start2, assignment2, 5.0)
trajectories2, _ = resolve_collisions_with_start_delays_me(trajectories2, drones)

###############
#   FUNZIONE GLOBALE PER POSIZIONI
###############
def position_global(did, t):
    if t <= duration1:
        return trajectories1[did].position(t)
    else:
        return trajectories2[did].position(t - duration1)

total_duration = duration1 + duration2

###############
#   VALIDAZIONE FINALE
###############
validation1 = check_constraints_and_collisions(trajectories1, drones)
validation2 = check_constraints_and_collisions(trajectories2, drones)
print("Validazione formazione 1:", validation1["dynamic_ok"], validation1["swarm_ok"])
print("Validazione formazione 2:", validation2["dynamic_ok"], validation2["swarm_ok"])

###############
#   ANIMAZIONE LIVE
###############
fig = plt.figure(figsize=(10,8))
ax = fig.add_subplot(111, projection='3d')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title("Animazione droni: due cerchi concatenati")

# Limiti assi (considera entrambe le formazioni)
all_positions = np.vstack([formation1.target_positions, formation2.target_positions])
xyz_min = all_positions.min(axis=0) - 1
xyz_max = all_positions.max(axis=0) + 1
ax.set_xlim(xyz_min[0], xyz_max[0])
ax.set_ylim(xyz_min[1], xyz_max[1])
ax.set_zlim(xyz_min[2], xyz_max[2])

# Punti droni
points = [ax.plot([], [], [], 'o', label=f"Drone {d.drone_id}")[0] for d in drones]

# Frame e timestep
fps = 20
num_frames = int(total_duration * fps)
times = np.linspace(0, total_duration, num_frames)

def init():
    for p in points:
        p.set_data([], [])
        p.set_3d_properties([])
    return points

def animate(i):
    t = times[i]
    for idx, d in enumerate(drones):
        pos = position_global(d.drone_id, t)
        points[idx].set_data([pos[0]], [pos[1]])
        points[idx].set_3d_properties([pos[2]])
    return points

ani = animation.FuncAnimation(fig, animate, frames=num_frames, init_func=init, blit=True)

# Mostra i target di entrambe le formazioni
ax.scatter(formation1.target_positions[:,0], formation1.target_positions[:,1], formation1.target_positions[:,2], color='red', s=50, label='Target 1')
ax.scatter(formation2.target_positions[:,0], formation2.target_positions[:,1], formation2.target_positions[:,2], color='green', s=50, label='Target 2')

plt.legend()
plt.show()
