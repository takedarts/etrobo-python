import argparse
import csv
from typing import List

from etrobo_python.log import LogReader


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('logfile', type=str, default=None, help='Path to log file (input)')
    parser.add_argument('csvfile', type=str, default=None, help='Path to csv file (output)')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows: List[List[str]] = [[], []]

    with LogReader(args.logfile) as reader:
        devices = reader.get_devices()
        for name, type_name in devices:
            rows[0].append(f'{name}:{type_name}')
            if type_name == 'hub':
                rows[0].extend(['', '', '', ''])
                rows[1].extend(['time', 'left_button', 'right_button', 'up_button', 'down_button'])
            elif type_name == 'motor':
                rows[1].append('count')
            elif type_name == 'color_sensor':
                rows[0].extend(['', '', '', ''])
                rows[1].extend(['brightness', 'ambient', 'red', 'green', 'blue'])
            elif type_name == 'touch_sensor':
                rows[1].append('pressed')
            elif type_name == 'sonar_sensor':
                rows[1].append('distance')
            elif type_name == 'gyro_sensor':
                rows[0].extend([''])
                rows[1].extend(['angle', 'velocity'])

        for values in reader:
            rows.append([])
            for value, (_, type_name) in zip(values, devices):
                if type_name == 'hub':
                    rows[-1].append(str(int.from_bytes(value[:4], 'big')))
                    rows[-1].append(str(int(value[4] & 0x01 != 0)))
                    rows[-1].append(str(int(value[4] & 0x02 != 0)))
                    rows[-1].append(str(int(value[4] & 0x04 != 0)))
                    rows[-1].append(str(int(value[4] & 0x08 != 0)))
                elif type_name == 'motor':
                    rows[-1].append(str(int.from_bytes(value, 'big', signed=True)))
                elif type_name == 'color_sensor':
                    rows[-1].append(str(value[0]))
                    rows[-1].append(str(value[1]))
                    rows[-1].append(str(value[2]))
                    rows[-1].append(str(value[3]))
                    rows[-1].append(str(value[4]))
                elif type_name == 'touch_sensor':
                    rows[-1].append(str(int(value[0])))
                elif type_name == 'sonar_sensor':
                    rows[-1].append(str(int.from_bytes(value, 'big')))
                elif type_name == 'gyro_sensor':
                    rows[-1].append(str(int.from_bytes(value[:2], 'big', signed=True)))
                    rows[-1].append(str(int.from_bytes(value[2:], 'big', signed=True)))

    with open(args.csvfile, 'w') as writer:
        csv_writer = csv.writer(writer)
        csv_writer.writerows(rows)


if __name__ == '__main__':
    main()
