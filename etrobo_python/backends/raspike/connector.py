import threading
import time
from typing import Callable, Optional, Tuple

import serial

_CONNECTOR: Optional['_Connector'] = None

# 受信データ
# バッファ内の位置: 命令番号 - 意味
# 00:  1 - カラーセンサ（ambient)
# 01:  2 - カラーセンサ（color）
# 02:  3 - カラーセンサ（reflect）
# 03:  4 - カラーセンサ（Red）
# 04:  5 - カラーセンサ（Green）
# 05:  6 - カラーセンサ（Blue）
# 06:  7 - ジャイロセンサ（Angle）
# 07:  8 - ジャイロセンサ（Speed）
# 08: 22 - 超音波センサ（距離）
# 09: 23 - 超音波センサ（Listen）
# 10: 28 - タッチセンサ（Pressed）
# 11: 29 - バッテリ電流
# 12: 30 - バッテリ電圧
# 13: 64 - モータA（Count）
# 14: 65 - モータB（Count）
# 15: 66 - モータC（Count）
_RECV_CMD_INDEX = [
    -1, 0, 1, 2, 3, 4, 5, 6, 7, -1,
    -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
    -1, -1, 8, 9, -1, -1, -1, -1, 10, 11,
    12, -1, -1, -1, -1, -1, -1, -1, -1, -1,
    -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
    -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
    -1, -1, -1, -1, 13, 14, 15, -1, -1, -1,
]

# 送信データ
# 命令番号 - 意味 - 取りうる値
# 1 - モータA（PWM）- [-100, 100]
# 2 - モータB（PWM）- [-100, 100]
# 3 - モータC（PWM）- [-100, 100]
# 5 - モータA（Brake）- {0, 1}
# 6 - モータB（Brake）- {0, 1}
# 7 - モータC（Brake）- {0, 1}
# 9 - モータA（Reset）- Any
# 10 - モータB（Reset）- Any
# 11 - モータC（Reset）- Any
# 61 - カラーセンサ（Mode）- 1:Ambient, 2:Color, 3:Reflect, 4:RGB
# 62 - 超音波センサ（Mode）- 1:Distance, 2:Listen
# 63 - ジャイロセンサ（Reset）- 4（なぜか4を指定しないとリセットされない仕様）


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


def _parse_received_command(bin: bytearray) -> Tuple[int, int]:
    command = (
        (bin[1] - 48) * 1000
        + (bin[2] - 48) * 100
        + (bin[3] - 48) * 10
        + (bin[4] - 48))
    value = (
        (bin[7] - 48) * 10000
        + (bin[8] - 48) * 1000
        + (bin[9] - 48) * 100
        + (bin[10] - 48) * 10
        + (bin[11] - 48))

    if bin[6] == 45:  # '-'
        value = -value

    return command, value


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

        self.recv_data = [0] * 16
        self.send_data = bytearray(3)
        self.running = False

        self.serial = serial.Serial(
            port=port, baudrate=baudrate, timeout=timeout)
        self.event = threading.Event()

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
            self.send_command(command=5, value=1, wait_for_ack=False)
            self.send_command(command=6, value=1, wait_for_ack=False)
            self.send_command(command=7, value=1, wait_for_ack=False)

    def _run_receiver(self) -> None:
        buffer = bytearray(12)

        try:
            while self.running:
                # 受信データを読み込む
                size = self.serial.readinto(buffer)

                # タイムアウト
                if size < 12:
                    print('Connection is timeout.')
                    break

                # 先頭が'<'か'@'以外の場合は先頭位置を調整する
                if buffer[0] not in (60, 64):  # '<' or '@':
                    if 58 not in buffer:
                        print('Protocol error.')
                        break

                    offset = (buffer.index(58) + 19) % 12
                    buffer[:-offset] = buffer[offset:]
                    buffer[-offset:] = self.serial.read(offset)

                # タイムアウト
                if len(buffer) < 12:
                    print('Connection is timeout.')
                    break

                # ACKの場合は待機しているスレッドに通知する
                if buffer[0] == 60:
                    self.event.set()
                    continue

                # 命令と値を取り出す
                command, value = _parse_received_command(buffer)

                # 受信データを反映する
                if 0 <= command < len(_RECV_CMD_INDEX):
                    self.recv_data[_RECV_CMD_INDEX[command]] = value
        finally:
            self.running = False

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

                # 接続を維持するためにダミーコマンドを送信
                self.send_command(command=127, value=0, wait_for_ack=False)
        except StopIteration:
            print('Stopped by handler.')
        finally:
            self.running = False

    def send_command(
        self,
        command: int,
        value: int,
        wait_for_ack: bool,
    ) -> None:
        self.event.clear()

        if value < 0:
            value = -value
            sign = 1
        else:
            sign = 0

        self.send_data[0] = 0x80 | command
        self.send_data[1] = (sign << 5) | ((value >> 7) & 0x1f)
        self.send_data[2] = (value & 0x7f)

        self.serial.write(self.send_data)
        if wait_for_ack:
            self.event.wait()


class Hub(object):
    def get_battery_voltage(self) -> int:
        return _get_connector().recv_data[12]

    def get_battery_current(self) -> int:
        return _get_connector().recv_data[11]


class Motor(object):
    def __init__(self, port: int) -> None:
        self.port = port

    def get_count(self) -> int:
        return _get_connector().recv_data[13 + self.port]

    def reset_count(self) -> None:
        _get_connector().send_command(
            command=9 + self.port, value=0, wait_for_ack=True)

    def set_pwm(self, power: int) -> None:
        _get_connector().send_command(
            command=1 + self.port, value=power, wait_for_ack=False)

    def set_brake(self, brake: bool) -> None:
        _get_connector().send_command(
            command=1 + self.port, value=int(brake), wait_for_ack=False)


class ColorSensor(object):
    def __init__(self) -> None:
        self.mode = 0

    def get_brightness(self) -> int:
        self._change_mode(3)
        return _get_connector().recv_data[2]

    def get_ambient(self) -> int:
        self._change_mode(1)
        return _get_connector().recv_data[0]

    def get_raw_color(self) -> Tuple[int, int, int]:
        self._change_mode(4)
        conn = _get_connector()

        return conn.recv_data[3], conn.recv_data[4], conn.recv_data[5]

    def _change_mode(self, mode: int) -> None:
        if self.mode != mode:
            _get_connector().send_command(
                command=61, value=mode, wait_for_ack=True)
            self.mode = mode


class TouchSensor(object):
    def is_pressed(self) -> bool:
        return _get_connector().recv_data[10] != 0


class SonarSensor(object):
    def __init__(self):
        self.mode = 0

    def listen(self) -> bool:
        # SPIKE側のプログラムが正常に動作しないため常にFalseを返す（2022/05/16）。
        return False

    def get_distance(self) -> int:
        self._change_mode(1)
        return _get_connector().recv_data[8]

    def _change_mode(self, mode: int) -> None:
        if self.mode != mode:
            _get_connector().send_command(
                command=62, value=mode, wait_for_ack=True)
            self.mode = mode


class GyroSensor(object):
    def reset(self) -> None:
        _get_connector().send_command(command=63, value=4, wait_for_ack=True)

    def get_angle(self) -> int:
        return _get_connector().recv_data[6]

    def get_angler_velocity(self) -> int:
        return _get_connector().recv_data[7]
