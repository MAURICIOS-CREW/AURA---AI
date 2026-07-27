import os
import asyncio

class LinuxQRStrategy:
    """Estrategia para interceptar hardware en Linux usando evdev."""
    def __init__(self):
        self.device_id = os.getenv("QR_DEVICE_ID", "")
        self.running = False

    def start(self, on_char, on_enter):
        if not self.device_id:
            print("[QR-Linux] ADVERTENCIA: QR_DEVICE_ID no configurado en el .env")
            print("[QR-Linux] Ejecuta el programa con --init o --test para identificar el dispositivo.")
            return

        self.running = True
        # Envolvemos el bucle asíncrono de evdev para bloquear el hilo,
        # cumpliendo con el contrato de start() como lo hace Tkinter en Windows.
        asyncio.run(self._async_run(on_char, on_enter))

    async def _async_run(self, on_char, on_enter):
        try:
            import evdev
        except ImportError:
            print("[QR-Linux] Error: La librería 'evdev' no está instalada.")
            return

        try:
            device = evdev.InputDevice(self.device_id)
            print(f"[QR-Linux] Interceptor conectado y agarrando (grab) dispositivo: {device.name}")
            device.grab()
        except Exception as e:
            print(f"[QR-Linux] Error abriendo el dispositivo '{self.device_id}': {e}")
            print(f"[QR-Linux] Asegúrate de ejecutar con permisos sudo o pertenecer al grupo input.")
            return

        try:
            async for event in device.async_read_loop():
                if not self.running:
                    break
                    
                if event.type == evdev.ecodes.EV_KEY:
                    key_event = evdev.categorize(event)
                    if key_event.keystate == key_event.key_down:
                        keycode = key_event.keycode
                        if isinstance(keycode, list):
                            keycode = keycode[0] 
                            
                        if keycode in ('KEY_ENTER', 'KEY_KPENTER'):
                            on_enter()
                        elif keycode.startswith('KEY_'):
                            key_char = keycode.replace('KEY_', '')
                            if len(key_char) == 1:
                                on_char(key_char.lower())
                            elif key_char == 'MINUS':
                                on_char('-')
        except Exception as e:
            print(f"[QR-Linux] Bucle de lectura abortado: {e}")
        finally:
            try:
                device.ungrab()
            except Exception:
                pass

    def stop(self):
        self.running = False


def run_hardware_detection_linux():
    try:
        import evdev
    except ImportError:
        print("La librería 'evdev' no está instalada. Ejecuta 'pip install -r requirements.txt'")
        return

    print("\n" + "="*60)
    print("MODO DE DETECCIÓN DE HARDWARE (LINUX)")
    print("="*60)
    print("Dispositivos de entrada disponibles en tu sistema:\n")
    
    try:
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    except Exception as e:
        print(f"Error listando dispositivos: {e}")
        print("Recuerda que en Linux usualmente necesitas 'sudo' o pertenecer al grupo 'input' para acceder a /dev/input/")
        return

    if not devices:
        print("No se encontraron dispositivos en /dev/input/")
        return
        
    for device in devices:
        print(f"Device Path: {device.path}  |  Nombre: {device.name}")
        
    print("\nBusca tu lector QR en la lista anterior.")
    print("Copia el texto de 'Device Path' (ej. /dev/input/event3)")
    print("y colócalo en tu archivo .env como el valor de la variable QR_DEVICE_ID.\n")
