import os
import sys
import time
import argparse
from dotenv import load_dotenv

# Cargar variables de entorno antes de importar modulos que dependan de ellas
load_dotenv()

from core import AIModule, QRInterceptor, run_hardware_detection, SerialController, EventBus

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

    # Inicializar Bus de Eventos global (Mediador)
    event_bus = EventBus()

    # Inicializar controlador Serial (corre en su propio hilo)
    serial_controller = SerialController()
    serial_controller.start()

    # Nos suscribimos al evento de acceso concedido para abrir la pluma
    event_bus.subscribe("ACCESS_GRANTED", lambda *args, **kwargs: serial_controller.send_command("OPEN"))

    # Inicializar interceptor QR y pasarle el bus de eventos
    qr_interceptor = QRInterceptor(event_bus=event_bus)
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
        serial_controller.stop()
        qr_interceptor.join(timeout=2)
        ai_module.join(timeout=2)
        serial_controller.join(timeout=2)

if __name__ == "__main__":
    run_app()
