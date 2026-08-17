import os
import time
import queue
import asyncio
import threading
from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor

from .plate import BurstAnalyzer, PlateResult
from api.client import AccessValidationClient

class AIModule(threading.Thread):
    """
    Módulo de Inteligencia Artificial para procesamiento asíncrono y no bloqueante
    de ráfagas de fotos para detección y reconocimiento de placas.
    """
    def __init__(self, event_bus=None):
        super().__init__(daemon=True)
        self.running = False
        self.event_bus = event_bus
        self.watch_dir = os.getenv("CAMERA_SAVE_PATH", "./storage/camera")
        self.min_confidence = float(os.getenv("PLATE_MIN_CONFIDENCE", "0.25"))
        
        self._task_queue = queue.Queue()
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="AIWorker")
        self.burst_analyzer: Optional[BurstAnalyzer] = None
        self.api_client = AccessValidationClient()

        # Suscribirse al evento BURST_CAPTURED si hay EventBus
        if self.event_bus:
            self.event_bus.subscribe("BURST_CAPTURED", self.on_burst_captured)

    def on_burst_captured(self, image_paths: List[str]):
        """Callback invocado por el EventBus al capturar una ráfaga de imágenes."""
        if image_paths:
            print(f"[AI] Nueva ráfaga recibida en la cola ({len(image_paths)} fotos).")
            self._task_queue.put(image_paths)

    def process_burst_async(self, image_paths: List[str]):
        """Procesa una ráfaga de imágenes de forma asíncrona usando el pool ejecutor."""
        try:
            if self.burst_analyzer is None:
                # Cargar los modelos YOLO la primera vez que se utilicen para no bloquear el inicio rápido
                print("[AI] Inicializando analizador de placas y OCR...")
                self.burst_analyzer = BurstAnalyzer()

            result: Optional[PlateResult] = self.burst_analyzer.analyze_burst(image_paths)
            if not result:
                print("[AI] Ninguna placa válida fue identificada en la ráfaga.")
                return

            print(f"[AI] Resultado final de la ráfaga: Placa='{result.cleaned_plate}' (Método={result.detection_method}, Score={result.composite_score:.4f})")
            if result.debug_annotated_path:
                print(f"[AI] Evidencia visual de depuración: {result.debug_annotated_path}")

            if result.composite_score < self.min_confidence:
                print(f"[AI] Confianza ({result.composite_score:.2f}) inferior al umbral mínimo ({self.min_confidence}). Acceso omitido.")
                return

            # Consultar asíncronamente a la API de validación
            print(f"[AI] Validando placa '{result.cleaned_plate}' con el servidor...")
            success, response = asyncio.run(self.api_client.validate_plate(result.cleaned_plate))

            if success and response:
                print(f"[AI] ★ ACCESO VALIDADO POR LA API: {response.message}")
                if self.event_bus:
                    print("[AI] Emitiendo evento ACCESS_GRANTED al bus de eventos...")
                    self.event_bus.publish("ACCESS_GRANTED", source="AI_PLATE", plate=result.cleaned_plate)
            else:
                print(f"[AI] Acceso Denegado por el servidor para la placa: '{result.cleaned_plate}'")

        except Exception as e:
            print(f"[AI] Error durante el procesamiento asíncrono de la ráfaga: {e}")

    def run(self):
        print(f"[AI] Iniciando el hilo de Inteligencia Artificial (Directorio a vigilar: '{self.watch_dir}')...")
        self.running = True

        while self.running:
            try:
                # Espera no bloqueante en la cola de tareas
                image_paths = self._task_queue.get(timeout=1.0)
                if image_paths and self.running:
                    # Enviar el análisis al ejecutor en segundo plano
                    self._executor.submit(self.process_burst_async, image_paths)
                self._task_queue.task_done()
            except queue.Empty:
                pass
            except Exception as e:
                print(f"[AI] Error en el bucle principal de IA: {e}")

    def stop(self):
        print("[AI] Deteniendo el módulo de IA.")
        self.running = False
        self._executor.shutdown(wait=False)
