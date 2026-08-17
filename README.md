# AuraAI

Documentación técnica y guía de configuración para el entorno de desarrollo del proyecto AuraAI.

## Requisitos Previos

- Python 3.10 o superior.
- Git.

## Guía de Instalación

### 1. Instalación de Python

#### Entorno Windows
1. Descargue el instalador de Python desde el [sitio web oficial](https://www.python.org/downloads/windows/).
2. Ejecute el archivo descargado.
3. **Importante:** En la primera pantalla del asistente de instalación, asegúrese de marcar la casilla **"Add Python to PATH"** (Agregar Python al PATH).
4. Seleccione "Install Now" y espere a que finalice el proceso.
5. Verifique la instalación abriendo una nueva terminal (Command Prompt o PowerShell) y ejecutando el siguiente comando:
   ```powershell
   python --version
   ```

#### Entorno Linux (Debian/Ubuntu)
1. Actualice los repositorios del sistema:
   ```bash
   sudo apt update
   ```
2. Instale Python 3, el gestor de paquetes `pip` y el módulo `venv`:
   ```bash
   sudo apt install python3 python3-venv python3-pip
   ```
3. Verifique la instalación:
   ```bash
   python3 --version
   ```

### 2. Clonación del Repositorio

Abra una terminal, clone el repositorio y navegue hacia el directorio raíz del proyecto:
```bash
git clone <url_del_repositorio>
cd AuraAI
```

### 3. Configuración de Variables de Entorno

El proyecto requiere variables de entorno para funcionar correctamente. Se proporciona un archivo de plantilla llamado `.env.example`.

1. Duplique el archivo `.env.example` y nombre la copia como `.env`.
   - **En Windows:**
     ```powershell
     copy .env.example .env
     ```
   - **En Linux/macOS:**
     ```bash
     cp .env.example .env
     ```
2. Abra el archivo `.env` generado y asigne los valores correspondientes a cada variable (por ejemplo, `HOST`).

### 4. Creación y Activación del Entorno Virtual (venv)

El uso de un entorno virtual garantiza que las dependencias del proyecto se mantengan aisladas del sistema operativo.

#### En Windows
1. Para crear el entorno virtual, ejecute:
   ```powershell
   python -m venv .venv
   ```
2. Para activar el entorno virtual:
   - Si utiliza **PowerShell**:
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - Si utiliza **Command Prompt (CMD)**:
     ```cmd
     .venv\Scripts\activate.bat
     ```

#### En Linux/macOS
1. Para crear el entorno virtual, ejecute:
   ```bash
   python3 -m venv .venv
   ```
2. Para activar el entorno virtual:
   ```bash
   source .venv/bin/activate
   ```

*Nota: Sabrá que el entorno virtual está activo porque el identificador `(.venv)` aparecerá al inicio de la línea de comandos en su terminal.*

### 5. Instalación de Dependencias

Una vez que el entorno virtual se encuentre activo, proceda a instalar las librerías requeridas especificadas en el archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 6. Ejecución del Proyecto

#### Configuración y Permisos del Escáner QR (Hardware)

Antes de ejecutar la aplicación, debes configurar el escáner QR en tu archivo `.env` y asegurarte de tener los permisos correctos en tu sistema operativo para que la aplicación intercepte las lecturas sin confundirlas con el teclado estándar.

##### En Windows:
1. Para encontrar el identificador de tu escáner, ejecuta el modo de prueba/inicialización:
   ```bash
   python main.py --init
   ```
   *(También puedes usar `python main.py --debug` para entrar al menú interactivo de hardware)*
2. Presiona el gatillo del escáner o teclea en él. La consola imprimirá un identificador (ej. `\\?\HID#VID_XXXX&PID_XXXX...`).
3. Copia ese identificador y pégalo en tu archivo `.env` en la variable `QR_DEVICE_ID`.

##### En Linux (Debian/Ubuntu):
En Linux se requiere acceso directo a los eventos del hardware (mediante `evdev`). Por defecto, los usuarios regulares no tienen este permiso.

1. **Otorgar Permisos de Lectura:** Añade tu usuario al grupo `input` ejecutando este comando en la terminal:
   ```bash
   sudo usermod -aG input $USER
   ```
2. **Aplicar los Cambios (¡Crítico!):** Para que los permisos surtan efecto de forma permanente, debes **reiniciar tu computadora** (o cerrar tu sesión de usuario y volver a entrar).
   *(Alternativa temporal: Si deseas probar inmediatamente sin reiniciar, ejecuta el comando `newgrp input` en tu terminal activa, y lanza tu aplicación desde esa misma ventana).*
3. **Identificar el Dispositivo:** Una vez que tengas los permisos aplicados, ejecuta el modo de detección:
   ```bash
   python3 main.py --init
   ```
   *(También puedes usar `python3 main.py --debug`)*
4. Aparecerá una lista de dispositivos. El script automáticamente intentará mostrar la ruta persistente (ej. `/dev/input/by-id/usb-Wireless...-event-kbd`).
5. Copia esa ruta (la que dice `Device Path`) y pégala en tu archivo `.env` en la variable `QR_DEVICE_ID`.

#### Configuración de la Cámara

Para que el sistema de ráfaga de imágenes funcione correctamente cuando se detecta un vehículo:

1. Ejecuta el modo de depuración interactivo:
   ```bash
   python main.py --debug
   ```
2. Selecciona la opción **2. Identificar y probar Cámaras**.
3. Sigue las instrucciones en pantalla. El sistema listará las cámaras disponibles e intentará abrirlas para que puedas identificar visualmente cuál es la correcta. (Presiona `q` para cerrar la ventana de prueba).
4. Configura tu `.env` con los parámetros deseados, por ejemplo:
   ```env
   CAMERA_INDEX=0
   CAMERA_BURST_COUNT=3
   CAMERA_BURST_DELAY=1.0
   CAMERA_SAVE_PATH=./storage/camera
   ```

#### Iniciar la Aplicación Principal
Una vez configurado el `.env`, para iniciar la aplicación con todos sus hilos corriendo en paralelo (IA e Interceptor QR), simplemente ejecuta:

```bash
python main.py
```

### 7. Entorno de Desarrollo (Visual Studio Code)

Este repositorio incluye configuraciones predeterminadas para Visual Studio Code dentro del directorio `.vscode`.

- **Intérprete de Python:** VSCode está configurado para detectar automáticamente el entorno virtual ubicado en `.venv`.
- **Variables de Entorno:** El archivo `.vscode/settings.json` indica al editor que cargue automáticamente las variables desde el archivo `.env`.
- **Depuración (Debugging):** Puede utilizar la tecla `F5` para iniciar la ejecución con el depurador directamente sobre el archivo actual, gracias a la configuración establecida en `.vscode/launch.json`.
