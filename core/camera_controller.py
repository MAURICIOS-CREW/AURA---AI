import os
import time
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

class CameraController:
    """
    Controlador para gestionar la cámara de forma no bloqueante.
    Toma ráfagas de fotos y las guarda en el disco.
    """
    def __init__(self, event_bus=None):
        # Configuraciones con valores por defecto
        self.camera_index = int(os.getenv("CAMERA_INDEX", "0"))
        self.burst_count = int(os.getenv("CAMERA_BURST_COUNT", "3"))
        self.burst_delay = float(os.getenv("CAMERA_BURST_DELAY", "1.0"))
        self.save_path = os.getenv("CAMERA_SAVE_PATH", "./storage/camera")
        self.event_bus = event_bus
        
        # Crear directorio si no existe
        os.makedirs(self.save_path, exist_ok=True)
        
        # Usamos un ThreadPoolExecutor con 1 hilo para no sobrecargar si hay múltiples disparos rápidos
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.is_capturing = False

    def take_burst(self):
        """
        Inicia la captura de ráfaga en un hilo separado de forma no bloqueante.
        Si ya hay una captura en curso, se ignora para no saturar.
        """
        if self.is_capturing:
            print("[Camara] Ya hay una captura en progreso. Ignorando evento.")
            return
            
        print(f"[Camara] Iniciando ráfaga de {self.burst_count} fotos de forma asíncrona...")
        self.executor.submit(self._capture_task)

    def _find_working_camera_index(self, default_index):
        import cv2, glob
        # 1. Probar el índice configurado
        if sys.platform.startswith('linux'):
            cap = cv2.VideoCapture(default_index, cv2.CAP_V4L2)
        elif sys.platform == 'win32':
            cap = cv2.VideoCapture(default_index, cv2.CAP_DSHOW)
        else:
            cap = cv2.VideoCapture(default_index)

        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret and frame is not None:
                return default_index

        print(f"[Camara] [AVISO] El índice {default_index} no devolvió imagen. Buscando cámara disponible...")
        
        # 2. En Linux, intentar resolver symlinks estables en /dev/v4l/by-id/
        if sys.platform.startswith('linux'):
            by_id_files = sorted(glob.glob("/dev/v4l/by-id/*video-index0"))
            for by_id in by_id_files:
                try:
                    target = os.path.realpath(by_id)
                    idx = int(target.replace("/dev/video", ""))
                    cap = cv2.VideoCapture(idx, cv2.CAP_V4L2)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        cap.release()
                        if ret and frame is not None:
                            print(f"[Camara] Cámara auto-detectada mediante persistent link en índice {idx}")
                            return idx
                except Exception:
                    pass

            # 3. Escaneo dinámico de todos los /dev/video*
            dev_files = glob.glob("/dev/video*")
            indices = sorted([int(d.replace("/dev/video", "")) for d in dev_files if d.replace("/dev/video", "").isdigit()])
            for idx in indices:
                cap = cv2.VideoCapture(idx, cv2.CAP_V4L2)
                if cap.isOpened():
                    ret, frame = cap.read()
                    cap.release()
                    if ret and frame is not None:
                        print(f"[Camara] Cámara auto-detectada dinámicamente en índice {idx}")
                        return idx

        return default_index

    def _get_video_capture(self):
        import cv2
        
        active_index = self._find_working_camera_index(self.camera_index)
        
        # Forzar backends para mejor compatibilidad dependiendo del SO
        if sys.platform.startswith('linux'):
            cap = cv2.VideoCapture(active_index, cv2.CAP_V4L2)
        elif sys.platform == 'win32':
            cap = cv2.VideoCapture(active_index, cv2.CAP_DSHOW)
        else:
            cap = cv2.VideoCapture(active_index)
            
        return cap

    def _capture_task(self):
        self.is_capturing = True
        saved_files = []
        try:
            import cv2
            cap = self._get_video_capture()

            if not cap.isOpened():
                print(f"[Camara] [ERROR] No se pudo abrir la cámara con índice {self.camera_index}.")
                self.is_capturing = False
                return

            # Dar un pequeño respiro para que la cámara abra el flujo (calentamiento)
            time.sleep(0.5)

            for i in range(self.burst_count):
                ret, frame = cap.read()
                if ret and frame is not None:
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = os.path.join(self.save_path, f"captura_{timestamp}_{i+1}.jpg")
                    cv2.imwrite(filename, frame)
                    saved_files.append(filename)
                    print(f"[Camara] Foto {i+1}/{self.burst_count} guardada en {filename}")
                else:
                    print(f"[Camara] [ERROR] No se pudo leer el fotograma {i+1}.")
                
                # Esperar el delay si no es la última foto
                if i < self.burst_count - 1:
                    time.sleep(self.burst_delay)

            cap.release()
            print("[Camara] Ráfaga completada exitosamente.")
            
            if saved_files and self.event_bus:
                print(f"[Camara] Publicando evento BURST_CAPTURED con {len(saved_files)} imágenes...")
                self.event_bus.publish("BURST_CAPTURED", saved_files)
            
        except Exception as e:
            print(f"[Camara] [ERROR] Ocurrió un error en la captura: {e}")
        finally:
            self.is_capturing = False

    def stop(self):
        """Libera los recursos y el executor."""
        self.executor.shutdown(wait=False)

