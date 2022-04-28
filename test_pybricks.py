#!/usr/bin/env pybricks-micropython
import etrobo_python
from etrobo_python import ColorSensor, Motor, TouchSensor

TARGET = 20
POWER = 70
PID_P = 1.8


class LineTracer(object):
    def __init__(self) -> None:
        self.running = False

    def trace_line(
        self,
        right_motor: Motor,
        left_motor: Motor,
        color_sensor: ColorSensor,
    ) -> None:
        brightness = color_sensor.get_brightness() - TARGET
        right_pwm = round(POWER + PID_P * brightness)
        left_pwm = round(POWER - PID_P * brightness)

        right_motor.set_pwm(right_pwm)
        left_motor.set_pwm(left_pwm)

    def __call__(
        self,
        right_motor: Motor,
        left_motor: Motor,
        touch_sensor: TouchSensor,
        color_sensor: ColorSensor,
    ) -> None:
        if touch_sensor.is_pressed():
            self.running = True

        if self.running:
            self.trace_line(
                right_motor=right_motor,
                left_motor=left_motor,
                color_sensor=color_sensor)


def main():
    (etrobo_python.ETRobo(backend='pybricks')
     .add_device('right_motor', device_type='motor', port='B')
     .add_device('left_motor', device_type='motor', port='C')
     .add_device('touch_sensor', device_type='touch_sensor', port='1')
     .add_device('color_sensor', device_type='color_sensor', port='2')
     .add_handler(LineTracer())
     .dispatch())


if __name__ == '__main__':
    main()
