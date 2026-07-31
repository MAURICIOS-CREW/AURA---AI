# Inicialización del módulo Core
from .ai_module import AIModule
from .qr.qr_interceptor import QRInterceptor, run_hardware_detection
from .serial_controller import SerialController
from .events import EventBus

__all__ = ["AIModule", "QRInterceptor", "run_hardware_detection", "SerialController", "EventBus"]
