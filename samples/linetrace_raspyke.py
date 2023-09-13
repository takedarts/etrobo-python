import argparse
from linetrace_simulator import run

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default='/dev/ttyAMA1', help='Serial port.')
    args = parser.parse_args()
    run(backend='raspyke', port=args.port, interval=0.01, target=60, power=60, pid_p=0.05)
