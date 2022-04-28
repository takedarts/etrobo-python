from etrobo_python import ColorSensor, Motor, TouchSensor

import pybricks.ev3devices as ev3dev
from pybricks.parameters import Port

try:
    from typing import Any, Tuple
except BaseException:
    pass


def create_device(device_type: str, port: str) -> Any:
    ev3port = get_ev3port(port)

    if device_type == 'motor':
        return MotorImpl(ev3port)
    elif device_type == 'color_sensor':
        return ColorSensorImpl(ev3port)
    elif device_type == 'touch_sensor':
        return TouchSensorImpl(ev3port)
    else:
        raise NotImplementedError(
            'Unsupported device: {}'.format(device_type))


def get_ev3port(port: str) -> Port:
    if port == 'A':
        return Port.A
    elif port == 'B':
        return Port.B
    elif port == 'C':
        return Port.C
    elif port == 'D':
        return Port.D
    elif port == '1':
        return Port.S1
    elif port == '2':
        return Port.S2
    elif port == '3':
        return Port.S3
    elif port == '4':
        return Port.S4
    else:
        raise Exception('Unknown port: {}'.format(port))


class MotorImpl(Motor):
    def __init__(self, port: Port) -> None:
        self.motor = ev3dev.Motor(port)

    def set_pwm(self, pwm: int) -> None:
        self.motor.run(pwm)

    def set_brake(self, brake: bool) -> None:
        if brake:
            self.motor.brake()


class ColorSensorImpl(ColorSensor):
    def __init__(self, port: Port) -> None:
        self.color_sensor = ev3dev.ColorSensor(port)

    def get_brightness(self) -> int:
        return self.color_sensor.reflection()

    def get_raw_color(self) -> Tuple[int, int, int]:
        return self.color_sensor.rgb()


class TouchSensorImpl(TouchSensor):
    def __init__(self, port: Port) -> None:
        self.touch_sensor = ev3dev.TouchSensor(port)

    def is_pressed(self) -> bool:
        return self.touch_sensor.pressed()
