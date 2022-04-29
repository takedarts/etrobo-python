try:
    from typing import Tuple
except BaseException:
    pass


class Motor(object):
    def get_count(self) -> int:
        raise NotImplementedError()

    def set_pwm(self, pwm: int) -> None:
        raise NotImplementedError()

    def set_brake(self, brake: bool) -> None:
        raise NotImplementedError()


class ColorSensor(object):
    def get_brightness(self) -> int:
        raise NotImplementedError()

    def get_ambient(self) -> int:
        raise NotImplementedError()

    def get_raw_color(self) -> Tuple[int, int, int]:
        raise NotImplementedError()


class TouchSensor(object):
    def is_pressed(self) -> bool:
        raise NotImplementedError()


class SonarSensor(object):
    def listen(self) -> bool:
        raise NotImplementedError()

    def get_distance(self) -> int:
        raise NotImplementedError()
