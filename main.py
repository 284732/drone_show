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
"""
QUESTO FUNZIONA FINO A QUANDO NON HO USATO LA GUI 2 OFFLINE


import yaml
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from models.drone import Drone
from models.show_sequencer import ShowSequencer
import subprocess
import sys
import os


# Importa direttamente la GUI - questo la esegue automaticamente
from GUI_DronesShow.Process import mainRoot

###############
# CARICA DRONI DAL FILE GENERATO DALLA GUI
###############
config_path = "config/drone_config.yaml"  # ← Path corretto

# Verifica che il file esista
if not os.path.exists(config_path):
    raise FileNotFoundError(f"❌ File {config_path} non trovato! La GUI dovrebbe averlo creato.")

with open(config_path, "r") as f:  # ← Path corretto
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


"""
'''import yaml
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from models.drone import Drone
from models.show_sequencer import ShowSequencer
import os
import sys

###############
# STEP 1: ESEGUI LA GUI E GENERA I FILE YAML
###############
print("🚁 Avvio configurazione Drone Show...")
print("=" * 50)

# Importa e esegui la GUI
# IMPORTANTE: L'import esegue automaticamente Process.py che apre le finestre GUI
try:
    from GUI.process import mainRoot

    # Chiudi la finestra root principale dopo che la GUI ha finito
    if mainRoot:
        mainRoot.destroy()
except Exception as e:
    print(f"⚠️  Errore durante l'esecuzione della GUI: {e}")
    sys.exit(1)

# A questo punto la GUI è stata completata e i file YAML sono stati creati
print("\n" + "=" * 50)
print("✅ Configurazione GUI completata!")
print("=" * 50)

###############
# STEP 2: VERIFICA CHE I FILE YAML ESISTANO
###############
drone_config_path = "config/drone_config.yaml"
show_config_path = "config/show_config.yaml"

if not os.path.exists(drone_config_path):
    raise FileNotFoundError(f"❌ File {drone_config_path} non trovato! La GUI dovrebbe averlo creato.")

if not os.path.exists(show_config_path):
    raise FileNotFoundError(f"❌ File {show_config_path} non trovato! La GUI dovrebbe averlo creato.")

print(f"\n📄 File di configurazione trovati:")
print(f"   - {drone_config_path}")
print(f"   - {show_config_path}")

###############
# STEP 3: CARICA DRONI DAL FILE YAML
###############
print("\n🔄 Caricamento droni...")
with open(drone_config_path, "r") as f:
    drone_data = yaml.safe_load(f)

drones = []
for drone_info in drone_data["drones"]:
    drone = Drone(
        drone_id=drone_info["drone_id"],
        initial_position=drone_info["initial_position"],
        max_velocity=drone_info["max_velocity"],
        max_acceleration=drone_info["max_acceleration"]
    )
    drones.append(drone)

print(f"✅ {len(drones)} droni caricati con successo!")

###############
# STEP 4: COSTRUISCI LO SHOW
###############
print("\n🎭 Costruzione sequenza show...")
sequencer = ShowSequencer(show_config_path, drones)
total_duration = sequencer.build_show()

print(f"✅ Show costruito! Durata totale: {total_duration:.2f} secondi")

###############
# STEP 5: PREPARAZIONE ANIMAZIONE
###############
print("\n🎬 Preparazione animazione...")

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

print(f"   FPS: {fps}")
print(f"   Frame totali: {num_frames}")
print(f"   Formazioni: {len(all_formations)}")


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


###############
# STEP 6: AVVIO ANIMAZIONE
###############
print("\n▶️  Avvio simulazione...\n")
print("=" * 50)

ani = animation.FuncAnimation(fig, animate, frames=num_frames,
                              init_func=init, blit=False, interval=1000 / fps)

plt.legend(loc='upper right')
plt.tight_layout()
plt.show()

print("\n✅ Simulazione completata!")'''

