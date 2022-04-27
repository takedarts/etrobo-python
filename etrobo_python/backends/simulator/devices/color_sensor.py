from typing import Any, Tuple

import etrobosim.ev3api as ev3
from etrobo_python import ColorSensor

from .util import get_ev3port


class ColorSensorImpl(ColorSensor):
    def __init__(self, port: str) -> None:
        self.color_sensor = ev3.ColorSensor(get_ev3port(port))

    def ev3device(self) -> Any:
        return self.color_sensor

    def get_brightness(self) -> int:
        return self.color_sensor.getBrightness()

    def get_raw_color(self) -> Tuple[int, int, int]:
        return self.color_sensor.getRawColor()
