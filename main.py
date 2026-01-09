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

# main_show.py
import yaml
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from models.drone import Drone
from models.show_sequencer import ShowSequencer


###############
# CARICA DRONI DA GUI OFFLINE
###############


###############
# CARICA DRONI
###############
with open("GUI_DronesShow/config/drone_config.yaml", "r") as f:
    data = yaml.safe_load(f)

drones = []
for drone_info in data["drones"]:
    drone = Drone(
        drone_id=drone_info["drone_id"],
        initial_position=drone_info["initial_position"],
        max_velocity=drone_info["max_velocity"],
        max_acceleration=drone_info["max_acceleration"]
    )
    drones.append(drone)

print(f"Droni caricati: {len(drones)}")

###############
# COSTRUISCI SHOW DALLA GUI CONFIG
###############
sequencer = ShowSequencer("config/show_config.yaml", drones)
total_duration = sequencer.build_show()

###############
# ANIMAZIONE
###############
fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(111, projection='3d')
ax.set_xlabel('X [m]')
ax.set_ylabel('Y [m]')
ax.set_zlabel('Z [m]')

# Calcola limiti da tutte le formazioni
all_formations = sequencer.get_all_formations()
all_positions = np.vstack(all_formations)
margin = 2.0
xyz_min = all_positions.min(axis=0) - margin
xyz_max = all_positions.max(axis=0) + margin
ax.set_xlim(xyz_min[0], xyz_max[0])
ax.set_ylim(xyz_min[1], xyz_max[1])
ax.set_zlim(xyz_min[2], xyz_max[2])

# Punti droni
points = [ax.plot([], [], [], 'o', markersize=10)[0] for d in drones]

# Mostra tutti i target delle formazioni
colors = ['red', 'green', 'blue', 'orange', 'purple', 'cyan', 'magenta', 'yellow']
for i, formation_pos in enumerate(all_formations):
    color = colors[i % len(colors)]
    ax.scatter(formation_pos[:, 0], formation_pos[:, 1], formation_pos[:, 2],
               color=color, s=50, alpha=0.3, marker='x',
               label=f'Formazione {i + 1}')

# Setup animazione
fps = sequencer.get_fps()
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
        pos = sequencer.get_position(d.drone_id, t)
        points[idx].set_data([pos[0]], [pos[1]])
        points[idx].set_3d_properties([pos[2]])

    # Mostra progresso
    ax.set_title(f"Drone Show - {t:.1f}s / {total_duration:.1f}s", fontsize=14)
    return points


ani = animation.FuncAnimation(fig, animate, frames=num_frames,
                              init_func=init, blit=False, interval=1000 / fps)

plt.legend(loc='upper right')
plt.tight_layout()
plt.show()