import serial
import time
import os
from dotenv import load_dotenv

load_dotenv()

port = os.getenv("SERIAL_PORT", "/dev/ttyUSB0")
baudrate = int(os.getenv("SERIAL_BAUDRATE", "115200"))

print(f"Probando conexión a {port} a {baudrate} baudios...")

try:
    # Usar DTR/RTS en false puede prevenir que el ESP32 se reinicie al conectar
    ser = serial.Serial()
    ser.port = port
    ser.baudrate = baudrate
    ser.timeout = 2
    ser.setDTR(False)
    ser.setRTS(False)
    
    ser.open()
    print("Conexión abierta. Esperando 2 segundos para que el ESP32 inicie...")
    
    # IMPORTANTE: Muchos ESP32 se reinician inevitablemente al abrir el puerto.
    # Si mandamos el comando inmediatamente, el ESP32 está arrancando y lo ignora.
    time.sleep(2)
    
    # Enviar un comando de prueba (Arduino IDE suele mandar \r\n)
    comando = b"OPEN\r\n"
    print(f"Enviando comando: {comando}...")
    ser.write(comando)
    
    while True:
        if ser.in_waiting > 0:
            # Leer crudo para ver exactamente qué llega
            raw_data = ser.readline()
            print(f"Recibido (crudo): {raw_data}")
            try:
                print(f"Recibido (texto): {raw_data.decode('utf-8', errors='replace').strip()}")
            except Exception as e:
                print(f"Error decodificando: {e}")
        else:
            time.sleep(0.1)

except Exception as e:
    print(f"Error: {e}")
except KeyboardInterrupt:
    print("\nSaliendo...")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
