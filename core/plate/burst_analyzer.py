import cv2
import os
import time
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from .detector import PlateDetector
from .ocr import PlateOCR
from .validator import MexicanPlateValidator

@dataclass
class PlateResult:
    image_path: str
    plate_text: str
    cleaned_plate: str
    plate_confidence: float
    ocr_confidence: float
    format_score: float
    composite_score: float
    detection_method: str = "UNKNOWN"
    bbox: Optional[Tuple[int, int, int, int]] = None
    char_details: List[dict] = field(default_factory=list)
    debug_crop_path: Optional[str] = None
    debug_annotated_path: Optional[str] = None

class BurstAnalyzer:
    """
    Analizador de ráfagas de fotos para seleccionar la mejor toma de placa
    con soporte para fallbacks de detección y depuración visual.
    """
    def __init__(
        self, 
        detector: Optional[PlateDetector] = None, 
        ocr: Optional[PlateOCR] = None,
        debug_mode: Optional[bool] = None,
        debug_dir: Optional[str] = None
    ):
        self.detector = detector or PlateDetector()
        self.ocr = ocr or PlateOCR()
        
        # Cargar variables de configuración de depuración
        if debug_mode is not None:
            self.debug_mode = debug_mode
        else:
            self.debug_mode = os.getenv("DEBUG_SAVE_IMAGES", "true").lower() in ("true", "1", "yes")

        self.debug_dir = debug_dir or os.getenv("DEBUG_OUTPUT_DIR", "./storage/debug")
        self.plate_conf_threshold = float(os.getenv("PLATE_CONF_THRESHOLD", "0.15"))
        self.ocr_conf_threshold = float(os.getenv("OCR_CONF_THRESHOLD", "0.20"))

        if self.debug_mode:
            os.makedirs(self.debug_dir, exist_ok=True)

    def analyze_burst(self, image_paths: List[str]) -> Optional[PlateResult]:
        """
        Analiza una ráfaga de imágenes y retorna la mejor toma de placa encontrada.
        """
        if not image_paths:
            print("[BurstAnalyzer] No se recibieron imágenes para analizar.")
            return None

        candidates: List[PlateResult] = []
        timestamp_str = time.strftime("%Y%m%d_%H%M%S")

        print(f"[BurstAnalyzer] Analizando ráfaga de {len(image_paths)} fotos (Debug={self.debug_mode})...")
        for idx, path in enumerate(image_paths):
            if not os.path.exists(path):
                print(f"[BurstAnalyzer] Imagen no encontrada: {path}")
                continue

            image = cv2.imread(path)
            if image is None:
                print(f"[BurstAnalyzer] Error al cargar la imagen: {path}")
                continue

            crop, plate_conf, box, method = self.detector.detect_and_crop(
                image, 
                conf_threshold=self.plate_conf_threshold,
                enable_fallback=True
            )

            if crop is None:
                print(f"[BurstAnalyzer] No se detectó placa ni región candidata en: {path}")
                continue

            raw_text, ocr_conf, char_details = self.ocr.read_plate(
                crop, 
                conf_threshold=self.ocr_conf_threshold
            )
            cleaned_text = MexicanPlateValidator.clean_text(raw_text)

            print(f"[BurstAnalyzer] [{os.path.basename(path)}] Método={method}, Box={box}, PlateConf={plate_conf:.3f}, OCR Raw='{raw_text}', Cleaned='{cleaned_text}', OCRConf={ocr_conf:.3f}")

            if not cleaned_text:
                print(f"[BurstAnalyzer] OCR sin caracteres válidos en: {path}")
                continue

            fmt_score = MexicanPlateValidator.evaluate_format(cleaned_text)
            comp_score = MexicanPlateValidator.calculate_candidate_score(cleaned_text, ocr_conf, plate_conf)

            # Generar imágenes de depuración si está activado
            debug_crop_path = None
            debug_annotated_path = None

            if self.debug_mode and crop is not None:
                base_filename = f"debug_{timestamp_str}_frame{idx+1}_{os.path.splitext(os.path.basename(path))[0]}"
                
                # Image 1: Anotación en imagen original con caja de detección
                annotated_full = image.copy()
                if box is not None:
                    x1, y1, x2, y2 = box
                    color = (0, 255, 0) if method == "YOLO" else (255, 165, 0)
                    cv2.rectangle(annotated_full, (x1, y1), (x2, y2), color, 3)
                    label = f"[{method}] Conf: {plate_conf:.2f}"
                    cv2.putText(annotated_full, label, (x1, max(25, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                
                debug_annotated_path = os.path.join(self.debug_dir, f"{base_filename}_det.jpg")
                cv2.imwrite(debug_annotated_path, annotated_full)

                # Image 2: Crop anotado con caracteres detectados por el OCR
                annotated_crop = crop.copy()
                for cdet in char_details:
                    cx1, cy1, cx2, cy2 = cdet['box']
                    char_str = cdet['char']
                    cconf = cdet['conf']
                    cv2.rectangle(annotated_crop, (cx1, cy1), (cx2, cy2), (255, 0, 255), 2)
                    cv2.putText(annotated_crop, f"{char_str}:{cconf:.2f}", (cx1, max(15, cy1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)

                cv2.putText(annotated_crop, f"RESULT: {cleaned_text} ({comp_score:.2f})", (10, annotated_crop.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                debug_crop_path = os.path.join(self.debug_dir, f"{base_filename}_ocr.jpg")
                cv2.imwrite(debug_crop_path, annotated_crop)

            result = PlateResult(
                image_path=path,
                plate_text=raw_text,
                cleaned_plate=cleaned_text,
                plate_confidence=plate_conf,
                ocr_confidence=ocr_conf,
                format_score=fmt_score,
                composite_score=comp_score,
                detection_method=method,
                bbox=box,
                char_details=char_details,
                debug_crop_path=debug_crop_path,
                debug_annotated_path=debug_annotated_path
            )
            candidates.append(result)
            print(f"[BurstAnalyzer] -> Candidato Registrado [{os.path.basename(path)}]: Placa='{cleaned_text}' (ScoreCompuesto={comp_score:.4f}, FormatScore={fmt_score:.2f})")

        if not candidates:
            print("[BurstAnalyzer] Ráfaga procesada pero no se encontró ninguna placa reconocible.")
            return None

        # Ordenar candidatos de mayor a menor puntaje compuesto
        candidates.sort(key=lambda c: c.composite_score, reverse=True)
        best_candidate = candidates[0]
        print(f"[BurstAnalyzer] ★ MEJOR TOMA SELECCIONADA: '{best_candidate.cleaned_plate}' desde {os.path.basename(best_candidate.image_path)} (Score={best_candidate.composite_score:.4f}, Método={best_candidate.detection_method})")
        if best_candidate.debug_annotated_path:
            print(f"[BurstAnalyzer] Imagen de depuración guardada en: {best_candidate.debug_annotated_path}")

        return best_candidate
