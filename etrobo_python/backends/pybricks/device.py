import time

import pybricks.ev3devices as ev3dev
import pybricks.hubs as hubs
from pybricks.parameters import Button, Color, Port

import etrobo_python

try:
    from typing import Any, Tuple
except BaseException:
    pass


def create_device(device_type: str, port: str) -> Any:
    if device_type == 'hub':
        return Hub()

    ev3_port = get_ev3_port(port)

    if device_type == 'motor':
        return Motor(ev3_port)
    elif device_type == 'color_sensor':
        return ColorSensor(ev3_port)
    elif device_type == 'touch_sensor':
        return TouchSensor(ev3_port)
    elif device_type == 'sonar_sensor':
        return SonarSensor(ev3_port)
    elif device_type == 'gyro_sensor':
        return GyroSensor(ev3_port)
    else:
        raise NotImplementedError(
            'Unsupported device: {}'.format(device_type))


def get_ev3_port(port: str) -> Port:
    port_names = ('A', 'B', 'C', 'D', '1', '2', '3', '4')
    port_values = (Port.A, Port.B, Port.C, Port.D,
                   Port.S1, Port.S2, Port.S3, Port.S4)

    if port in port_names:
        return port_values[port_names.index(port)]
    else:
        raise Exception('Unknown port: {}'.format(port))


class Hub(etrobo_python.Hub):
    def __init__(self) -> None:
        self.ev3brick = hubs.EV3Brick()
        self.base_time = time.time()
        self.log = bytearray(5)

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
        return time.time() - self.base_time

    def get_battery_voltage(self) -> int:
        return self.ev3brick.battery.voltage()

    def get_battery_current(self) -> int:
        return self.ev3brick.battery.current()

    def play_speaker_tone(self, frequency: int, duration: float) -> None:
        self.ev3brick.speaker.beep(frequency, round(duration * 1000))

    def set_speaker_volume(self, volume: int) -> None:
        self.ev3brick.speaker.set_volume(volume)

    def is_left_button_pressed(self) -> bool:
        return Button.LEFT in self.ev3brick.buttons.pressed()

    def is_right_button_pressed(self) -> bool:
        return Button.RIGHT in self.ev3brick.buttons.pressed()

    def is_up_button_pressed(self) -> bool:
        return Button.UP in self.ev3brick.buttons.pressed()

    def is_down_button_pressed(self) -> bool:
        return Button.DOWN in self.ev3brick.buttons.pressed()

    def get_log(self) -> bytes:
        self.log[:4] = int.to_bytes(int(self.get_time() * 1000), 4, 'big')
        self.log[4] = (
            int(self.is_left_button_pressed())
            | int(self.is_right_button_pressed()) << 1
            | int(self.is_up_button_pressed()) << 2
            | int(self.is_down_button_pressed()) << 3
        )

        return self.log


class Motor(etrobo_python.Motor):
    def __init__(self, port: Port) -> None:
        self.motor = ev3dev.Motor(port)
        self.log = bytearray(4)

    def get_count(self) -> int:
        return self.motor.angle()

    def reset_count(self) -> None:
        self.motor.reset_angle(0)

    def set_power(self, power: int) -> None:
        self.motor.run(power)

    def set_brake(self, brake: bool) -> None:
        if brake:
            self.motor.brake()

    def get_log(self) -> bytes:
        self.log[:] = int.to_bytes(self.get_count() & 0xffffffff, 4, 'big')
        return self.log


class ColorSensor(etrobo_python.ColorSensor):
    def __init__(self, port: Port) -> None:
        self.color_sensor = ev3dev.ColorSensor(port)
        self.mode = -1
        self.log = bytearray(5)

    def get_brightness(self) -> int:
        self.mode = 0
        return self.color_sensor.reflection()

    def get_ambient(self) -> int:
        self.mode = 1
        return self.color_sensor.ambient()

    def get_raw_color(self) -> Tuple[int, int, int]:
        self.mode = 2
        return self.color_sensor.rgb()

    def get_log(self) -> bytes:
        if self.mode == 0:
            self.log[0] = self.get_brightness()
            self.log[1] = 0
            self.log[2], self.log[3], self.log[4] = 0, 0, 0
        elif self.mode == 1:
            self.log[0] = 0
            self.log[1] = self.get_ambient()
            self.log[2], self.log[3], self.log[4] = 0, 0, 0
        elif self.mode == 2:
            self.log[0] = 0
            self.log[1] = 0
            self.log[2], self.log[3], self.log[4] = self.get_raw_color()

        return self.log


class TouchSensor(etrobo_python.TouchSensor):
    def __init__(self, port: Port) -> None:
        self.touch_sensor = ev3dev.TouchSensor(port)
        self.log = bytearray(1)

    def is_pressed(self) -> bool:
        return self.touch_sensor.pressed()

    def get_log(self) -> bytes:
        self.log[0] = int(self.is_pressed())
        return self.log


class SonarSensor(etrobo_python.SonarSensor):
    def __init__(self, port: Port) -> None:
        self.sonar_sensor = ev3dev.UltrasonicSensor(port)
        self.log = bytearray(2)

    def listen(self) -> bool:
        return self.sonar_sensor.presence()

    def get_distance(self) -> int:
        return self.sonar_sensor.distance()

    def get_log(self) -> bytes:
        self.log[:] = int.to_bytes(self.get_distance(), 2, 'big')
        return self.log


class GyroSensor(etrobo_python.GyroSensor):
    def __init__(self, port: Port) -> None:
        self.gyro_sensor = ev3dev.GyroSensor(port)
        self.log = bytearray(4)

    def reset(self) -> None:
        self.gyro_sensor.reset_angle(0)

    def get_angle(self) -> int:
        return self.gyro_sensor.angle()

    def get_angler_velocity(self) -> int:
        return self.gyro_sensor.speed()

    def get_log(self) -> bytes:
        self.log[:2] = int.to_bytes(self.get_angle() & 0xffff, 2, 'big')
        self.log[2:] = int.to_bytes(self.get_angler_velocity() & 0xffff, 2, 'big')
        return self.log
