import sys
import time

def run_camera_test():
    """Menú para listar cámaras disponibles y probarlas."""
    try:
        import cv2
    except ImportError:
        print("\n[Error] La librería 'opencv-python' no está instalada.")
        print("Instálala usando: pip install opencv-python")
        return

    print("\n" + "="*60)
    print("MODO DE DETECCIÓN DE HARDWARE (CÁMARA)")
    print("="*60)
    print("Buscando cámaras disponibles... (Esto puede tardar unos segundos)\n")
    
    import glob

    available_cameras = []
    
    # Obtener lista de índices a probar
    candidate_indices = []
    if sys.platform.startswith('linux'):
        dev_files = glob.glob("/dev/video*")
        for dev in dev_files:
            try:
                idx = int(dev.replace("/dev/video", ""))
                candidate_indices.append(idx)
            except ValueError:
                pass
        candidate_indices.sort()

    if not candidate_indices:
        candidate_indices = list(range(71))

    for i in candidate_indices:
        if sys.platform.startswith('linux'):
            cap = cv2.VideoCapture(i, cv2.CAP_V4L2)
        elif sys.platform == 'win32':
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        else:
            cap = cv2.VideoCapture(i)
            
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                available_cameras.append(i)
            cap.release()

    if not available_cameras:
        print("No se encontró ninguna cámara disponible o conectada.")
        return

    print("Cámaras encontradas en los siguientes índices:")
    for idx in available_cameras:
        print(f"  [{idx}] Cámara {idx}")
        
    print("\nSelecciona el índice de la cámara que deseas probar (o presiona Enter para cancelar):")
    choice = input("Índice > ").strip()
    
    if not choice:
        return
        
    try:
        selected_index = int(choice)
        if selected_index not in available_cameras:
            print("Índice no válido.")
            return
    except ValueError:
        print("Entrada no válida.")
        return
        
    print(f"\nIniciando prueba con cámara {selected_index}...")
    print("Presiona la tecla 'q' en la ventana de video para salir de la prueba.")
    
    if sys.platform.startswith('linux'):
        cap = cv2.VideoCapture(selected_index, cv2.CAP_V4L2)
    elif sys.platform == 'win32':
        cap = cv2.VideoCapture(selected_index, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(selected_index)
        
    if not cap.isOpened():
        print("No se pudo abrir la cámara para la prueba.")
        return
        
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error al leer de la cámara.")
            break
            
        cv2.imshow(f"Prueba de Camara {selected_index} (Presiona 'q' para salir)", frame)
        
        # Salir si se presiona 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()
    print(f"\nPrueba finalizada. Si esta es la cámara correcta, asegúrate de configurar:")
    print(f"CAMERA_INDEX={selected_index}")
    print("En tu archivo .env.")


def run_hardware_menu():
    """Menú principal interactivo de pruebas e inicialización."""
    while True:
        print("\n" + "="*60)
        print("    MENÚ DE CONFIGURACIÓN Y PRUEBA DE HARDWARE (--debug / --init)")
        print("="*60)
        print("1. Identificar y probar Lector QR")
        print("2. Identificar y probar Cámaras")
        print("3. Salir")
        print("="*60)
        
        choice = input("Selecciona una opción (1-3): ").strip()
        
        if choice == '1':
            if sys.platform == 'win32':
                from .qr.windows_qr import run_hardware_detection_windows
                run_hardware_detection_windows()
            elif sys.platform.startswith('linux'):
                from .qr.linux_qr import run_hardware_detection_linux
                run_hardware_detection_linux()
            else:
                print(f"Plataforma {sys.platform} no soportada para QR interactivo.")
        elif choice == '2':
            run_camera_test()
        elif choice == '3' or choice.lower() in ('q', 'quit', 'exit'):
            print("Saliendo del menú de hardware.")
            break
        else:
            print("Opción inválida. Intenta nuevamente.")
