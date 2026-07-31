import os
import time
import json
import threading
import serial

class SerialController(threading.Thread):
    """
    Controlador para la comunicación serial con el ESP32.
    Se ejecuta en su propio hilo para no bloquear el resto de la aplicación.
    """
    def __init__(self):
        super().__init__(daemon=True)
        self.port = os.getenv("SERIAL_PORT", "/dev/ttyUSB0")
        self.baudrate = int(os.getenv("SERIAL_BAUDRATE", "115200"))
        self.running = False
        self.serial_conn = None
        self._lock = threading.Lock()

    def connect(self):
        try:
            self.serial_conn = serial.Serial()
            self.serial_conn.port = self.port
            self.serial_conn.baudrate = self.baudrate
            self.serial_conn.timeout = 1
            # Evitar reiniciar el ESP32 al conectar
            self.serial_conn.setDTR(False)
            self.serial_conn.setRTS(False)
            self.serial_conn.open()
            print(f"[Serial] Conectado a {self.port} a {self.baudrate} baudios.")
            return True
        except serial.SerialException as e:
            print(f"[Serial] Advertencia: No se pudo conectar a {self.port}: {e}")
            print("[Serial] El programa continuará, pero los comandos seriales no se enviarán.")
            return False

    def run(self):
        if not self.connect():
            # Si no se pudo conectar, nos mantenemos vivos pero sin hacer nada 
            # para no romper la arquitectura si el ESP no está conectado.
            self.running = True
            while self.running:
                time.sleep(1)
            return
            
        # IMPORTANTE: Dar tiempo al ESP32 a que reinicie tras conectar
        print("[Serial] Conexión abierta. Esperando 2 segundos para inicio del ESP32...")
        time.sleep(2)
        
        self.running = True
        print("[Serial] Hilo de lectura serial listo.")
        
        while self.running:
            try:
                if self.serial_conn and self.serial_conn.is_open and self.serial_conn.in_waiting > 0:
                    line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        self._process_message(line)
                else:
                    time.sleep(0.05)
            except Exception as e:
                print(f"[Serial] Error leyendo del puerto: {e}")
                time.sleep(1) # Prevenir bucle rápido en caso de error

    def _process_message(self, line: str):
        try:
            data = json.loads(line)
            msg_type = data.get("type")
            if msg_type == "response":
                print(f"[ESP32 Resp] {data.get('status')}: {data.get('message')} {data.get('data', '')}")
            elif msg_type == "event":
                print(f"[ESP32 Evt] {data.get('name')}: {data.get('message')}")
            else:
                print(f"[ESP32 RAW] {line}")
        except json.JSONDecodeError:
            # Si no es un JSON válido, simplemente lo imprimimos
            print(f"[ESP32 RAW] {line}")

    def send_command(self, command: str):
        """
        Envía un comando al ESP32.
        Comandos soportados: OPEN, CLOSE, STATUS, PING
        """
        if self.serial_conn and self.serial_conn.is_open:
            if not command.endswith('\r\n'):
                command = command.strip() + '\r\n'
            with self._lock:
                try:
                    self.serial_conn.write(command.encode('utf-8'))
                    print(f"[Serial] Comando enviado: {command.strip()}")
                except Exception as e:
                    print(f"[Serial] Error enviando comando: {e}")
        else:
            print(f"[Serial] Error: No hay conexión serial para enviar el comando: {command.strip()}")

    def stop(self):
        self.running = False
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.close()
                print("[Serial] Conexión cerrada.")
            except Exception as e:
                print(f"[Serial] Error cerrando conexión: {e}")
