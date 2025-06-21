from typing import Any, Callable, List, Optional, Tuple

from etrobo_python.device import Device
from etrobo_python.log import LogWriter

from .connector import Connector


def create_dispatcher(
    devices: List[Tuple[str, Device]],
    handlers: List[Callable[..., None]],
    port: str = '/dev/USB_SPIKE',
    interval: float = 0.04,
    logfile: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    return Dispatcher(
        devices=devices,
        handlers=handlers,
        port=port,
        interval=interval,
        logfile=logfile,
    )


class Dispatcher(object):
    def __init__(
        self,
        devices: List[Tuple[str, Device]],
        handlers: List[Callable[..., None]],
        interval: float,
        port: str,
        logfile: Optional[str],
    ) -> None:
        self.devices = devices
        self.handlers = handlers
        self.interval = interval
        self.port = port
        self.logfile = logfile
        self.terminated = False

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

        Connector(
            handler=run_handlers,
            interval=self.interval,
            port=self.port,
        ).run()

        if writer is not None:
            writer.close()
