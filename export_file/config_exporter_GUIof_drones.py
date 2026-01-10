# export_file/config_exporter_GUIof_drones.py
import yaml
import os


def export_drones_config_to_yaml(drone_config, output_path="config/drone_config.yaml"):
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

    # Crea la cartella config se non esiste (path assoluto dalla root del progetto)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Scrivi il file YAML con liste compatte
    with open(output_path, 'w') as f:
        yaml.dump(yaml_data, f, default_flow_style=None, sort_keys=False)

    print(f"✅ Configurazione droni salvata in: {output_path}")
    return output_path