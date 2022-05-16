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
        interval: float,
    ) -> None:
        self.devices = devices
        self.handlers = handlers
        self.interval = interval

    def dispatch(self) -> None:
        variables = {name: device for name, device in self.devices}
        previous_time = 0

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
        except StopIteration:
            print('Stopped by handler.')
