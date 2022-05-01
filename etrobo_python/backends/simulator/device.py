from typing import Any, Tuple

import etrobo_python
from . import connector


def create_device(device_type: str, port: str) -> Any:
    if device_type == 'hub':
        return Hub()
    elif device_type == 'motor':
        return Motor(get_ev3port(port))
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


def get_ev3port(port: str) -> int:
    port_names = ('A', 'B', 'C', 'D', '1', '2', '3', '4')
    port_values = (0, 1, 2, 3, -1, -1, -1, -1)

    if port in port_names:
        return port_values[port_names.index(port)]
    else:
        raise Exception(f'Unknown port: {port}')


class Hub(object):
    def __init__(self):
        self.hub = connector.Hub()

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
        pass

    def set_speaker_volume(self, volume: int) -> None:
        pass


class Motor(etrobo_python.Motor):
    def __init__(self, port: int) -> None:
        self.motor = connector.Motor(port)

    def get_count(self) -> int:
        return self.motor.get_count()

    def reset_count(self) -> None:
        self.motor.reset_count()

    def set_power(self, power: int) -> None:
        self.motor.set_pwm(power)

    def set_brake(self, brake: bool) -> None:
        self.motor.set_brake(brake)


class ColorSensor(etrobo_python.ColorSensor):
    def __init__(self) -> None:
        self.color_sensor = connector.ColorSensor()

    def get_brightness(self) -> int:
        return self.color_sensor.get_brightness()

    def get_ambient(self) -> int:
        return self.color_sensor.get_ambient()

    def get_raw_color(self) -> Tuple[int, int, int]:
        return self.color_sensor.get_raw_color()


class TouchSensor(etrobo_python.TouchSensor):
    def __init__(self) -> None:
        self.touch_sensor = connector.TouchSensor()

    def is_pressed(self) -> bool:
        return self.touch_sensor.is_pressed()


class SonarSensor(etrobo_python.SonarSensor):
    def __init__(self) -> None:
        self.sonar_sensor = connector.SonarSensor()

    def listen(self) -> bool:
        return self.sonar_sensor.listen()

    def get_distance(self) -> int:
        return self.sonar_sensor.get_distance()


class GyroSensor(object):
    def __init__(self) -> None:
        self.gyro_sensor = connector.GyroSensor()

    def reset(self) -> None:
        self.gyro_sensor.reset()

    def get_angle(self) -> int:
        return self.gyro_sensor.get_angle()

    def get_angler_velocity(self) -> int:
        return self.gyro_sensor.get_angler_velocity()
