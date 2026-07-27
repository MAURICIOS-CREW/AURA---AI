import time
import threading

class AIModule(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.running = False
        
    def run(self):
        print("[AI] Iniciando el hilo de Inteligencia Artificial (Placeholder)...")
        self.running = True
        
        while self.running:
            # Placeholder: Aquí iría la lógica de la IA.
            # time.sleep en su propio hilo no bloquea nada externo.
            time.sleep(10.0)
            if self.running:
                print("[AI] El hilo de la IA sigue trabajando en su propio hilo del SO...")
            
    def stop(self):
        self.running = False
        print("[AI] Deteniendo el módulo de IA.")
