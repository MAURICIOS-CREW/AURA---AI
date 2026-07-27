import os
import sys
import time
import argparse
from dotenv import load_dotenv

# Cargar variables de entorno antes de importar modulos que dependan de ellas
load_dotenv()

from core import AIModule, QRInterceptor, run_hardware_detection

def run_app():
    parser = argparse.ArgumentParser(description="AuraAI - Hilos Concurrentes de IA y QR")
    parser.add_argument("--test", "--init", action="store_true", help="Inicia el modo de detección de hardware para configurar el escáner QR.")
    args = parser.parse_args()

    if args.test:
        run_hardware_detection()
        sys.exit(0)

    print("Iniciando aplicación AuraAI...")
    host = os.getenv("HOST")
    print(f"Configuración HOST API: '{host}'")

    # Inicializar interceptor QR (corre en su propio hilo de SO y levanta su propio asyncio internamente)
    qr_interceptor = QRInterceptor()
    qr_interceptor.start()

    # Inicializar módulo de IA (corre en su propio hilo de SO)
    ai_module = AIModule()
    ai_module.start()
    
    try:
        # El hilo principal del programa se queda esperando
        # mientras los otros dos hilos independientes hacen el trabajo
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nSaliendo de la aplicación...")
    finally:
        qr_interceptor.stop()
        ai_module.stop()
        qr_interceptor.join(timeout=2)
        ai_module.join(timeout=2)

if __name__ == "__main__":
    run_app()
