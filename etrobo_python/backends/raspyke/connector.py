import base64
import threading
import time
from typing import Callable, Optional, Tuple

import serial

'''
送信（観測）データ: Base64でエンコードした文字列を送受信する
[0-1] magic number (0x7f, 0x7f)
[2-4] time
[5-13] motor count (A, B, C) (3 bytes each)
[14-16] one of ambient, color, reflect, rgb (r, g, b)
[17-17] ultrasonic
[18-20] gyro (angle, speed) (12bit each)
[21-23] system info  - number(1byte) value(2bytes)
  0: buttun status (値の1ビット目:connect, 1:left, 2:right, 3:center)
  1: battery voltage
  2: battery current

受信（命令）データ: バイナリデータを送受信する
[0-1] magic number (0x7f, 0x7f)
[2-3] command
[3-6] value

command: number - value
0x00: sleep - time (milli seconds)
0x01: sound - frequency (Hz), duration (milli seconds) (2bytes each)
0x02: volume - volume (0-10)
0x03: led - number (0-20)
0x11: motor A power - power
0x12: motor A brake - 0/1
0x13: motor A reset - 0
0x21: motor B power - power
0x22: motor B brake - 0/1
0x23: motor B reset - 0
0x31: motor C power - power
0x32: motor C brake - 0/1
0x33: motor C reset - 0
0x41: color sensor mode - mode (0=ambient, 1=color, 2=reflect, 3=rgb)
0x51: gyro reset - 0
'''

# モーターの回転方向
# モーターの設定値と取得値の方向を設定する
# +1 か -1 を設定すること
MOTOR_SIGN = 1

_CONNECTOR: Optional['_Connector'] = None


def connect_spike(
    handler: Callable[[], None],
    interval: float,
    port: str,
    baudrate: int,
    timeout: float,
) -> None:
    global _CONNECTOR

    if _CONNECTOR is not None:
        raise Exception('This process have already connected to the Spike.')

    _CONNECTOR = _Connector(
        handler=handler,
        interval=interval,
        port=port,
        baudrate=baudrate,
        timeout=timeout)
    _CONNECTOR.run()
    _CONNECTOR = None


def _get_connector() -> '_Connector':
    global _CONNECTOR

    if _CONNECTOR is None:
        raise Exception(
            'This process have been not connected to the Spike yet.')

    return _CONNECTOR


