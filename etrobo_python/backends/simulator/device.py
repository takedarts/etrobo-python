from typing import Any, Tuple

import etrobosim.ev3api as ev3
from etrobo_python import ColorSensor, Motor, TouchSensor


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
    if port == 'A':
        return ev3.ePortM.PORT_A
    elif port == 'B':
        return ev3.ePortM.PORT_B
    elif port == 'C':
        return ev3.ePortM.PORT_C
    elif port == 'D':
        return ev3.ePortM.PORT_D
    elif port == '1':
        return ev3.ePortS.PORT_1
    elif port == '2':
        return ev3.ePortS.PORT_2
    elif port == '3':
        return ev3.ePortS.PORT_3
    elif port == '4':
        return ev3.ePortS.PORT_4
    else:
        raise Exception(f'Unknown port: {port}')


class MotorImpl(Motor):
    def __init__(self, port: int) -> None:
        self.motor = ev3.Motor(port, True, ev3.MotorType.LARGE_MOTOR)
        self.motor.reset()

    def ev3device(self) -> Any:
        return self.motor

    def set_pwm(self, pwm: int) -> None:
        self.motor.setPWM(pwm)

    def set_brake(self, brake: bool) -> None:
        self.motor.setBrake(brake)


class ColorSensorImpl(ColorSensor):
    def __init__(self, port: int) -> None:
        self.color_sensor = ev3.ColorSensor(port)

    def ev3device(self) -> Any:
        return self.color_sensor

    def get_brightness(self) -> int:
        return self.color_sensor.getBrightness()

    def get_raw_color(self) -> Tuple[int, int, int]:
        return self.color_sensor.getRawColor()


class TouchSensorImpl(TouchSensor):
    def __init__(self, port: int) -> None:
        self.touch_sensor = ev3.TouchSensor(port)

    def ev3device(self) -> Any:
        return self.touch_sensor

    def is_pressed(self) -> bool:
        return self.touch_sensor.isPressed()
