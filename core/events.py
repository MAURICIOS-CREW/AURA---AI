class EventBus:
    """
    Bus de eventos centralizado (Pub/Sub) para la comunicación entre hilos.
    Permite desacoplar los componentes (QR, IA, Serial) para que no necesiten
    conocerse entre sí.
    """
    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event_type: str, callback):
        """Añade un listener para un tipo de evento específico."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        if callback not in self._subscribers[event_type]:
            self._subscribers[event_type].append(callback)

    def publish(self, event_type: str, *args, **kwargs):
        """Emite un evento a todos los listeners suscritos."""
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    print(f"[EventBus] Error ejecutando callback para {event_type}: {e}")
