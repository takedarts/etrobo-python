import argparse
from observe_simulator import run

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default='/dev/ttyAMA1', help='Serial port.')
    parser.add_argument('--logfile', type=str, default=None, help='Path to log file')
    args = parser.parse_args()
    run(backend='raspike', port=args.port, logfile=args.logfile)
