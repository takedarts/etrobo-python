import argparse
from typing import Any

from button_simulator import Controller
from etrobo_python import ETRobo, Motor


def run(backend: str, **kwargs: Any) -> None:
    (ETRobo(backend=backend)
     .add_hub('hub')
     .add_device('right_motor', device_type=Motor, port='A')
     .add_device('left_motor', device_type=Motor, port='B')
     .add_handler(Controller())
     .dispatch(**kwargs))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default='/dev/USB_SPIKE', help='Serial port.')
    parser.add_argument('--logfile', type=str, default=None, help='Path to log file')
    args = parser.parse_args()
    run(backend='raspike_art', port=args.port, interval=0.04, logfile=args.logfile)
