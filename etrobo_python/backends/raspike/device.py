import time
from typing import Any, Tuple

import etrobo_python

from . import connector


def create_device(device_type: str, port: str) -> Any:
    if device_type == 'hub':
        return Hub()
    elif device_type == 'motor':
        return Motor(get_raspike_port(port))
    elif device_type == 'color_sensor':
        return ColorSensor()
    elif device_type == 'touch_sensor':
        return TouchSensor()
    elif device_type == 'sonar_sensor':
        return SonarSensor()
    elif device_type == 'gyro_sensor':
        return GyroSensor()
    else:
        raise NotImplementedError(f'Unsupported device: {device_type}')


def get_raspike_port(port: str) -> int:
    port_names = ('A', 'B', 'C', 'D', '1', '2', '3', '4')
    port_values = (0, 1, 2, -1, -1, -1, -1, -1)

    if port in port_names:
        return port_values[port_names.index(port)]
    else:
        raise Exception(f'Unknown port: {port}')


class Hub(etrobo_python.Hub):
    def __init__(self):
        self.hub = connector.Hub()
        self.base_time = time.time()
        self.log = bytearray(5)

    def set_led(self, color: str) -> None:
        pass

    def get_time(self) -> float:
        return time.time() - self.base_time

    def get_battery_voltage(self) -> int:
        return self.hub.get_battery_voltage()

    def get_battery_current(self) -> int:
        return self.hub.get_battery_current()

    def play_speaker_tone(self, frequency: int, duration: float) -> None:
        pass

    def set_speaker_volume(self, volume: int) -> None:
        pass

    def is_left_button_pressed(self) -> bool:
        return (self.hub.get_button_pressed() & 0x01) != 0

    def is_right_button_pressed(self) -> bool:
        return (self.hub.get_button_pressed() & 0x02) != 0

    def is_up_button_pressed(self) -> bool:
        return False

    def is_down_button_pressed(self) -> bool:
        return False

    def get_log(self) -> bytes:
        self.log[:4] = int.to_bytes(int(self.get_time() * 1000), 4, 'big')
        self.log[4] = (
            int(self.is_left_button_pressed())
            | int(self.is_right_button_pressed()) << 1
        )

        return self.log


class Motor(etrobo_python.Motor):
    def __init__(self, port: int) -> None:
        self.motor = connector.Motor(port)
        self.log = bytearray(4)

    def get_count(self) -> int:
        return self.motor.get_count()

    def reset_count(self) -> None:
        self.motor.reset_count()

    def set_power(self, power: int) -> None:
        self.motor.set_pwm(power)

    def set_brake(self, brake: bool) -> None:
        self.motor.set_brake(brake)

    def get_log(self) -> bytes:
        self.log[:] = int.to_bytes(self.get_count(), 4, 'big', signed=True)
        return self.log


class ColorSensor(etrobo_python.ColorSensor):
    def __init__(self) -> None:
        self.color_sensor = connector.ColorSensor()
        self.mode = -1
        self.log = bytearray(5)

    def get_brightness(self) -> int:
        self.mode = 0
        return self.color_sensor.get_brightness()

    def get_ambient(self) -> int:
        self.mode = 1
        return self.color_sensor.get_ambient()

    def get_raw_color(self) -> Tuple[int, int, int]:
        self.mode = 2
        return self.color_sensor.get_raw_color()

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
    def __init__(self) -> None:
        self.touch_sensor = connector.TouchSensor()
        self.log = bytearray(1)

    def is_pressed(self) -> bool:
        return self.touch_sensor.is_pressed()

    def get_log(self) -> bytes:
        self.log[0] = int(self.is_pressed())
        return self.log


class SonarSensor(etrobo_python.SonarSensor):
    def __init__(self) -> None:
        self.sonar_sensor = connector.SonarSensor()
        self.log = bytearray(2)

    def listen(self) -> bool:
        return self.sonar_sensor.listen()

    def get_distance(self) -> int:
        distance = self.sonar_sensor.get_distance()
        if 0 <= distance < 255:
            return distance
        else:
            return 255

    def get_log(self) -> bytes:
        self.log[:] = int.to_bytes(self.get_distance(), 2, 'big')
        return self.log


class GyroSensor(etrobo_python.GyroSensor):
    def __init__(self) -> None:
        self.gyro_sensor = connector.GyroSensor()
        self.log = bytearray(4)

    def reset(self) -> None:
        self.gyro_sensor.reset()

    def get_angle(self) -> int:
        return self.gyro_sensor.get_angle()

    def get_angler_velocity(self) -> int:
        return self.gyro_sensor.get_angler_velocity()

    def get_log(self) -> bytes:
        self.log[:2] = int.to_bytes(self.get_angle(), 2, 'big', signed=True)
        self.log[2:] = int.to_bytes(self.get_angler_velocity(), 2, 'big', signed=True)
        return self.log
