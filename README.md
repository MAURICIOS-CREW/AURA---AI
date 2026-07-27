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

Para iniciar la aplicación principal, ejecute el siguiente comando:

```bash
python main.py
```

### 7. Entorno de Desarrollo (Visual Studio Code)

Este repositorio incluye configuraciones predeterminadas para Visual Studio Code dentro del directorio `.vscode`.

- **Intérprete de Python:** VSCode está configurado para detectar automáticamente el entorno virtual ubicado en `.venv`.
- **Variables de Entorno:** El archivo `.vscode/settings.json` indica al editor que cargue automáticamente las variables desde el archivo `.env`.
- **Depuración (Debugging):** Puede utilizar la tecla `F5` para iniciar la ejecución con el depurador directamente sobre el archivo actual, gracias a la configuración establecida en `.vscode/launch.json`.
