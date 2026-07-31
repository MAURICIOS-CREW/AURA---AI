# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.2]
### Added
- Sistema de mensajería interno mediante un Bus de Eventos (`EventBus`) para lograr una arquitectura desacoplada entre componentes.
- Componente `SerialController` que corre en su propio hilo para manejar la comunicación asíncrona con dispositivos de hardware (ej. microcontrolador ESP32) vía puerto serial.
- Script `serial_debug.py` para facilitar pruebas directas y depuración de comandos con el puerto serial.
- Dependencia `pyserial` agregada al archivo `requirements.txt`.

### Changed
- Modificado `QRInterceptor` para aceptar una instancia de `EventBus` e inyectarle la capacidad de publicar un evento `ACCESS_GRANTED` de manera global al ocurrir una validación exitosa.
- Archivo `main.py` actualizado para orquestar los nuevos flujos, inicializar el controlador serial y suscribirse a los eventos del escáner para enviar automáticamente el comando `OPEN` a la pluma/puerta.
- Se agregaron las configuraciones base `SERIAL_PORT` y `SERIAL_BAUDRATE` al archivo `.env.example`.

## [0.1.1] - 2026-07-27
### Added
- Documentación detallada en el `README.md` sobre la configuración y asignación de permisos (grupo `input`) para el interceptor QR en Linux.
- Logs de depuración de estado HTTP y texto crudo en `api/client.py` para visualizar fácilmente respuestas de error desde el servidor.

### Changed
- Mejorado el modo de detección de hardware en Linux (`--init`) para que resuelva y muestre automáticamente rutas persistentes (`/dev/input/by-id/`) en lugar de descriptores volátiles (`eventX`).

### Fixed
- Soporte para mayúsculas en `LinuxQRStrategy` interceptando y manteniendo el estado de las teclas `SHIFT` (izquierdo y derecho) enviadas por los lectores de códigos de barras/QR.
- Añadida compatibilidad con la tecla `KEY_END` como señal de finalización y envío de código en `LinuxQRStrategy`, soportando lectores configurados con este sufijo en lugar de `Enter`.
- Corrección de la ruta del endpoint en el cliente API apuntando ahora a `/api/access/qr` en lugar de la ruta incorrecta.
- Resolución de un error de respuesta del backend (HTTP 400 Bad Request) añadiendo el header requerido `Accept: application/json` en las peticiones HTTP del cliente.

## [0.1.0] - 2026-07-27

### Added
- Arquitectura multi-hilo en `main.py` permitiendo la ejecución concurrente e independiente de `AIModule` y `QRInterceptor`.
- Soporte de intercepción de hardware multiplataforma usando el Patrón Estrategia (Strategy Pattern) en `core/qr`.
- Implementación de `LinuxQRStrategy` utilizando `evdev` para capturar y bloquear (grab) la entrada del escáner exclusivamente en Linux.
- Implementación de `WindowsQRStrategy` utilizando `win-raw-in` y ventanas ocultas de `tkinter` para entornos Windows.
- Modos de detección de hardware (`--init` / `--test`) para identificar las rutas de dispositivo (Device Paths) de escáneres específicos en ambos sistemas operativos.

### Changed
- Actualización de `requirements.txt` con marcadores de entorno (`sys_platform`) para la instalación dinámica de `evdev` (solo Linux) y `win-raw-in` (solo Windows).

### Fixed
- Parche en tiempo de ejecución (monkey-patch) en `core/qr/windows_qr.py` para solucionar un *crash* interno de la librería `win-raw-in` al leer formatos de dispositivo no estándar.
- Solución al bloqueo de `KeyboardInterrupt` (Ctrl+C) en el modo de detección de hardware en Windows mediante la inyección de ciclos de respiro con `root.after()` en `tkinter`.
