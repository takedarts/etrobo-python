from typing import Any

import etrobosim.ev3api as ev3
from etrobo_python import Motor

from .util import get_ev3port


class MotorImpl(Motor):
    def __init__(self, port: str) -> None:
        self.motor = ev3.Motor(
            get_ev3port(port), True, ev3.MotorType.LARGE_MOTOR)
        self.motor.reset()

    def ev3device(self) -> Any:
        return self.motor

    def set_pwm(self, pwm: int) -> None:
        self.motor.setPWM(pwm)

    def set_brake(self, brake: bool) -> None:
        self.motor.setBrake(brake)
