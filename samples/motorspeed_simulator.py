'''モーターの回転速度を計測するプログラム。
ポートBに接続されたモーターを回転させ、それぞれの設定値のときの回転速度を計測する。
'''
import argparse

from etrobo_python import ETRobo, Hub, Motor

MEASURE_TIME = 10.0


class SpeedChecker(object):
    def __init__(self) -> None:
        self.power = 0
        self.start_time = 0.0
        self.finished = False

    def __call__(self, hub: Hub, motor: Motor) -> None:
        if self.finished:
            return

        current_time = hub.get_time()

        if self.power != 0 and current_time - self.start_time < MEASURE_TIME:
            return

        if self.power != 0:
            print('power={}: speed={:.4f} [deg/sec]'.format(
                self.power, motor.get_count() / MEASURE_TIME))

        if self.power >= 100:
            motor.set_power(0)
            self.finished = True
            return

        self.power += 10
        self.start_time = current_time
        motor.reset_count()
        motor.set_power(self.power)


def run(backend: str, **kwargs) -> None:
    (ETRobo(backend=backend)
     .add_hub('hub')
     .add_device('motor', device_type=Motor, port='B')
     .add_handler(SpeedChecker())
     .dispatch(**kwargs))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--logfile', type=str, default=None, help='Path to log file')
    args = parser.parse_args()
    run(backend='simulator', logfile=args.logfile)
