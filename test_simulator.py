import etrobo_python
from etrobo_python import ColorSensor, Motor, TouchSensor

TARGET = 20
POWER = 70
PID_P = 1.8


class LineTracer(object):
    def __init__(self) -> None:
        self.running = False

    def __call__(
        self,
        right_motor: Motor,
        left_motor: Motor,
        touch_sensor: TouchSensor,
        color_sensor: ColorSensor,
    ) -> None:
        if touch_sensor.is_pressed():
            self.running = True

        if not self.running:
            return

        brightness = color_sensor.get_brightness() - TARGET
        right_pwm = round(POWER + PID_P * brightness)
        left_pwm = round(POWER - PID_P * brightness)

        right_motor.set_pwm(right_pwm)
        left_motor.set_pwm(left_pwm)
        print(left_motor.get_count(), right_motor.get_count())


def main():
    (etrobo_python.ETRobo(backend='simulator')
     .add_device('right_motor', device_type='motor', port='B')
     .add_device('left_motor', device_type='motor', port='C')
     .add_device('touch_sensor', device_type='touch_sensor', port='1')
     .add_device('color_sensor', device_type='color_sensor', port='2')
     .add_handler(LineTracer())
     .dispatch(course='left'))


if __name__ == '__main__':
    main()
