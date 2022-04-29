from typing import Any, Tuple

from etrobo_python import ColorSensor, Motor, TouchSensor

from . import connector


def create_device(device_type: str, port: str) -> Any:
    ev3port = get_ev3port(port)

    if device_type == 'motor':
        return MotorImpl(ev3port)
    elif device_type == 'color_sensor':
        return ColorSensorImpl(ev3port)
    elif device_type == 'touch_sensor':
        return TouchSensorImpl(ev3port)
    else:
        raise NotImplementedError(f'Unsupported device: {device_type}')


def get_ev3port(port: str) -> int:
    if port in ('A', 'B', 'C', 'D'):
        return ('A', 'B', 'C', 'D').index(port)
    if port in ('1', '2', '3', '4'):
        return -1
    else:
        raise Exception(f'Unknown port: {port}')


class MotorImpl(Motor):
    def __init__(self, port: int) -> None:
        self.motor = connector.Motor(port)

    def set_pwm(self, pwm: int) -> None:
        self.motor.set_pwm(pwm)

    def set_brake(self, brake: bool) -> None:
        self.motor.set_brake(brake)


class ColorSensorImpl(ColorSensor):
    def __init__(self, port: int) -> None:
        self.color_sensor = connector.ColorSensor()

    def get_brightness(self) -> int:
        return self.color_sensor.get_brightness()

    def get_raw_color(self) -> Tuple[int, int, int]:
        return self.color_sensor.get_raw_color()


class TouchSensorImpl(TouchSensor):
    def __init__(self, port: int) -> None:
        self.touch_sensor = connector.TouchSensor()

    def is_pressed(self) -> bool:
        return self.touch_sensor.is_pressed()
