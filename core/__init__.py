# Inicialización del módulo Core
from .ai_module import AIModule
from .qr.qr_interceptor import QRInterceptor, run_hardware_detection

__all__ = ["AIModule", "QRInterceptor", "run_hardware_detection"]