'''
QUESTO VA MA DEBUG UN PO INCAPIBILE

import yaml
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from models.drone import Drone
from models.show_sequencer import ShowSequencer
import os
import sys

###############
# STEP 1: ESEGUI LA GUI E GENERA I FILE YAML
###############
print("🚁 Avvio configurazione Drone Show...")
print("=" * 50)

# Importa e esegui la GUI
# IMPORTANTE: L'import esegue automaticamente Process.py che apre le finestre GUI
try:
    from GUI.process import mainRoot

    # Chiudi la finestra root principale dopo che la GUI ha finito
    if mainRoot:
        mainRoot.destroy()
except Exception as e:
    print(f"⚠️  Errore durante l'esecuzione della GUI: {e}")
    sys.exit(1)

# A questo punto la GUI è stata completata e i file YAML sono stati creati
print("\n" + "=" * 50)
print("✅ Configurazione GUI completata!")
print("=" * 50)

###############
# STEP 2: VERIFICA CHE I FILE YAML ESISTANO
###############
drone_config_path = "config/drone_config.yaml"
show_config_path = "config/show_config.yaml"

if not os.path.exists(drone_config_path):
    raise FileNotFoundError(f"❌ File {drone_config_path} non trovato! La GUI dovrebbe averlo creato.")

if not os.path.exists(show_config_path):
    raise FileNotFoundError(f"❌ File {show_config_path} non trovato! La GUI dovrebbe averlo creato.")

print(f"\n📄 File di configurazione trovati:")
print(f"   - {drone_config_path}")
print(f"   - {show_config_path}")

###############
# STEP 3: CARICA DRONI DAL FILE YAML
###############
print("\n🔄 Caricamento droni...")
with open(drone_config_path, "r") as f:
    drone_data = yaml.safe_load(f)

drones = []
for drone_info in drone_data["drones"]:
    drone = Drone(
        drone_id=drone_info["drone_id"],
        initial_position=drone_info["initial_position"],
        max_velocity=drone_info["max_velocity"],
        max_acceleration=drone_info["max_acceleration"]
    )
    drones.append(drone)

print(f"✅ {len(drones)} droni caricati con successo!")





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
plt.show()'''

import yaml
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from models.drone import Drone
from models.show_sequencer import ShowSequencer
import os
import sys
from export_file.trajectory_exporter import export_trajectories_full



