try:
    from typing import Any, Callable, List, Tuple
except BaseException:
    pass


class ETRobo(object):
    def __init__(self, backend: str) -> None:
        if backend == 'simulator':
            from .backends import simulator
            self.backend = simulator  # type: Any
        elif backend == 'pybricks':
            from .backends import pybricks
            self.backend = pybricks
        else:
            raise NotImplementedError(
                'Unsupported backend: {}'.format(backend))

        self.devices = []  # type: List[Tuple[str, Any]]
        self.handlers = []  # type: List[Callable[..., None]]

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
