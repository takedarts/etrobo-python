from typing import Any, Callable, List, Tuple

from .connector import connect_spike


def create_dispatcher(
    devices: List[Tuple[str, Any]],
    handlers: List[Callable[..., None]],
    interval: float = 0.01,
    port: str = '/dev/ttyAMA1',
    baudrate: int = 115_200,
    timeout: float = 5.0,
    **kwargs,
) -> Any:
    return Dispatcher(
        devices=devices,
        handlers=handlers,
        interval=interval,
        port=port,
        baudrate=baudrate,
        timeout=timeout,
    )


class Dispatcher(object):
    def __init__(
        self,
        devices: List[Tuple[str, Any]],
        handlers: List[Callable[..., None]],
        interval: float,
        port: str,
        baudrate: int,
        timeout: float,
    ) -> None:
        self.devices = devices
        self.handlers = handlers
        self.interval = interval
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout

    def dispatch(self) -> None:
        variables = {name: device for name, device in self.devices}

        def run_handlers() -> None:
            for handler in self.handlers:
                handler(**variables)

        connect_spike(
            handler=run_handlers,
            interval=self.interval,
            port=self.port,
            baudrate=self.baudrate,
            timeout=self.timeout,
        )
