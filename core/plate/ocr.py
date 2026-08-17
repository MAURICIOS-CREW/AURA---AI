import os
import cv2
import numpy as np
from typing import Optional, Tuple, List
from ultralytics import YOLO

class PlateOCR:
    """
    Reconocedor OCR de caracteres en placas utilizando un modelo YOLO.
    """
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or os.getenv("MODEL_OCR_PATH", "./models/ocr/best.pt")
        self._model = None

    def _get_model(self) -> YOLO:
        if self._model is None:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"[PlateOCR] Modelo de OCR no encontrado en: {self.model_path}")
            print(f"[PlateOCR] Cargando modelo de OCR desde: {self.model_path}")
            self._model = YOLO(self.model_path)
        return self._model

    def read_plate(self, crop_image: np.ndarray, conf_threshold: float = 0.20) -> Tuple[str, float, List[dict]]:
        """
        Lee los caracteres del recorte de la placa.
        Retorna (texto_placa, confianza_promedio_ocr, lista_detalles_caracteres).
        """
        if crop_image is None or crop_image.size == 0:
            return "", 0.0, []

        model = self._get_model()
        results = model(crop_image, verbose=False)

        if len(results) == 0 or len(results[0].boxes) == 0:
            return "", 0.0, []

        raw_detections = []
        boxes = results[0].boxes
        for xyxy, cls_id, conf in zip(boxes.xyxy, boxes.cls, boxes.conf):
            confidence = float(conf)
            if confidence < conf_threshold:
                continue

            coords = xyxy.cpu().numpy()
            x1, y1, x2, y2 = map(int, coords)
            char_name = model.names[int(cls_id)]
            raw_detections.append({
                'char': char_name,
                'conf': confidence,
                'box': (x1, y1, x2, y2),
                'x_center': (x1 + x2) / 2.0
            })

        if not raw_detections:
            return "", 0.0, []

        # Filtrar duplicados / solapamientos fuertes (conservando el de mayor confianza)
        raw_detections.sort(key=lambda d: d['conf'], reverse=True)
        filtered_detections = []
        for det in raw_detections:
            x1, y1, x2, y2 = det['box']
            overlap = False
            for kept in filtered_detections:
                kx1, ky1, kx2, ky2 = kept['box']
                # Calcular la intersección horizontal
                inter_x1 = max(x1, kx1)
                inter_x2 = min(x2, kx2)
                inter_w = max(0, inter_x2 - inter_x1)
                min_w = min(x2 - x1, kx2 - kx1)
                if min_w > 0 and (inter_w / min_w) > 0.60:
                    overlap = True
                    break
            if not overlap:
                filtered_detections.append(det)

        # Ordenar caracteres de izquierda a derecha por coordenada X central
        filtered_detections.sort(key=lambda d: d['x_center'])
        plate_text = "".join([d['char'] for d in filtered_detections])
        avg_confidence = float(np.mean([d['conf'] for d in filtered_detections])) if filtered_detections else 0.0

        return plate_text, avg_confidence, filtered_detections
