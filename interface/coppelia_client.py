
# clients/coppelia_client.py

import time
from typing import Sequence
import numpy as np
from coppeliasim_zmqremoteapi_client import RemoteAPIClient


class CoppeliaClient:
    """
    Client Python per interagire con CoppeliaSim tramite ZMQ Remote API (protocol v2).
    - Porta di default ZMQ: 23000 (NON 19997).
    - Import corretto del client: coppeliasim_zmqremoteapi_client.
    """

    def __init__(self, ip: str = '127.0.0.1', port: int = 23000):
        """
        Inizializza il client e connette CoppeliaSim.
        :param ip: indirizzo del server ZMQ (di solito '127.0.0.1')
        :param port: porta del server ZMQ (default 23000)
        """
        self.client = RemoteAPIClient(host=ip, port=port)
        # API moderna: require('sim') carica/ottiene l'oggetto remoto 'sim'
        self.sim = self.client.require('sim')
        self.sim_running = False

    # -------------------------------------------------------------------------
    # Controllo simulazione
    # -------------------------------------------------------------------------

    def start_simulation(self, stepped: bool = False):
        """
        Avvia la simulazione.
        :param stepped: se True abilita la modalità stepping (sim.step()).
        """
        if not self.sim_running:
            if stepped:
                self.sim.setStepping(True)
            self.sim.startSimulation()
            self.sim_running = True
            print("Simulazione avviata.")

    def stop_simulation(self):
        """
        Ferma la simulazione.
        """
        if self.sim_running:
            self.sim.stopSimulation()
            self.sim_running = False
            print("Simulazione fermata.")

    def step(self, dt: float = 0.01):
        """
        Esegue un passo della simulazione se la modalità stepping è attiva
        (cioè se prima hai chiamato start_simulation(stepped=True)).
        In ogni caso attende dt secondi (utile per esempi in tempo reale).
        """
        try:
            # In modalità stepped questa chiamata fa avanzare la simulazione
            self.sim.step()
        except Exception:
            # Se non è in stepping mode, step() non è necessario
            pass
        time.sleep(float(dt))

    # -------------------------------------------------------------------------
    # Utility sugli oggetti
    # -------------------------------------------------------------------------

    def get_handle(self, object_name: str) -> int:
        """
        Restituisce l'handle di un oggetto nella scena.
        Prova prima l'API moderna (getObject), poi fallback a getObjectHandle.
        :param object_name: path o nome dell'oggetto, es. '/Quadcopter' o '/Floor'
        """
        try:
            return int(self.sim.getObject(object_name))
        except Exception:
            return int(self.sim.getObjectHandle(object_name))

    def set_drone_position(self, handle: int, position: Sequence[float]):
        """
        Imposta la posizione di un oggetto (es. drone) in riferimento alla base (-1).
        :param handle: handle dell'oggetto
        :param position: iterabile [x, y, z]
        """
        pos = np.asarray(position, dtype=float)
        if pos.shape != (3,):
            raise ValueError("position deve essere un vettore 3D [x, y, z].")
        self.sim.setObjectPosition(handle, -1, pos.tolist())

    def get_drone_position(self, handle: int) -> np.ndarray:
        """
        Legge la posizione corrente di un oggetto (es. drone) in coordinate di base.
        :param handle: handle dell'oggetto
        :return: np.ndarray shape (3,) [x, y, z]
        """
        return np.asarray(self.sim.getObjectPosition(handle, -1), dtype=float)
