from typing import Any, Tuple

import etrobosim.ev3api as ev3
from etrobo_python import ColorSensor, Motor, TouchSensor

from .util import get_ev3port


def create_device(device_type: str, port: str) -> Any:
    if device_type == 'motor':
        return MotorImpl(port)
    elif device_type == 'color_sensor':
        return ColorSensorImpl(port)
    elif device_type == 'touch_sensor':
        return TouchSensorImpl(port)
    else:
        raise NotImplementedError(f'Unsupported device: {device_type}')


class MotorImpl(Motor):
    def __init__(self, port: str) -> None:
        self.motor = ev3.Motor(
            get_ev3port(port), True, ev3.MotorType.LARGE_MOTOR)
        self.motor.reset()

    def ev3device(self) -> Any:
        return self.motor

    def set_pwm(self, pwm: int) -> None:
        self.motor.setPWM(pwm)

    def set_brake(self, brake: bool) -> None:
        self.motor.setBrake(brake)


class ColorSensorImpl(ColorSensor):
    def __init__(self, port: str) -> None:
        self.color_sensor = ev3.ColorSensor(get_ev3port(port))

    def ev3device(self) -> Any:
        return self.color_sensor

    def get_brightness(self) -> int:
        return self.color_sensor.getBrightness()

    def get_raw_color(self) -> Tuple[int, int, int]:
        return self.color_sensor.getRawColor()


class TouchSensorImpl(TouchSensor):
    def __init__(self, port: str) -> None:
        self.touch_sensor = ev3.TouchSensor(get_ev3port(port))

    def ev3device(self) -> Any:
        return self.touch_sensor

    def is_pressed(self) -> bool:
        return self.touch_sensor.isPressed()
