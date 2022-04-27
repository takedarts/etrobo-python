from typing import Tuple


class Motor(object):
    def set_pwm(self, pwm: int) -> None:
        raise NotImplementedError()

    def set_brake(self, brake: bool) -> None:
        raise NotImplementedError()


class ColorSensor(object):
    def get_brightness(self) -> int:
        raise NotImplementedError()

    def get_raw_color(self) -> Tuple[int, int, int]:
        raise NotImplementedError()


class TouchSensor(object):
    def is_pressed(self) -> bool:
        raise NotImplementedError()
