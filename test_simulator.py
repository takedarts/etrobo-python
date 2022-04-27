import pathlib
import sys

ETROBOSIM_PATH = str(
    (pathlib.Path(__file__).parent / 'ETRoboSimController').absolute())
if ETROBOSIM_PATH not in sys.path:
    sys.path.insert(0, ETROBOSIM_PATH)

import etrobo_python
from etrobo_python import ColorSensor, Motor

TARGET = 20
POWER = 70
PID_P = 1.8


def line_trace(right_motor: Motor, left_motor: Motor, color_sensor: ColorSensor) -> None:
    brightness = color_sensor.get_brightness() - TARGET
    right_pwm = round(POWER + PID_P * brightness)
    left_pwm = round(POWER - PID_P * brightness)

    right_motor.set_pwm(right_pwm)
    left_motor.set_pwm(left_pwm)


def main():
    (etrobo_python.ETRobo(backend='simulator')
     .add_device('right_motor', device_type='motor', port='B')
     .add_device('left_motor', device_type='motor', port='C')
     .add_device('color_sensor', device_type='color_sensor', port='2')
     .add_handler(line_trace)
     .dispatch(course='left', debug=True))


if __name__ == '__main__':
    main()
