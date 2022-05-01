from etrobo_python import ColorSensor, Motor, TouchSensor, ETRobo

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
        right_power = round(POWER + PID_P * brightness)
        left_power = round(POWER - PID_P * brightness)

        right_motor.set_power(right_power)
        left_motor.set_power(left_power)


def run(backend: str) -> None:
    (ETRobo(backend=backend)
     .add_device('right_motor', device_type='motor', port='B')
     .add_device('left_motor', device_type='motor', port='C')
     .add_device('touch_sensor', device_type='touch_sensor', port='1')
     .add_device('color_sensor', device_type='color_sensor', port='2')
     .add_handler(LineTracer())
     .dispatch())
