# core/show_sequencer.py
import yaml
import numpy as np
from typing import List, Dict
from models.drone import Drone
from core.formation_generator import circle_formation_normal, sphere_formation, spiral_formation, star_formation, line_formation, heart_formation, number_formation, helix_formation, pyramid_formation, cube_formation, grid_formation, wave_formation
from core.trajectory_generator import generate_trajectories
from core.assignment_solver import assign_drones_to_targets
from core.trajectory_validator import check_constraints_and_collisions
from core.trajectory_postprocessor import (
    time_scale_trajectories,
    resolve_collisions_with_start_delays_me
)


class ShowSequencer:
    def __init__(self, yaml_path: str, drones: List[Drone]):
        self.drones = drones
        self.sequences = []
        self.trajectories = []
        self.durations = []
        self.cumulative_times = [0.0]

        with open(yaml_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Mappa tipo formazione -> funzione generatrice
        self.formation_generators = {
            'circle': self._generate_circle,
            'line': self._generate_line,
            'sphere': self._generate_sphere,
            'helix': self._generate_helix,
            'cube': self._generate_cube,
            'grid': self._generate_grid,
            'heart': self._generate_heart,
            'star': self._generate_star,
            'wave': self._generate_wave,
            'pyramid': self._generate_pyramid,
            'spiral': self._generate_spiral,
            'number': self._generate_number,
        }

    def _generate_circle(self, params: Dict) -> np.ndarray:
        """Genera formazione a cerchio"""
        return circle_formation_normal(
            num_points=len(self.drones),
            radius=params['radius'],
            center=tuple(params['center']),
            normal=tuple(params['normal'])
        )

    def _generate_line(self, params):
        return line_formation(
            num_points=len(self.drones),
            length=params['length'],
            axis=params['axis']
        )

    def _generate_sphere(self, params):
        return sphere_formation(
            num_points=len(self.drones),
            radius=params['radius'],
            center=tuple(params['center'])
        )

    def _generate_helix(self, params):
        return helix_formation(
            num_points=len(self.drones),
            radius=params['radius'],
            height=params['height'],
            turns=params['turns'],
            center=tuple(params['center'])
        )

    def _generate_cube(self, params):
        return cube_formation(
            num_points=len(self.drones),
            side_length=params['side_length'],
            center=tuple(params['center'])
        )

    def _generate_grid(self, params):
        return grid_formation(
            num_points=len(self.drones),
            spacing=params['spacing'],
            center=tuple(params['center']),
            plane=params['plane']
        )

    def _generate_heart(self, params):
        return heart_formation(
            num_points=len(self.drones),
            size=params['size'],
            center=tuple(params['center']),
            plane=params['plane']
        )

    def _generate_star(self, params):
        return star_formation(
            num_points=len(self.drones),
            outer_radius=params['outer_radius'],
            inner_radius=params['inner_radius'],
            num_spikes=params['num_spikes'],
            center=tuple(params['center']),
            plane=params['plane']
        )

    def _generate_wave(self, params):
        return wave_formation(
            num_points=len(self.drones),
            wavelength=params['wavelength'],
            amplitude=params['amplitude'],
            length=params['length'],
            center=tuple(params['center']),
        )

    def _generate_pyramid(self, params):
        return pyramid_formation(
            num_points=len(self.drones),
            base_size=params['base_size'],
            height=params['height'],
            center=tuple(params['center'])
        )

    def _generate_spiral(self, params):
        return spiral_formation(
            num_points=len(self.drones),
            radius_start=params['radius_start'],
            radius_end=params['radius_end'],
            height=params['height'],
            turns=params['turns'],
            center=tuple(params['center'])
        )

    def _generate_number(self, params):
        return number_formation(
            num_points=len(self.drones),
            digit=params['number'],
            size=params['size'],
            center=tuple(params['center']),
            plane=params['plane']
        )


    # Aggiungi qui altri metodi _generate_xxx per altre formazioni

    def build_show(self):
        """Costruisce l'intera sequenza dello show dalla configurazione YAML"""
        current_positions = {d.drone_id: d.initial_position for d in self.drones}

        for seq_idx, sequence in enumerate(self.config['sequences']):
            print(f"\n=== Sequenza {seq_idx + 1}/{len(self.config['sequences'])} ===")

            # 1. Genera la formazione target
            formation_type = sequence['formation']['type']
            formation_params = sequence['formation']['params']

            if formation_type not in self.formation_generators:
                raise ValueError(f"Tipo formazione '{formation_type}' non supportato")

            formation = self.formation_generators[formation_type](formation_params)
            print(f"  Formazione: {formation_type}")

            # 2. Crea droni temporanei con posizioni correnti
            temp_drones = [
                Drone(d.drone_id, current_positions[d.drone_id],
                      d.max_velocity, d.max_acceleration)
                for d in self.drones
            ]

            # 3. Assegna droni ai target
            assignment = assign_drones_to_targets(temp_drones, formation)

            # 4. Genera e scala traiettorie per la transizione
            transition_duration = sequence['transition_duration']
            trajectories, actual_duration = time_scale_trajectories(
                temp_drones, assignment, transition_duration
            )
            print(f"  Transition duration: {actual_duration:.2f}s")

            # 5. Risolvi collisioni
            trajectories, _ = resolve_collisions_with_start_delays_me(
                trajectories, self.drones
            )

            # 6. Valida traiettorie
            validation = check_constraints_and_collisions(trajectories, self.drones)
            print(f"  Validazione: dinamica={validation['dynamic_ok']}, "
                  f"collisioni={validation['swarm_ok']}")

            if not (validation['dynamic_ok'] and validation['swarm_ok']):
                print(f"  ⚠️ ATTENZIONE: Sequenza {seq_idx + 1} non valida!")

            # 7. Salva hold duration
            hold_duration = sequence.get('hold_duration', 0.0)
            print(f"  Hold duration: {hold_duration:.2f}s")

            # 8. Memorizza tutte le info della sequenza
            self.sequences.append({
                'formation': formation,
                'assignment': assignment,
                'trajectories': trajectories,
                'transition_duration': actual_duration,
                'hold_duration': hold_duration,
                'type': formation_type
            })

            total_seq_duration = actual_duration + hold_duration
            self.durations.append(total_seq_duration)
            self.cumulative_times.append(
                self.cumulative_times[-1] + total_seq_duration
            )

            # 9. Aggiorna posizioni correnti per la prossima sequenza
            for d in self.drones:
                current_positions[d.drone_id] = trajectories[d.drone_id].position(
                    actual_duration
                )

        print(f"\n=== Show completo ===")
        print(f"Durata totale: {self.get_total_duration():.2f}s")

        return self.get_total_duration()

    def get_total_duration(self) -> float:
        """Ritorna la durata totale dello show"""
        return self.cumulative_times[-1]

    def get_position(self, drone_id: int, t: float) -> np.ndarray:
        """Ritorna la posizione di un drone al tempo t globale"""
        # Trova in quale sequenza ci troviamo
        for i, seq in enumerate(self.sequences):
            t_start = self.cumulative_times[i]
            t_end = self.cumulative_times[i + 1]

            if t_start <= t < t_end:
                local_t = t - t_start
                transition_dur = seq['transition_duration']

                # Fase di transizione: drone in movimento
                if local_t <= transition_dur:
                    return seq['trajectories'][drone_id].position(local_t)
                # Fase di hold: drone fermo nella formazione
                else:
                    return seq['trajectories'][drone_id].position(transition_dur)

        # Se siamo oltre la fine, ritorna ultima posizione
        last_seq = self.sequences[-1]
        return last_seq['trajectories'][drone_id].position(
            last_seq['transition_duration']
        )

    def get_all_formations(self) -> List[np.ndarray]:
        """Ritorna tutte le formazioni target per visualizzazione"""
        return [seq['formation'].target_positions for seq in self.sequences]

    def get_fps(self) -> int:
        """Ritorna gli FPS configurati"""
        return self.config.get('fps', 20)