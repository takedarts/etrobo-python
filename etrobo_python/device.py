from typing import Tuple


class Motor(object):
    def __init__(self) -> None:
        raise NotImplementedError()

    def set_pwm(self, pwm: int) -> None:
        raise NotImplementedError()

    def set_brake(self, brake: bool) -> None:
        raise NotImplementedError()


class ColorSensor(object):
    def __init__(self) -> None:
        raise NotImplementedError()

    def get_brightness(self) -> int:
        raise NotImplementedError()

    def get_raw_color(self) -> Tuple[int, int, int]:
        raise NotImplementedError()
