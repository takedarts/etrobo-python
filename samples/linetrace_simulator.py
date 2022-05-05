from etrobo_python import ColorSensor, ETRobo, Motor, TouchSensor


class LineTracer(object):
    def __init__(self, target: int, power: int, pid_p: float) -> None:
        self.running = False
        self.target = target
        self.power = power
        self.pid_p = pid_p

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

        brightness = color_sensor.get_brightness() - self.target
        right_power = round(self.power + self.pid_p * brightness)
        left_power = round(self.power - self.pid_p * brightness)

        right_motor.set_power(right_power)
        left_motor.set_power(left_power)


def run(backend: str, target: int, power: int, pid_p: float) -> None:
    (ETRobo(backend=backend)
     .add_device('right_motor', device_type='motor', port='B')
     .add_device('left_motor', device_type='motor', port='C')
     .add_device('touch_sensor', device_type='touch_sensor', port='1')
     .add_device('color_sensor', device_type='color_sensor', port='2')
     .add_handler(LineTracer(target, power, pid_p))
     .dispatch())


if __name__ == '__main__':
    run(backend='simulator', target=20, power=70, pid_p=1.8)
