# export_file/config_exporter_show.py
import yaml
import os


def export_show_config_to_yaml(shape_dict, output_path="config/show_config.yaml"):
    """
    Esporta la configurazione dello show in formato YAML.

    Converte da shape_dict (formato GUI) a sequences (formato show).

    Args:
        shape_dict: dizionario con formato {"step_0": {...}, "step_1": {...}}
        output_path: percorso del file YAML di output

    Returns:
        str: percorso del file creato
    """

    sequences = []

    # Converti ogni step in una sequence
    for step_key in sorted(shape_dict.keys()):
        step_data = shape_dict[step_key]

        # Estrai il tipo di shape
        shape_type = step_data.get('shape', 'grid')

        # Crea la struttura params in base al tipo di shape
        params = {}

        if shape_type == 'sphere':
            params = {
                'radius': step_data.get('radius', 5.0),
                'center': step_data.get('center', [0.0, 0.0, 5.0])
            }

        elif shape_type == 'grid':
            params = {
                'spacing': step_data.get('spacing', 3.0),
                'center': step_data.get('center', [0.0, 0.0, 5.0]),
                'normal': step_data.get('normal', 'xy')
            }

        elif shape_type == 'circle':
            params = {
                'radius': step_data.get('radius', 5.0),
                'center': step_data.get('center', [0.0, 0.0, 5.0]),
                'normal': step_data.get('normal', [0, 0, 1])
            }

        elif shape_type == 'line':
            params = {
                'length': step_data.get('length', 10.0),
                'axis': step_data.get('axis', 'x')
            }

        elif shape_type == 'heart':
            params = {
                'size': step_data.get('size', 5.0),
                'center': step_data.get('center', [0.0, 0.0, 5.0]),
                'plane': step_data.get('plane', 'xy')
            }

        elif shape_type == 'wave':
            params = {
                'wavelength': step_data.get('wavelength', 5.0),
                'amplitude': step_data.get('amplitude', 2.0),
                'length': step_data.get('length', 20.0),
                'center': step_data.get('center', [0.0, 0.0, 5.0])
            }

        elif shape_type == 'spiral':
            params = {
                'radius_start': step_data.get('radius_start', 2.0),
                'radius_end': step_data.get('radius_end', 8.0),
                'height': step_data.get('height', 10.0),
                'turns': step_data.get('turns', 3.0),
                'center': step_data.get('center', [0.0, 0.0, 5.0])
            }

        elif shape_type == 'number':
            params = {
                'digit': step_data.get('digit', 0),
                'size': step_data.get('size', 5.0),
                'center': step_data.get('center', [0.0, 0.0, 5.0]),
                'plane': step_data.get('plane', 'xy')
            }

        # Crea la sequence entry
        sequence_entry = {
            'formation': {
                'type': shape_type,
                'params': params
            },
            'transition_duration': step_data.get('transition_duration', 5.0),
            'hold_duration': step_data.get('hold_duration', 2.0)
        }

        sequences.append(sequence_entry)

    # Crea la struttura finale
    yaml_data = {'sequences': sequences}

    # Crea la cartella config se non esiste
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Scrivi il file YAML
    with open(output_path, 'w') as f:
        yaml.dump(yaml_data, f, default_flow_style=None, sort_keys=False)

    print(f"✅ Configurazione show salvata in: {output_path}")
    return output_path