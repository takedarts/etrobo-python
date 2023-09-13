import base64
from typing import Callable, Optional, Tuple

import serial

'''
送信（観測）データ: Base64でエンコードした文字列を送受信する
Base64でエンコードした文字列は 0x66, 0x33 で始まる
[0-1] magic number (0x7f, 0x70) (12bit)
[1] parity (4bit)
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
[0] magic number (0x7f)
[1] parity
[2-3] command
[3-6] value

command: number - value
0x00: ping - time reset (1byte), interval (milli seconds) (3bytes)
0x01: sound - frequency (Hz), duration (milli seconds) (2bytes each)
0x02: volume - volume (0-10)
0x03: led - number (0-20)
0x04: screen - number (0-20)
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
        self.started = False

        # 受信バッファ
        self.recv_buffer = bytearray(32)
        # 受信データ
        self.recv_data = bytearray(27)
        # 送信データ
        self.send_data = bytearray(7)

        # シリアル通信オブジェクト
        self.serial = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)

    def run(self) -> None:
        # シリアル通信のバッファを空にする
        self.serial.reset_input_buffer()

        # リセットコマンドを送信する
        self.send_ping_command(reset=True)

        try:
            while True:
                # 受信データを読み込む
                if not self._recv_report():
                    continue

                # 受信データの時刻を取得する
                report_time = int.from_bytes(self.recv_data[2:5], 'big')

                # 最初に受信したデータの時刻が1000よりも大きい場合はリセットコマンドを再送信する
                if not self.started:
                    if report_time > 1000:
                        self.send_ping_command(reset=True)
                        continue
                    else:
                        self.started = True

                # pingコマンドを送信する
                self.send_ping_command(reset=False)

                # 制御処理を実行する
                self.handler()
        except KeyboardInterrupt:
            print('Interrupted by keyboard.')
        finally:
            self.send_command(command=0x11, value=0)
            self.send_command(command=0x21, value=0)
            self.send_command(command=0x31, value=0)

    def _recv_report(self) -> bool:
        # 受信データを読み込む
        buf = self.serial.read(len(self.recv_buffer))

        # タイムアウト
        if len(buf) != len(self.recv_buffer):
            raise Exception('Connection is timeout.')

        # パケットの先頭を探す
        # 最後に先頭のマジックナンバーが見つかった場合は読み込み処理を行い
        # Base64のデコードやパリティにデータの確認を任せる
        offset = 0
        while offset < len(buf) - 1 and (buf[offset] != 102 or buf[offset + 1] != 51):
            offset = buf.find(102, offset + 1)
            if offset < 0:
                return False

        # パケットの内容をコピーする
        size = 0
        for v in buf[offset:]:
            if (47 <= v <= 57 or 65 <= v <= 90 or 97 <= v <= 122 or v in (43, 61)):
                self.recv_buffer[size] = v
                size += 1

        # 残りのデータを受信する
        while size < len(self.recv_buffer):
            buf = self.serial.read(len(self.recv_buffer) - size)
            if len(buf) < len(self.recv_buffer) - size:
                raise Exception('Connection is timeout')

            # パケットの内容をコピーする
            for v in buf:
                if (47 <= v <= 57 or 65 <= v <= 90 or 97 <= v <= 122 or v in (43, 61)):
                    self.recv_buffer[size] = v
                    size += 1

        # base64の文字列をデコードしてデータを取得する
        try:
            data = base64.b64decode(self.recv_buffer.decode('ascii'))
        except UnicodeDecodeError:
            return False

        # パリティを確認する
        if not self._is_valid_parity(data):
            return False

        # 受信データを保存する
        self.recv_data[:21] = data[:21]

        if 0 <= data[21] < 3:
            offset = 21 + data[21] * 2
            self.recv_data[offset:offset + 2] = data[22:]

        return True

    def _is_valid_parity(self, buffer: bytes) -> bool:
        parity = 0
        for v in buffer[2:]:
            parity |= v

        parity = (parity | parity >> 4) & 0xf

        return buffer[1] & 0xf == parity

    def send_command(self, command: int, value: int) -> None:
        self.send_data[0] = 0x7f
        self.send_data[2] = command
        self.send_data[3:7] = int.to_bytes(value & 0xffffffff, 4, 'big')

        parity = 0
        for v in self.send_data[2:]:
            parity |= v

        self.send_data[1] = parity
        self.serial.write(self.send_data)

    def send_ping_command(self, reset: bool) -> None:
        value = int(reset) << 24 | int(self.interval * 1000) & 0xffffff
        self.send_command(command=0x00, value=value)


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
    def get_brightness(self) -> int:
        conn = _get_connector()

        if conn.recv_data[15] != 0 or conn.recv_data[16] != 2:
            conn.send_command(command=0x41, value=2)

        return _get_connector().recv_data[14]

    def get_ambient(self) -> int:
        conn = _get_connector()

        if conn.recv_data[15] != 0 or conn.recv_data[16] != 0:
            conn.send_command(command=0x41, value=0)

        return _get_connector().recv_data[14]

    def get_raw_color(self) -> Tuple[int, int, int]:
        conn = _get_connector()

        if conn.recv_data[15] == 0 or conn.recv_data[16] == 0:
            conn.send_command(command=0x41, value=3)

        red = max(conn.recv_data[14] - 1, 0)
        green = max(conn.recv_data[15] - 1, 0)
        blue = max(conn.recv_data[16] - 1, 0)

        return red, green, blue


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
