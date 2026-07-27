import os
import tkinter as tk

class WindowsQRStrategy:
    """Estrategia para interceptar hardware en Windows usando winrawin y Tkinter."""
    def __init__(self):
        self.device_id = os.getenv("QR_DEVICE_ID", "")
        self.tk_root = None
        self.running = False

    def start(self, on_char, on_enter):
        if not self.device_id:
            print("[QR-Windows] ADVERTENCIA: QR_DEVICE_ID no configurado en el .env")
            print("[QR-Windows] Ejecuta el programa con --init o --test para identificar el dispositivo.")
            return

        import winrawin
        import winrawin._api

        # Parche de seguridad para la librería
        import winrawin._device_id
        original_parse = winrawin._api.parse_device_id
        def safe_parse_device_id(device_id: str):
            try:
                return original_parse(device_id)
            except Exception:
                return winrawin._device_id.DeviceID('UNKNOWN', None, None, None, None)
        winrawin._api.parse_device_id = safe_parse_device_id

        self.running = True
        self.tk_root = tk.Tk()
        self.tk_root.withdraw()

        def _handle_event(event):
            if not self.running:
                if self.tk_root:
                    self.tk_root.quit()
                return
                
            if event.event_type != 'down':
                return
                
            if self.device_id and self.device_id not in event.device.path:
                return
                
            char = event.name
            if event.vkey == 13: 
                on_enter()
            else:
                if char and len(char) == 1 and char.isprintable():
                    on_char(char)

        winrawin.hook_raw_input_for_window(self.tk_root.winfo_id(), _handle_event)
        
        # Bloquea el hilo actual (esperado por la clase Contexto)
        self.tk_root.mainloop()

    def stop(self):
        self.running = False
        if self.tk_root:
            self.tk_root.quit()


def run_hardware_detection_windows():
    import winrawin
    import winrawin._api

    original_parse = winrawin._api.parse_device_id
    def safe_parse_device_id(device_id: str):
        try:
            return original_parse(device_id)
        except Exception:
            return winrawin._api.DeviceID('UNKNOWN', None, None, None, None)
    winrawin._api.parse_device_id = safe_parse_device_id

    print("\n" + "="*60)
    print("MODO DE DETECCIÓN DE HARDWARE (WINDOWS)")
    print("="*60)
    print("Por favor, escanea un código QR ahora o presiona teclas en tu lector.")
    print("Copia el texto del campo 'Device Path' y colócalo en tu archivo .env")
    print("como el valor de la variable QR_DEVICE_ID.")
    print("\nPresiona Ctrl+C en esta consola para salir cuando hayas terminado.\n")
    
    root = tk.Tk()
    root.withdraw()
    
    def on_event(event: winrawin.RawInputEvent):
        if event.event_type == 'down':
            print(f"[{event.name}] - Device Path: {event.device.path}")
            
    winrawin.hook_raw_input_for_window(root.winfo_id(), on_event)
    
    def check_signals():
        root.after(100, check_signals)
    root.after(100, check_signals)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nSaliendo del modo de detección...")