def print_header(title):
    """Stampa un'intestazione formattata"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_step(step_num, description):
    """Stampa un passo del processo"""
    print(f"\n[STEP {step_num}] {description}")
    print("-" * 60)


def print_success(message):
    """Stampa un messaggio di successo"""
    print(f"✅ {message}")


def print_info(message, indent=1):
    """Stampa un messaggio informativo"""
    prefix = "   " * indent
    print(f"{prefix}• {message}")


def print_error(message):
    """Stampa un messaggio di errore"""
    print(f"❌ ERROR: {message}")


###############################################################################
# MAIN PROGRAM
###############################################################################

print_header("🚁 DRONE SHOW - CONFIGURAZIONE E SIMULAZIONE")

###############
# STEP 1: GUI CONFIGURATION
###############
print_step(1, "Avvio interfaccia grafica di configurazione")
print_info("Aprendo finestre GUI in sequenza...")

try:
    from GUI.process import mainRoot

    if mainRoot:
        mainRoot.destroy()
    print_success("GUI completata con successo")

except Exception as e:
    print_error(f"Errore durante l'esecuzione della GUI: {e}")
    print_info("Chiusura del programma...", indent=2)
    sys.exit(1)

###############
# STEP 2: FILE VALIDATION
###############
print_step(2, "Verifica file di configurazione")

drone_config_path = "config/drone_config.yaml"
show_config_path = "config/show_config.yaml"

print_info(f"Cerco: {drone_config_path}")
if not os.path.exists(drone_config_path):
    print_error(f"File {drone_config_path} non trovato!")
    print_info("La GUI dovrebbe aver creato questo file", indent=2)
    sys.exit(1)
print_success(f"Trovato: {drone_config_path}")

print_info(f"Cerco: {show_config_path}")
if not os.path.exists(show_config_path):
    print_error(f"File {show_config_path} non trovato!")
    print_info("La GUI dovrebbe aver creato questo file", indent=2)
    sys.exit(1)
print_success(f"Trovato: {show_config_path}")

###############
# STEP 3: LOAD DRONES
###############
print_step(3, "Caricamento configurazione droni")

print_info(f"Lettura file: {drone_config_path}")
try:
    with open(drone_config_path, "r") as f:
        drone_data = yaml.safe_load(f)
    print_success("File YAML caricato correttamente")
except Exception as e:
    print_error(f"Errore nella lettura del file: {e}")
    sys.exit(1)

print_info("Inizializzazione droni...")
drones = []
for i, drone_info in enumerate(drone_data["drones"]):
    drone = Drone(
        drone_id=drone_info["drone_id"],
        initial_position=drone_info["initial_position"],
        max_velocity=drone_info["max_velocity"],
        max_acceleration=drone_info["max_acceleration"]
    )
    drones.append(drone)
    print_info(f"Drone {i}: ID={drone_info['drone_id']}, "
               f"Pos={drone_info['initial_position']}, "
               f"V_max={drone_info['max_velocity']} m/s", indent=2)

print_success(f"Caricati {len(drones)} droni con successo")

###############
# STEP 4: BUILD SHOW SEQUENCE
###############
print_step(4, "Costruzione sequenza show")

print_info(f"Lettura file: {show_config_path}")
try:
    sequencer = ShowSequencer(show_config_path, drones)
    print_success("Show Sequencer inizializzato")
except Exception as e:
    print_error(f"Errore nell'inizializzazione del sequencer: {e}")
    sys.exit(1)

print_info("Generazione traiettorie...")
try:
    total_duration = sequencer.build_show()
    print_success(f"Show costruito con successo")
    print_info(f"Durata totale: {total_duration:.2f} secondi", indent=2)
except Exception as e:
    print_error(f"Errore nella costruzione dello show: {e}")
    sys.exit(1)




###############
# STEP 5: EXPORT TRAJECTORIES TO CSV
###############
print_step(5, "Esportazione traiettorie in CSV")

output_dir = "trajectories_csv"
os.makedirs(output_dir, exist_ok=True)
print_info(f"Cartella output: {output_dir}")

try:
    # FPS dell'animazione (dal YAML)
    fps_anim = sequencer.get_fps()

    # 👉 FPS SOLO PER L'EXPORT: METTI QUI QUELLO CHE VUOI
    fps_export = 60   # oppure 100, 120, quello che ti serve

    export_info = export_trajectories_full(
        sequencer=sequencer,
        drones=drones,
        total_duration=total_duration,
        output_dir=output_dir,

        # ⚡ export ad alta precisione
        fps=fps_export,

        # 👉 Include l'ultimo campione t = total_duration
        include_endpoint=True,

        include_summary=True,   # se vuoi avere il file totale
        delimiter=",",
    )

    n_files = len(export_info.get('individual_files', {}))
    #print_success(f"Esportazione completata: {n_files} file individuali")
    if 'summary_file' in export_info:
        print_info(f"File riassuntivo: {export_info['summary_file']}", indent=2)

except Exception as e:
    print_error(f"Errore durante l'esportazione CSV: {e}")
    sys.exit(1)


###############
# STEP 6: SETUP ANIMATION
###############
print_step(6, "Preparazione visualizzazione 3D")

print_info("Configurazione figura matplotlib...")
fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(111, projection='3d')
ax.set_xlabel('X [m]')
ax.set_ylabel('Y [m]')
ax.set_zlabel('Z [m]')

# Calcola limiti spaziali
print_info("Calcolo limiti spaziali dalle formazioni...")
all_formations = sequencer.get_all_formations()
all_positions = np.vstack(all_formations)
margin = 2.0
xyz_min = all_positions.min(axis=0) - margin
xyz_max = all_positions.max(axis=0) + margin

print_info(f"Limiti X: [{xyz_min[0]:.1f}, {xyz_max[0]:.1f}] m", indent=2)
print_info(f"Limiti Y: [{xyz_min[1]:.1f}, {xyz_max[1]:.1f}] m", indent=2)
print_info(f"Limiti Z: [{xyz_min[2]:.1f}, {xyz_max[2]:.1f}] m", indent=2)

ax.set_xlim(xyz_min[0], xyz_max[0])
ax.set_ylim(xyz_min[1], xyz_max[1])
ax.set_zlim(xyz_min[2], xyz_max[2])

# Setup droni
print_info("Creazione punti droni...")
points = [ax.plot([], [], [], 'o', markersize=10)[0] for d in drones]
print_success(f"Creati {len(points)} marker per i droni")

# Mostra formazioni target
print_info("Rendering formazioni target...")
colors = ['red', 'green', 'blue', 'orange', 'purple', 'cyan', 'magenta', 'yellow']
for i, formation_pos in enumerate(all_formations):
    color = colors[i % len(colors)]
    ax.scatter(formation_pos[:, 0], formation_pos[:, 1], formation_pos[:, 2],
               color=color, s=50, alpha=0.3, marker='x',
               label=f'Formazione {i + 1}')
    print_info(f"Formazione {i + 1}: {len(formation_pos)} posizioni target ({color})", indent=2)

# Parametri animazione
fps = sequencer.get_fps()
num_frames = int(total_duration * fps)
times = np.linspace(0, total_duration, num_frames)

print_info(f"FPS: {fps}", indent=2)
print_info(f"Frame totali: {num_frames}", indent=2)
print_info(f"Formazioni: {len(all_formations)}", indent=2)

print_success("Setup visualizzazione completato")


# Funzioni animazione
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

    ax.set_title(f"Drone Show - {t:.1f}s / {total_duration:.1f}s", fontsize=14)
    return points


###############
# STEP 7: START SIMULATION
###############
print_step(7, "Avvio simulazione animata")

print_info("Creazione animazione...")
ani = animation.FuncAnimation(fig, animate, frames=num_frames,
                              init_func=init, blit=False, interval=1000 / fps)

plt.legend(loc='upper right')
plt.tight_layout()

print_success("Animazione pronta!")
print_info("Aprendo finestra matplotlib...", indent=2)
print_info("(Chiudi la finestra per terminare il programma)", indent=2)

print_header("▶️  SIMULAZIONE IN CORSO")

plt.show()

print_header("✅ SIMULAZIONE COMPLETATA")
print_info("Programma terminato con successo")