class _Connector(object):
    def __init__(
        self,
        handler: Callable[[], None],
        interval: float,
        port: str,
        baudrate: int,
        timeout: float,
    ) -> None:
        self.handler = handler
        self.interval = interval
        self.running = False

        self.recv_data = bytearray(27)
        self.send_data = bytearray(7)

        self.serial = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)

    def run(self) -> None:
        receiver_thread = threading.Thread(
            target=self._run_receiver,
            name='RasPike_run_receiver',
        )

        handler_thread = threading.Thread(
            target=self._run_handler,
            name='RasPike_run_handler',
        )

        self.running = True
        receiver_thread.start()
        handler_thread.start()

        try:
            receiver_thread.join()
            handler_thread.join()
        except KeyboardInterrupt:
            print('Interrupted by keyboard.')
            self.running = False
            receiver_thread.join()
            handler_thread.join()
            self.send_command(command=0x11, value=0)
            self.send_command(command=0x21, value=0)
            self.send_command(command=0x31, value=0)

    def _run_receiver(self) -> None:
        buffer = bytearray(32)

        try:
            while self.running:
                # 受信データを読み込む
                if not self._recv_report(buffer):
                    continue

                # base64の文字列をデコードしてデータを取得する
                try:
                    data = base64.b64decode(buffer.decode('ascii'))
                except UnicodeDecodeError:
                    continue

                # 受信データを保存する
                self.recv_data[:21] = data[:21]

                if 0 <= data[21] < 3:
                    offset = 21 + data[21] * 2
                    self.recv_data[offset:offset + 2] = data[22:]
        finally:
            self.running = False

    def _recv_report(self, buffer: bytearray) -> bool:
        # 受信データを読み込む
        size = self.serial.readinto(buffer)

        # タイムアウト
        if size < len(buffer):
            raise Exception('Connection is timeout.')

        # パケットの先頭を探す
        while buffer[0] != 102 or buffer[1] != 51:
            offset = buffer.find(102, 2, size)
            if offset < 0:
                return False

            buffer[:-offset] = buffer[offset:]
            size -= offset

        # 残りのデータを受信する
        while size < len(buffer):
            buf = self.serial.read(len(buffer) - size)
            if len(buf) < len(buffer) - size:
                raise Exception('Connection is timeout')

            buffer[size:] = buf
            size += len(buf)

        return True

    def _run_handler(self) -> None:
        previous_time = 0

        try:
            while self.running:
                # 時刻を確認する
                interval_time = int(self.interval * 1000)
                current_time = int(time.time() * 1000)
                process_time = (current_time // interval_time) * interval_time

                # 前回の時刻との間隔が設定値より短いなら待機する
                if process_time == previous_time:
                    next_time = previous_time + interval_time
                    time.sleep((next_time - current_time) * 0.001)
                    continue

                # 制御処理を実行
                previous_time = process_time
                self.handler()
        except StopIteration:
            print('Stopped by handler.')
        finally:
            self.running = False

    def send_command(self, command: int, value: int) -> None:
        self.send_data[0] = 0x7f
        self.send_data[1] = 0x7f
        self.send_data[2] = command
        self.send_data[3:7] = int.to_bytes(value & 0xffffffff, 4, 'big')
        self.serial.write(self.send_data)


class Hub(object):
    def set_led(self, code: int) -> None:
        _get_connector().send_command(command=0x03, value=code)

    def get_time(self) -> int:
        return int.from_bytes(_get_connector().recv_data[2:5], 'big')

    def get_battery_voltage(self) -> int:
        return int.from_bytes(_get_connector().recv_data[23:25], 'big')

    def get_battery_current(self) -> int:
        return int.from_bytes(_get_connector().recv_data[25:27], 'big')

    def play_speaker_tone(self, frequency: int, duration: int) -> None:
        value = (frequency & 0xffff) << 16 | duration & 0xffff
        _get_connector().send_command(command=0x01, value=value)

    def set_speaker_volume(self, volume: int) -> None:
        _get_connector().send_command(command=0x02, value=volume)

    def get_button_pressed(self) -> int:
        return int.from_bytes(_get_connector().recv_data[21:23], 'big')


class Motor(object):
    def __init__(self, port: int) -> None:
        self.port = port

    def get_count(self) -> int:
        index = 5 + self.port * 3
        return int.from_bytes(
            _get_connector().recv_data[index:index + 3], 'big', signed=True)

    def reset_count(self) -> None:
        command = (self.port + 1) * 16 + 3
        _get_connector().send_command(command=command, value=0)

    def set_pwm(self, power: int) -> None:
        command = (self.port + 1) * 16 + 1
        power = min(max(power, -128), 127)
        _get_connector().send_command(command=command, value=power)

    def set_brake(self, brake: bool) -> None:
        command = (self.port + 1) * 16 + 2
        _get_connector().send_command(command=command, value=int(brake))


class ColorSensor(object):
    def __init__(self) -> None:
        self.mode = -1

    def get_brightness(self) -> int:
        self._change_mode(2)
        return _get_connector().recv_data[14]

    def get_ambient(self) -> int:
        self._change_mode(0)
        return _get_connector().recv_data[14]

    def get_raw_color(self) -> Tuple[int, int, int]:
        self._change_mode(3)
        conn = _get_connector()

        return conn.recv_data[14], conn.recv_data[15], conn.recv_data[16]

    def _change_mode(self, mode: int) -> None:
        if self.mode != mode:
            _get_connector().send_command(command=0x41, value=mode)
            self.mode = mode


class SonarSensor(object):
    def __init__(self):
        self.mode = 0

    def listen(self) -> bool:
        return False

    def get_distance(self) -> int:
        return _get_connector().recv_data[17]


class GyroSensor(object):
    def reset(self) -> None:
        _get_connector().send_command(command=0x51, value=0)

    def get_angle(self) -> int:
        value = int.from_bytes(_get_connector().recv_data[18:21], 'big')
        value = value >> 12

        if value < 0x800:
            return value
        else:
            return value - 0x1000

    def get_angler_velocity(self) -> int:
        value = int.from_bytes(_get_connector().recv_data[18:21], 'big')
        value = value & 0x0fff

        if value < 0x800:
            return value
        else:
            return value - 0x1000
