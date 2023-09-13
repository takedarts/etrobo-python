from typing import Any, Callable, List, Optional, Tuple

from etrobo_python.device import Device
from etrobo_python.log import LogWriter

from .connector import connect_spike


def create_dispatcher(
    devices: List[Tuple[str, Device]],
    handlers: List[Callable[..., None]],
    interval: float = 0.01,
    port: str = '/dev/ttyAMA1',
    baudrate: int = 115_200,
    timeout: float = 5.0,
    logfile: Optional[str] = None,
    **kwargs,
) -> Any:
    return Dispatcher(
        devices=devices,
        handlers=handlers,
        interval=interval,
        port=port,
        baudrate=baudrate,
        timeout=timeout,
        logfile=logfile,
    )


class Dispatcher(object):
    def __init__(
        self,
        devices: List[Tuple[str, Device]],
        handlers: List[Callable[..., None]],
        interval: float,
        port: str,
        baudrate: int,
        timeout: float,
        logfile: Optional[str],
    ) -> None:
        self.devices = devices
        self.handlers = handlers
        self.interval = interval
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.logfile = logfile

    def dispatch(self) -> None:
        variables = {name: device for name, device in self.devices}

        writer: Optional[LogWriter] = None
        if self.logfile is not None:
            writer = LogWriter(self.logfile, self.devices)

        def run_handlers() -> None:
            for handler in self.handlers:
                handler(**variables)

            if writer is not None:
                writer.write([device for _, device in self.devices])

        connect_spike(
            handler=run_handlers,
            interval=self.interval,
            port=self.port,
            baudrate=self.baudrate,
            timeout=self.timeout,
        )

        if writer is not None:
            writer.close()
