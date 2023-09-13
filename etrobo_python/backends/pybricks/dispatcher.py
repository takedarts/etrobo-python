import time

from pybricks.hubs import EV3Brick

from etrobo_python.device import Device
from etrobo_python.log import LogWriter

try:
    from typing import Any, Callable, List, Optional, Tuple
except BaseException:
    pass


ev3 = EV3Brick()


def create_dispatcher(
    devices: List[Tuple[str, Device]],
    handlers: List[Callable[..., None]],
    interval: float = 0.01,
    logfile: Optional[str] = None,
    **kwargs,
) -> Any:
    return Dispatcher(
        devices=devices,
        handlers=handlers,
        interval=interval,
        logfile=logfile,
    )


class Dispatcher(object):
    def __init__(
        self,
        devices: List[Tuple[str, Device]],
        handlers: List[Callable[..., None]],
        interval: float,
        logfile: Optional[str],
    ) -> None:
        self.devices = devices
        self.handlers = handlers
        self.interval = interval
        self.logfile = logfile

    def dispatch(self) -> None:
        variables = {name: device for name, device in self.devices}
        previous_time = 0

        writer = None
        if self.logfile is not None:
            writer = LogWriter(self.logfile, self.devices)

        try:
            while True:
                interval_time = int(self.interval * 1000)
                current_time = int(time.time() * 1000)
                process_time = (current_time // interval_time) * interval_time

                if process_time == previous_time:
                    next_time = previous_time + interval_time
                    time.sleep((next_time - current_time) * 0.001)
                    continue

                previous_time = process_time

                for handler in self.handlers:
                    handler(**variables)

                if writer is not None:
                    writer.write([device for _, device in self.devices])
        except StopIteration:
            print('Stopped by handler.')

        if writer is not None:
            writer.close()
