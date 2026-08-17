import os
import cv2
import numpy as np
from typing import Optional, Tuple
from ultralytics import YOLO

class PlateDetector:
    """
    Detector de placas de vehículos utilizando un modelo YOLO.
    """
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or os.getenv("MODEL_PLATES_PATH", "./models/plate/best.pt")
        self._model = None

    def _get_model(self) -> YOLO:
        if self._model is None:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"[PlateDetector] Modelo de placas no encontrado en: {self.model_path}")
            print(f"[PlateDetector] Cargando modelo de placas desde: {self.model_path}")
            self._model = YOLO(self.model_path)
        return self._model

    def detect_and_crop(
        self, 
        image: np.ndarray, 
        conf_threshold: float = 0.15,
        enable_fallback: bool = True
    ) -> Tuple[Optional[np.ndarray], float, Optional[Tuple[int, int, int, int]], str]:
        """
        Detecta la placa en un fotograma OpenCV y retorna:
        (recorte_placa, confianza_de_detección, (x1, y1, x2, y2), metodo_usado)
        """
        if image is None or image.size == 0:
            return None, 0.0, None, "NONE"

        h, w = image.shape[:2]

        # 1. Intentar detección con modelo YOLO
        try:
            model = self._get_model()
            results = model(image, verbose=False)

            if len(results) > 0 and len(results[0].boxes) > 0:
                best_box_idx = int(results[0].boxes.conf.argmax())
                box = results[0].boxes[best_box_idx]
                confidence = float(box.conf[0])

                if confidence >= conf_threshold:
                    xyxy = box.xyxy[0].cpu().numpy()
                    x1, y1, x2, y2 = map(int, xyxy)
                    # Asegurar límites dentro de la imagen
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(w, x2), min(h, y2)
                    crop = image[y1:y2, x1:x2]
                    if crop.size > 0:
                        return crop, confidence, (x1, y1, x2, y2), "YOLO"
        except Exception as e:
            print(f"[PlateDetector] Aviso: fallo en inferencia YOLO: {e}")

        # 2. Fallback de visión por computadora tradicional (Búsqueda de rectángulos claros/blancos)
        if enable_fallback:
            cv_crop, cv_conf, cv_box = self._detect_cv_contour(image)
            if cv_crop is not None:
                return cv_crop, cv_conf, cv_box, "CV_CONTOUR"

            # 3. Fallback final: Imagen completa / Primer plano (Útil cuando la placa ocupa casi toda la toma)
            return image.copy(), 0.30, (0, 0, w, h), "FULL_IMAGE"

        return None, 0.0, None, "NONE"

    def _detect_cv_contour(self, image: np.ndarray) -> Tuple[Optional[np.ndarray], float, Optional[Tuple[int, int, int, int]]]:
        """
        Detecta regiones rectangulares claras con relación de aspecto típica de placas de circulación.
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # Filtro bilateral para suavizar ruidos manteniendo bordes definidos
            blur = cv2.bilateralFilter(gray, 9, 75, 75)
            # Umbral adaptativo o Otsu
            _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            h_img, w_img = image.shape[:2]
            img_area = h_img * w_img

            best_crop = None
            best_box = None
            max_score = 0.0

            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < (img_area * 0.015) or area > (img_area * 0.90):
                    continue

                x, y, w, h = cv2.boundingRect(cnt)
                aspect_ratio = float(w) / float(h)

                # Relación de aspecto de placas en México (~1.8 a ~3.5)
                if 1.5 <= aspect_ratio <= 4.0:
                    # Evaluar si el interior contiene brillo adecuado
                    roi_gray = gray[y:y+h, x:x+w]
                    mean_val = float(np.mean(roi_gray))
                    if mean_val > 80:  # Placa clara / reflectante
                        score = area / img_area
                        if score > max_score:
                            max_score = score
                            # Añadir un pequeño margen/padding
                            pad_w = int(w * 0.05)
                            pad_h = int(h * 0.05)
                            x1, y1 = max(0, x - pad_w), max(0, y - pad_h)
                            x2, y2 = min(w_img, x + w + pad_w), min(h_img, y + h + pad_h)
                            best_crop = image[y1:y2, x1:x2]
                            best_box = (x1, y1, x2, y2)

            if best_crop is not None and best_crop.size > 0:
                return best_crop, 0.45, best_box
        except Exception:
            pass

        return None, 0.0, None
