# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
