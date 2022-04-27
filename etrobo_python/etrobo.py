from typing import Any, Callable, List, Tuple


class ETRobo(object):
    def __init__(self, backend: str) -> None:
        if backend == 'simulator':
            from .backends import simulator
            self.backend: Any = simulator
        else:
            raise NotImplementedError(f'Unsupported backend: {backend}')

        self.devices: List[Tuple[str, Any]] = []
        self.handlers: List[Callable[..., None]] = []

    def add_device(self, name: str, device_type: str, port: str) -> 'ETRobo':
        device = self.backend.create_device(device_type, port)
        self.devices.append((name, device))
        return self

    def add_handler(self, func: Callable[..., None]) -> 'ETRobo':
        self.handlers.append(func)
        return self

    def dispatch(self, **kwargs) -> None:
        self.backend.create_dispatcher(
            devices=self.devices,
            handlers=self.handlers,
            **kwargs,
        ).dispatch()
