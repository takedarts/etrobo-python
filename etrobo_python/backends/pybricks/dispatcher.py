import time

from pybricks.hubs import EV3Brick

try:
    from typing import Any, Callable, List, Tuple
except BaseException:
    pass


ev3 = EV3Brick()


def create_dispatcher(
    devices: List[Tuple[str, Any]],
    handlers: List[Callable[..., None]],
    interval: float = 0.01,
    **kwargs,
) -> Any:
    return Dispatcher(
        devices=devices,
        handlers=handlers,
        interval=interval)


class Dispatcher(object):
    def __init__(
        self,
        devices: List[Tuple[str, Any]],
        handlers: List[Callable[..., None]],
        interval: float = 0.01,
    ) -> None:
        self.devices = devices
        self.handlers = handlers
        self.interval = interval

    def dispatch(self) -> None:
        variables = {name: device for name, device in self.devices}
        previous_time = 0

        while True:
            current_time = round(time.time() * 1000)
            process_time = current_time // round(self.interval * 1000)

            if process_time == previous_time:
                time.sleep(self.interval * 0.1)
                continue

            previous_time = process_time

            for handler in self.handlers:
                handler(**variables)
