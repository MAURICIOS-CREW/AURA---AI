import os
import sys
import threading
import asyncio
from api.client import AccessValidationClient

class QRInterceptor(threading.Thread):
    def __init__(self, event_bus=None):
        super().__init__(daemon=True)
        self.event_bus = event_bus
        self.running = False
        self.buffer = ""
        self.api_client = AccessValidationClient()
        self.app_identifier = os.getenv("DEVICE_IDENTIFIER", "QR-Device")
        self.loop = None

        
        if sys.platform == 'win32':
            from .windows_qr import WindowsQRStrategy
            self.strategy = WindowsQRStrategy()
        elif sys.platform.startswith('linux'):
            from .linux_qr import LinuxQRStrategy
            self.strategy = LinuxQRStrategy()
        else:
            print(f"[QR] Plataforma {sys.platform} no soportada.")
            self.strategy = None

    def run(self):
        if not self.strategy:
            return
            
        self.running = True
        
        # Contexto: Creamos el loop asíncrono para las peticiones HTTP
        self.loop = asyncio.new_event_loop()
        def run_asyncio_loop(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()
            
        async_thread = threading.Thread(target=run_asyncio_loop, args=(self.loop,), daemon=True)
        async_thread.start()

        # Iniciar la estrategia bloqueante/asíncrona
        # La estrategia se encarga únicamente de escuchar el hardware y emitir callbacks
        print("[QR] Interceptor iniciado. Esperando lecturas...")
        self.strategy.start(on_char=self._on_char, on_enter=self._on_enter)

    def _on_char(self, char: str):
        """Callback llamado por la estrategia cuando entra un carácter válido."""
        self.buffer += char

    def _on_enter(self):
        """Callback llamado por la estrategia cuando el código QR termina (Enter)."""
        if self.buffer:
            code_to_validate = self.buffer
            self.buffer = ""
            print(f"[QR] Código interceptado exitosamente: {code_to_validate}")
            
            # Disparamos la petición HTTP en nuestro loop asíncrono secundario
            if self.loop:
                asyncio.run_coroutine_threadsafe(self._validate_and_process(code_to_validate), self.loop)

    async def _validate_and_process(self, hash_code: str):
        print(f"[QR] Enviando a validar: {hash_code}...")
        success, response = await self.api_client.validate_qr(hash_code, self.app_identifier)
        if success and response:
            print(f"[API] Resultado: {response.status.upper()} - {response.message}")
            if response.data:
                print(f"[API] Info: Invitado: {response.data.guest_name}, Residencia: {response.data.residence_id}")
            
            # Si el acceso es exitoso, disparamos un evento global
            if response.status.lower() == "granted" and self.event_bus:
                self.event_bus.publish("ACCESS_GRANTED", response.data)
        else:
            print("[API] Error de comunicación al validar el QR.")


    def stop(self):
        self.running = False
        if self.strategy:
            self.strategy.stop()
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)
        print("[QR] Interceptor detenido.")

def run_hardware_detection():
    """Modo especial delegado a las estrategias para detectar hardware."""
    if sys.platform == 'win32':
        from .windows_qr import run_hardware_detection_windows
        run_hardware_detection_windows()
    elif sys.platform.startswith('linux'):
        from .linux_qr import run_hardware_detection_linux
        run_hardware_detection_linux()
    else:
        print(f"Plataforma {sys.platform} no soportada.")
