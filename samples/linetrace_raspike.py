import argparse
from linetrace_simulator import run

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default='/dev/ttyAMA1', help='Serial port.')
    args = parser.parse_args()
    run(backend='raspike', port=args.port, interval=0.04, target=60, power=55, pid_p=0.05)
