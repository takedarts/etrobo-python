import etrobo_python

import pybricks.ev3devices as ev3dev
from pybricks.parameters import Port

try:
    from typing import Any, Tuple
except BaseException:
    pass


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
        raise NotImplementedError(
            'Unsupported device: {}'.format(device_type))


def get_ev3port(port: str) -> Port:
    port_names = ('A', 'B', 'C', 'D', '1', '2', '3', '4')
    port_values = (Port.A, Port.B, Port.C, Port.D,
                   Port.S1, Port.S2, Port.S3, Port.S4)

    if port in port_names:
        return port_values[port_names.index(port)]
    else:
        raise Exception('Unknown port: {}'.format(port))


class Motor(etrobo_python.Motor):
    def __init__(self, port: Port) -> None:
        self.motor = ev3dev.Motor(port)

    def get_count(self) -> int:
        return self.motor.angle()

    def set_pwm(self, pwm: int) -> None:
        self.motor.run(pwm)

    def set_brake(self, brake: bool) -> None:
        if brake:
            self.motor.brake()


class ColorSensor(etrobo_python.ColorSensor):
    def __init__(self, port: Port) -> None:
        self.color_sensor = ev3dev.ColorSensor(port)

    def get_brightness(self) -> int:
        return self.color_sensor.reflection()

    def get_raw_color(self) -> Tuple[int, int, int]:
        return self.color_sensor.rgb()


class TouchSensor(etrobo_python.TouchSensor):
    def __init__(self, port: Port) -> None:
        self.touch_sensor = ev3dev.TouchSensor(port)

    def is_pressed(self) -> bool:
        return self.touch_sensor.pressed()


class SonarSensor(etrobo_python.SonarSensor):
    def __init__(self, port: Port) -> None:
        self.sonar_sensor = ev3dev.UltrasonicSensor(port)

    def listen(self) -> bool:
        return self.sonar_sensor.presence()

    def get_distance(self) -> int:
        return self.sonar_sensor.distance()
