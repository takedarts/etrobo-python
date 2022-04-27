import traceback
from typing import Any, Callable, List, Tuple

import etrobosim as ets


def create_dispatcher(
    devices: List[Tuple[str, Any]],
    handlers: List[Callable[..., None]],
    **kwargs,
) -> Any:
    return Dispatcher(
        devices=devices,
        handlers=handlers,
        **kwargs)


class Dispatcher(object):
    def __init__(
        self,
        devices: List[Tuple[str, Any]],
        handlers: List[Callable[..., None]],
        course: str,
        debug: bool = False,
    ) -> None:
        self.devices = devices
        self.handlers = handlers
        self.course = course
        self.debug = debug

    def dispatch(self) -> None:
        if self.course == 'right':
            course = ets.Course.RIGHT
        else:
            course = ets.Course.LEFT

        devices = [device.ev3device() for _, device in self.devices]
        variables = {name: device for name, device in self.devices}

        def runner():
            try:
                for handler in self.handlers:
                    handler(**variables)
            except BaseException:
                traceback.print_exc()

        try:
            controller = ets.Controller(course)
            controller.addHandlers(devices)
            controller.start(debug=True)
            controller.runCyclic(runner)
            controller.exit_process()
        except KeyboardInterrupt:
            controller.exit_process()
