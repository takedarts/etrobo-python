from typing import Any, Tuple

import etrobo_python
from . import connector

try:
    import os
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
    import pygame
    pygame.mixer.init(frequency=44100, channels=1)
except ImportError:
    pygame = None  # type: ignore

try:
    import numpy as np
except ImportError:
    np = None  # type: ignore


def create_device(device_type: str, port: str) -> Any:
    if device_type == 'hub':
        return Hub()
    elif device_type == 'motor':
        return Motor(get_sim_port(port))
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


def get_sim_port(port: str) -> int:
    port_names = ('A', 'B', 'C', 'D', '1', '2', '3', '4')
    port_values = (0, 1, 2, 3, -1, -1, -1, -1)

    if port in port_names:
        return port_values[port_names.index(port)]
    else:
        raise Exception(f'Unknown port: {port}')


def play_beep_sound(freq: float, duration: float, volume: float) -> None:
    if pygame is None or np is None:
        return

    sr = 44100
    length = int(sr * duration)
    wave = np.sin(np.arange(length) * freq * np.pi * 2 / sr) * volume
    wave = (wave * 32767).astype(np.int16)
    sound = pygame.sndarray.make_sound(wave.astype(np.int16))
    sound.play()


class Hub(etrobo_python.Hub):
    def __init__(self):
        self.hub = connector.Hub()
        self.volume = 1.0
        self.log = bytearray(5)

    def set_led(self, color: str) -> None:
        color_value = color.lower()[0]
        color_names = ('b', 'r', 'g', 'o')

        if color_value in color_names:
            self.hub.set_led(color_names.index(color_value))
        else:
            self.hub.set_led(0)

    def get_time(self) -> float:
        return self.hub.get_time()

    def get_battery_voltage(self) -> int:
        return 8000

    def get_battery_current(self) -> int:
        return 200

    def play_speaker_tone(self, frequency: int, duration: float) -> None:
        play_beep_sound(frequency, duration, self.volume)

    def set_speaker_volume(self, volume: int) -> None:
        self.volume = min(max(volume / 100, 0.0), 1.0)

    def is_left_button_pressed(self) -> bool:
        return (self.hub.get_button_pressed() & 0x01) != 0

    def is_right_button_pressed(self) -> bool:
        return (self.hub.get_button_pressed() & 0x02) != 0

    def is_up_button_pressed(self) -> bool:
        return (self.hub.get_button_pressed() & 0x04) != 0

    def is_down_button_pressed(self) -> bool:
        return (self.hub.get_button_pressed() & 0x08) != 0

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
        return self.sonar_sensor.get_distance()

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
