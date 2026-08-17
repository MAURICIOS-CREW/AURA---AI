# Inicialización del módulo Core
from .ai_module import AIModule
from .qr.qr_interceptor import QRInterceptor
from .serial_controller import SerialController
from .camera_controller import CameraController
from .hardware_menu import run_hardware_menu
from .events import EventBus
from .plate import BurstAnalyzer, PlateDetector, PlateOCR, MexicanPlateValidator

__all__ = [
    "AIModule", 
    "QRInterceptor", 
    "SerialController", 
    "CameraController", 
    "run_hardware_menu", 
    "EventBus",
    "BurstAnalyzer",
    "PlateDetector",
    "PlateOCR",
    "MexicanPlateValidator"
]

