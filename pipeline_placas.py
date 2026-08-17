import os
import sys
import asyncio
from dotenv import load_dotenv

# Cargar variables de entorno (.env)
load_dotenv()

from core.plate import BurstAnalyzer
from api.client import AccessValidationClient

def procesar_acceso_prueba(rutas_imagenes):
    """
    Script de prueba refactorizado para ejecutar la evaluación de placas y validación API
    utilizando las clases modulares de AuraAI.
    """
    if isinstance(rutas_imagenes, str):
        rutas_imagenes = [rutas_imagenes]

    print("==========================================")
    print("  AURAAI - PRUEBA DE PIPELINE DE PLACAS   ")
    print("==========================================")
    print(f"Imágenes a procesar: {rutas_imagenes}")

    analyzer = BurstAnalyzer()
    resultado = analyzer.analyze_burst(rutas_imagenes)

    if not resultado:
        print("[PRUEBA] No se pudo obtener ninguna placa válida de la ráfaga.")
        return

    print("\n--- RESULTADO DE LA MEJOR TOMA ---")
    print(f"Imagen seleccionada: {resultado.image_path}")
    print(f"Placa bruta OCR:     {resultado.plate_text}")
    print(f"Placa limpia:        {resultado.cleaned_plate}")
    print(f"Confianza Placa:     {resultado.plate_confidence:.4f}")
    print(f"Confianza OCR:       {resultado.ocr_confidence:.4f}")
    print(f"Formato México:      {resultado.format_score:.4f}")
    print(f"Puntaje Compuesto:   {resultado.composite_score:.4f}")

    print("\n[PRUEBA] Enviando placa al servidor API...")
    client = AccessValidationClient()
    exito, respuesta = asyncio.run(client.validate_plate(resultado.cleaned_plate))

    if exito and respuesta:
        print("\n--- RESPUESTA DE API ---")
        print(f"Estado:  {respuesta.status}")
        print(f"Mensaje: {respuesta.message}")
        print(f"Datos:   {respuesta.data}")
    else:
        print("\n[PRUEBA] Error o acceso denegado en la API.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        imagenes = sys.argv[1:]
    else:
        imagenes = ["coche_prueba.jpg"]
    
    procesar_acceso_prueba(imagenes)