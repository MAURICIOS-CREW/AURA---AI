import re

class MexicanPlateValidator:
    """
    Validador y evaluador de coincidencia de formato para placas de vehículos en México.
    
    Formatos comunes en México:
    - Particulares: 3 letras + 3 o 4 dígitos (ej. ABC1234, ABC123)
    - Formatos recientes / Estatales: 3 letras + 2 dígitos + 1 letra (ej. ABC12A) o XX1234X, XXX123, XX1234
    - Camiones / Carga / Motos: variaciones de 6-7 caracteres alfanuméricos.
    """

    # Regex para combinaciones típicas de placas mexicanas (automóviles y camiones)
    MEXICAN_PLATE_PATTERNS = [
        re.compile(r'^[A-Z]{3}\d{3,4}$'),       # ABC1234 o ABC123
        re.compile(r'^[A-Z]{3}\d{2}[A-Z]$'),    # ABC12A
        re.compile(r'^[A-Z]{2}\d{3,4}[A-Z]$'),  # AB1234C
        re.compile(r'^[A-Z]{2}\d{4}$'),         # AB1234
        re.compile(r'^\d{3}[A-Z]{3}$'),         # 123ABC
        re.compile(r'^[A-Z0-9]{6,7}$')          # Genérico alfanumérico 6-7 caracteres
    ]

    @classmethod
    def clean_text(cls, text: str) -> str:
        """Limpia el texto dejando solo caracteres alfanuméricos en mayúsculas."""
        if not text:
            return ""
        # Eliminar guiones, espacios y caracteres no alfanuméricos (aceptar minúsculas y convertir a mayúsculas)
        cleaned = re.sub(r'[^a-zA-Z0-9]', '', text)
        return cleaned.upper()


    @classmethod
    def evaluate_format(cls, text: str) -> float:
        """
        Evalúa el formato de la placa y retorna un puntaje entre 0.0 y 1.0.
        """
        cleaned = cls.clean_text(text)
        if not cleaned:
            return 0.0

        length = len(cleaned)
        
        # Penalizar fuertemente longitudes inadecuadas
        if length < 4 or length > 9:
            return 0.1

        # Puntuación base por longitud ideal (6-7 caracteres)
        if length in (6, 7):
            score = 0.8
        elif length in (5, 8):
            score = 0.5
        else:
            score = 0.3

        # Verificar concordancia con patrones de placas de México
        for pattern in cls.MEXICAN_PLATE_PATTERNS:
            if pattern.match(cleaned):
                score = min(1.0, score + 0.2)
                break

        return score

    @classmethod
    def calculate_candidate_score(cls, plate_text: str, ocr_confidence: float, plate_confidence: float) -> float:
        """
        Calcula una puntuación compuesta (0.0 a 1.0) para comparar tomas de una ráfaga.
        Ponderación:
        - 40% Validez de formato mexicano
        - 40% Confianza promedio del OCR
        - 20% Confianza de detección de la placa
        """
        format_score = cls.evaluate_format(plate_text)
        composite = (format_score * 0.40) + (ocr_confidence * 0.40) + (plate_confidence * 0.20)
        return round(composite, 4)
