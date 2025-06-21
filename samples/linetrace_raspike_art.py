import argparse
from typing import Any

from etrobo_python import ColorSensor, ETRobo, Motor, TouchSensor
from linetrace_simulator import LineTracer


def run(backend: str, target: int, power: int, pid_p: float, **kwargs: Any) -> None:
    (ETRobo(backend=backend)
     .add_hub('hub')
     .add_device('right_motor', device_type=Motor, port='A')
     .add_device('left_motor', device_type=Motor, port='B')
     .add_device('touch_sensor', device_type=TouchSensor, port='D')
     .add_device('color_sensor', device_type=ColorSensor, port='E')
     .add_handler(LineTracer(target, power, pid_p))
     .dispatch(**kwargs))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default='/dev/USB_SPIKE', help='Serial port.')
    parser.add_argument('--logfile', type=str, default=None, help='Path to log file')
    args = parser.parse_args()
    run(backend='raspike_art', port=args.port,
        interval=0.04, target=60, power=55, pid_p=0.05, logfile=args.logfile)
