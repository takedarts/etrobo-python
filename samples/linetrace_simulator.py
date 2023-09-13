import argparse

from etrobo_python import ColorSensor, ETRobo, Hub, Motor, TouchSensor


class LineTracer(object):
    def __init__(self, target: int, power: int, pid_p: float) -> None:
        self.running = False
        self.target = target
        self.power = power
        self.pid_p = pid_p

    def __call__(
        self,
        hub: Hub,
        right_motor: Motor,
        left_motor: Motor,
        touch_sensor: TouchSensor,
        color_sensor: ColorSensor,
    ) -> None:
        if not self.running and (
                touch_sensor.is_pressed()
                or hub.is_left_button_pressed()
                or hub.is_right_button_pressed()):
            self.running = True

        if not self.running:
            return

        brightness = color_sensor.get_brightness() - self.target
        power_ratio = self.pid_p * brightness

        if power_ratio > 0:
            right_motor.set_power(self.power)
            left_motor.set_power(int(self.power / (1 + power_ratio)))
        else:
            right_motor.set_power(int(self.power / (1 - power_ratio)))
            left_motor.set_power(self.power)


def run(backend: str, target: int, power: int, pid_p: float, **kwargs) -> None:
    (ETRobo(backend=backend)
     .add_hub('hub')
     .add_device('right_motor', device_type=Motor, port='B')
     .add_device('left_motor', device_type=Motor, port='C')
     .add_device('touch_sensor', device_type=TouchSensor, port='1')
     .add_device('color_sensor', device_type=ColorSensor, port='2')
     .add_handler(LineTracer(target, power, pid_p))
     .dispatch(**kwargs))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--logfile', type=str, default=None, help='Path to log file')
    args = parser.parse_args()
    run(backend='simulator', target=17, power=50, pid_p=0.2, logfile=args.logfile)
