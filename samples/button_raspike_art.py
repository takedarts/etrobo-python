import argparse

from etrobo_python import ColorSensor, ETRobo, Hub, Motor, TouchSensor
from button_simulator import Controller

def run(backend: str, **kwargs) -> None:
    (ETRobo(backend=backend)
     .add_hub('hub')
     .add_device('right_motor', device_type=Motor, port='B')
     .add_device('left_motor', device_type=Motor, port='E')
     .add_handler(Controller())
     .dispatch(**kwargs))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--logfile', type=str, default=None, help='Path to log file')
    args = parser.parse_args()
    run(backend='raspike_art', interval=0.04, logfile=args.logfile)
