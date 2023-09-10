'''ボタンによってモーターを操作するプログラム。
左ボタンを押す：左方向に旋回する
右ボタンを押す：右方向に旋回する
上ボタンを押す：前進する
下ボタンを押す：後退する
'''
import argparse

from etrobo_python import ETRobo, Hub, Motor

MOTOR_POWER = 50


class Controller(object):
    def __call__(self, hub: Hub, left_motor: Motor, right_motor: Motor) -> None:
        if hub.is_left_button_pressed():
            left_motor.set_power(MOTOR_POWER)
            right_motor.set_power(-MOTOR_POWER)
        elif hub.is_right_button_pressed():
            left_motor.set_power(-MOTOR_POWER)
            right_motor.set_power(MOTOR_POWER)
        elif hub.is_up_button_pressed():
            left_motor.set_power(MOTOR_POWER)
            right_motor.set_power(MOTOR_POWER)
        elif hub.is_down_button_pressed():
            left_motor.set_power(-MOTOR_POWER)
            right_motor.set_power(-MOTOR_POWER)
        else:
            left_motor.set_power(0)
            right_motor.set_power(0)


def run(backend: str, **kwargs) -> None:
    (ETRobo(backend=backend)
     .add_hub('hub')
     .add_device('right_motor', device_type=Motor, port='B')
     .add_device('left_motor', device_type=Motor, port='C')
     .add_handler(Controller())
     .dispatch(**kwargs))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--logfile', type=str, default=None, help='Path to log file')
    args = parser.parse_args()
    run(backend='simulator', logfile=args.logfile)
