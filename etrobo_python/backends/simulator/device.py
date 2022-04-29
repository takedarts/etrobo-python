from typing import Any, Tuple

import etrobo_python
from . import connector


def create_device(device_type: str, port: str) -> Any:
    ev3port = get_ev3port(port)

    if device_type == 'motor':
        return Motor(ev3port)
    elif device_type == 'color_sensor':
        return ColorSensor(ev3port)
    elif device_type == 'touch_sensor':
        return TouchSensor(ev3port)
    elif device_type == 'sonar_sensor':
        return SonarSensor(ev3port)
    else:
        raise NotImplementedError(f'Unsupported device: {device_type}')


def get_ev3port(port: str) -> int:
    port_names = ('A', 'B', 'C', 'D', '1', '2', '3', '4')
    port_values = (0, 1, 2, 3, -1, -1, -1, -1)

    if port in port_names:
        return port_values[port_names.index(port)]
    else:
        raise Exception(f'Unknown port: {port}')


class Motor(etrobo_python.Motor):
    def __init__(self, port: int) -> None:
        self.motor = connector.Motor(port)

    def get_count(self) -> int:
        return self.motor.get_count()

    def set_pwm(self, pwm: int) -> None:
        self.motor.set_pwm(pwm)

    def set_brake(self, brake: bool) -> None:
        self.motor.set_brake(brake)


class ColorSensor(etrobo_python.ColorSensor):
    def __init__(self, port: int) -> None:
        self.color_sensor = connector.ColorSensor()

    def get_brightness(self) -> int:
        return self.color_sensor.get_brightness()

    def get_raw_color(self) -> Tuple[int, int, int]:
        return self.color_sensor.get_raw_color()


class TouchSensor(etrobo_python.TouchSensor):
    def __init__(self, port: int) -> None:
        self.touch_sensor = connector.TouchSensor()

    def is_pressed(self) -> bool:
        return self.touch_sensor.is_pressed()


class SonarSensor(etrobo_python.SonarSensor):
    def __init__(self, port: int) -> None:
        self.sonar_sensor = connector.SonarSensor()

    def listen(self) -> bool:
        return self.sonar_sensor.listen()

    def get_distance(self) -> int:
        return self.sonar_sensor.get_distance()
