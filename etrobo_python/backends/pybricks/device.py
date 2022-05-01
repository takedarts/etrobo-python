import time

import etrobo_python

import pybricks.ev3devices as ev3dev
import pybricks.hubs as hubs
from pybricks.parameters import Port, Color

try:
    from typing import Any, Tuple
except BaseException:
    pass


def create_device(device_type: str, port: str) -> Any:
    if device_type == 'hub':
        return Hub()

    ev3port = get_ev3port(port)

    if device_type == 'motor':
        return Motor(ev3port)
    elif device_type == 'color_sensor':
        return ColorSensor(ev3port)
    elif device_type == 'touch_sensor':
        return TouchSensor(ev3port)
    elif device_type == 'sonar_sensor':
        return SonarSensor(ev3port)
    elif device_type == 'gyro_sensor':
        return GyroSensor(ev3port)
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


class Hub(object):
    def __init__(self) -> None:
        self.ev3brick = hubs.EV3Brick()

    def set_led(self, color: str) -> None:
        color_value = color.lower()[0]
        if color_value == 'r':
            self.ev3brick.light.on(Color.RED)
        elif color_value == 'g':
            self.ev3brick.light.on(Color.GREEN)
        elif color_value == 'o':
            self.ev3brick.light.on(Color.ORANGE)
        else:
            self.ev3brick.light.on(Color.BLACK)

    def get_time(self) -> float:
        return time.time()

    def get_battery_voltage(self) -> int:
        return self.ev3brick.battery.voltage()

    def get_battery_current(self) -> int:
        return self.ev3brick.battery.current()

    def play_speaker_tone(self, frequency: int, duration: float) -> None:
        self.ev3brick.speaker.beep(frequency, round(duration * 1000))

    def set_speaker_volume(self, volume: int) -> None:
        self.ev3brick.speaker.set_volume(volume)


class Motor(etrobo_python.Motor):
    def __init__(self, port: Port) -> None:
        self.motor = ev3dev.Motor(port)

    def get_count(self) -> int:
        return self.motor.angle()

    def reset_count(self) -> None:
        self.motor.reset_angle(0)

    def set_power(self, power: int) -> None:
        self.motor.run(power)

    def set_brake(self, brake: bool) -> None:
        if brake:
            self.motor.brake()


class ColorSensor(etrobo_python.ColorSensor):
    def __init__(self, port: Port) -> None:
        self.color_sensor = ev3dev.ColorSensor(port)

    def get_brightness(self) -> int:
        return self.color_sensor.reflection()

    def get_ambient(self) -> int:
        return self.color_sensor.ambient()

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


class GyroSensor(object):
    def __init__(self, port: Port) -> None:
        self.gyro_sensor = ev3dev.GyroSensor(port)

    def reset(self) -> None:
        self.gyro_sensor.reset_angle(0)

    def get_angle(self) -> int:
        return self.gyro_sensor.angle()

    def get_angler_velocity(self) -> int:
        return self.gyro_sensor.speed()
