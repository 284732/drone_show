# config_exporter.py
import yaml
import os

'''def export_drones_config_to_yaml(drone_config, output_path="config/drone_config.yaml"):
    """
    Esporta la configurazione dei droni in formato YAML.

    Args:
        drone_config: dizionario con formato {"drone 1": {...}, "drone 2": {...}}
        output_path: percorso del file YAML di output

    Returns:
        str: percorso del file creato
    """
    # Converti il dizionario in una lista nel formato corretto
    drones_list = []

    for key, value in drone_config.items():
        # Estrai l'ID del drone dalla chiave "drone 1", "drone 2", etc.
        drone_id = int(key.split()[1]) - 1  # -1 per iniziare da 0

        drone_entry = {
            'drone_id': drone_id,
            'initial_position': value['initial_position'],
            'max_velocity': value['max_velocity'],
            'max_acceleration': value['max_acceleration']
        }
        drones_list.append(drone_entry)

    # Crea la struttura finale
    yaml_data = {'drones': drones_list}

    # Crea la cartella config se non esiste
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Scrivi il file YAML
    with open(output_path, 'w') as f:
        yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False)

    print(f"✅ Configurazione droni salvata in: {output_path}")
    return output_path'''
import yaml
import os
from pathlib import Path

def export_drones_config_to_yaml(drone_config, output_path=None):
    """
    Esporta la configurazione dei droni nel file config/drone_config.yaml
    nella root del progetto, indipendentemente da dove viene eseguito lo script.
    """

    # Trova la root del progetto risalendo dal file corrente
    project_root = Path(__file__).resolve().parents[2]  # GUI/export_file -> GUI -> DRONE_SHOW
    config_dir = project_root / "config"

    # Se non è specificato un percorso esterno, usa quello nella root del progetto
    if output_path is None:
        output_path = config_dir / "drone_config.yaml"
    else:
        output_path = Path(output_path)

    # Converti il dizionario nel formato finale
    drones_list = []
    for key, value in drone_config.items():
        drone_id = int(key.split()[1]) - 1
        drones_list.append({
            'drone_id': drone_id,
            'initial_position': value['initial_position'],
            'max_velocity': value['max_velocity'],
            'max_acceleration': value['max_acceleration']
        })

    yaml_data = {'drones': drones_list}

    # Assicurati che la cartella config esista
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Scrivi il file
    with open(output_path, 'w') as f:
        yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False)

    print(f"Configurazione droni salvata in: {output_path}")
    return str(output_path)
