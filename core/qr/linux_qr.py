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
            print(f"[QR-Linux] Interceptor conectado, dispositivo: {device.name}")
            device.grab()
        except Exception as e:
            print(f"[QR-Linux] Error abriendo el dispositivo '{self.device_id}': {e}")
            print(f"[QR-Linux] Asegúrate de ejecutar con permisos sudo o pertenecer al grupo input.")
            return

        shift_active = False
        try:
            async for event in device.async_read_loop():
                if not self.running:
                    break
                    
                if event.type == evdev.ecodes.EV_KEY:
                    key_event = evdev.categorize(event)
                    keycode = key_event.keycode
                    if isinstance(keycode, list):
                        keycode = keycode[0]
                        
                    if key_event.keystate == key_event.key_down:
                        if keycode in ('KEY_LEFTSHIFT', 'KEY_RIGHTSHIFT'):
                            shift_active = True
                            continue
                            
                        if keycode in ('KEY_ENTER', 'KEY_KPENTER', 'KEY_END'):
                            on_enter()
                        elif keycode.startswith('KEY_'):
                            key_char = keycode.replace('KEY_', '')
                            if len(key_char) == 1:
                                if shift_active:
                                    on_char(key_char.upper())
                                else:
                                    on_char(key_char.lower())
                            elif key_char == 'MINUS':
                                on_char('_' if shift_active else '-')
                            elif key_char == 'SPACE':
                                on_char(' ')
                    elif key_event.keystate == key_event.key_up:
                        if keycode in ('KEY_LEFTSHIFT', 'KEY_RIGHTSHIFT'):
                            shift_active = False
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
        
    # Crear un mapa de rutas reales a enlaces simbólicos en by-id
    by_id_map = {}
    by_id_dir = "/dev/input/by-id"
    if os.path.exists(by_id_dir):
        for filename in os.listdir(by_id_dir):
            symlink_path = os.path.join(by_id_dir, filename)
            if os.path.islink(symlink_path):
                real_path = os.path.realpath(symlink_path)
                by_id_map[real_path] = symlink_path
                
    for device in devices:
        real_device_path = os.path.realpath(device.path)
        best_path = by_id_map.get(real_device_path, device.path)
        print(f"Device Path: {best_path}\n    └─ Nombre: {device.name}\n")
        
    print("Busca tu lector QR en la lista anterior (usualmente tiene un nombre descriptivo o dice 'Wireless' / 'Keyboard').")
    print("Copia el texto de 'Device Path' (ej. /dev/input/by-id/usb-Mi_Lector-event-kbd)")
    print("y colócalo en tu archivo .env como el valor de la variable QR_DEVICE_ID.\n")
