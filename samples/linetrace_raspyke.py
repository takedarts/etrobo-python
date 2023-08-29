import argparse
from linetrace_simulator import run

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default='/dev/ttyAMA1', help='Serial port.')
    args = parser.parse_args()
    run(backend='raspyke', target=20, power=70, pid_p=1.8, port=args.port)
