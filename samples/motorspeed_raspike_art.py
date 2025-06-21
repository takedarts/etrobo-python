import argparse

from motorspeed_simulator import run

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default='/dev/USB_SPIKE', help='Serial port.')
    parser.add_argument('--logfile', type=str, default=None, help='Path to log file')
    args = parser.parse_args()
    run(backend='raspike_art', port=args.port, interval=0.04, logfile=args.logfile)
