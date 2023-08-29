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


class Hub(object):
    def __init__(self):
        self.hub = connector.Hub()

    def set_led(self, color: str) -> None:
        if color.startswith('bla'):  # black
            color_code = 0
        elif color.startswith('p'):  # pink
            color_code = 1
        elif color.startswith('blu'):  # blue
            color_code = 3
        elif color.startswith('g'):  # green
            color_code = 6
        elif color.startswith('y'):  # yellow
            color_code = 7
        elif color.startswith('o'):  # orange
            color_code = 8
        elif color.startswith('r'):  # red
            color_code = 9
        else:
            return

        self.hub.set_led(color_code)

    def get_time(self) -> float:
        return self.hub.get_time() / 1000

    def get_battery_voltage(self) -> int:
        return self.hub.get_battery_voltage()

    def get_battery_current(self) -> int:
        return self.hub.get_battery_current()

    def play_speaker_tone(self, frequency: int, duration: float) -> None:
        pass

    def set_speaker_volume(self, volume: int) -> None:
        pass

    def is_left_button_pressed(self) -> bool:
        return (self.hub.get_button_pressed() & 0x02) != 0

    def is_right_button_pressed(self) -> bool:
        return (self.hub.get_button_pressed() & 0x04) != 0

    def is_up_button_pressed(self) -> bool:
        return False

    def is_down_button_pressed(self) -> bool:
        return False


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
    def __init__(self):
        self.hub = connector.Hub()

    def is_pressed(self) -> bool:
        return (self.hub.get_button_pressed() & 0x01) != 0


class SonarSensor(etrobo_python.SonarSensor):
    def __init__(self) -> None:
        self.sonar_sensor = connector.SonarSensor()

    def listen(self) -> bool:
        return self.sonar_sensor.listen()

    def get_distance(self) -> int:
        return self.sonar_sensor.get_distance()


class GyroSensor(etrobo_python.GyroSensor):
    def __init__(self) -> None:
        self.gyro_sensor = connector.GyroSensor()

    def reset(self) -> None:
        self.gyro_sensor.reset()

    def get_angle(self) -> int:
        return self.gyro_sensor.get_angle()

    def get_angler_velocity(self) -> int:
        return self.gyro_sensor.get_angler_velocity()
