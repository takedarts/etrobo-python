from typing import Any, Callable, Optional, Tuple
import socket
from struct import pack_into, unpack_from


_CONNECTOR: Optional['_Connector'] = None


def get_connector() -> '_Connector':
    global _CONNECTOR

    if _CONNECTOR is None:
        raise Exception('Simulator have been not connected yet.')

    return _CONNECTOR


def _read_values(fmt, offset) -> Tuple[Any, ...]:
    return unpack_from(fmt, get_connector().recv_data, offset)


def _write_values(fmt, offset, *args) -> None:
    return pack_into(fmt, get_connector().send_data, offset, *args)


def connect_simulator(
    course: str = 'left',
    interval: float = 0.01,
    hook: Optional[Callable[[], None]] = None,
    timeout: float = 5.0,
) -> None:
    global _CONNECTOR

    if _CONNECTOR is not None:
        raise Exception('Simulator is already connected.')

    _CONNECTOR = _Connector(
        course=course, interval=interval, hook=hook, timeout=timeout)
    _CONNECTOR.run()
    _CONNECTOR = None


class _Connector(object):
    def __init__(
        self,
        course: str = 'left',
        interval: float = 0.01,
        hook: Optional[Callable[[], None]] = None,
        timeout: float = 5.0,
    ) -> None:
        if course.lower() == 'right':
            self.send_address = ('127.0.0.1', 54003)
            self.recv_address = ('127.0.0.1', 54004)
        else:
            self.send_address = ('127.0.0.1', 54001)
            self.recv_address = ('127.0.0.1', 54002)

        self.interval = round(interval * 1_000_000)

        self.send_data = bytearray(1024)
        self.recv_data = b'0' * 1024

        self.send_time = 0
        self.recv_time = 0

        self.hook = hook
        self.timeout = timeout

    def run(self) -> None:
        sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        sock.bind(self.recv_address)

        try:
            # Unityに接続
            print('Connecting to the Unity Simulator.')
            pack_into('<4sI', self.send_data, 0, b'ETTX', 1)
            pack_into('<II', self.send_data, 24, 512, 512)
            sock.sendto(self.send_data, self.send_address)

            self.recv_data, _ = sock.recvfrom(1024)
            self.recv_time, = unpack_from('<Q', self.recv_data, 16)
            send_time = (self.recv_time // self.interval) * self.interval
            print('Connected to the Unity Simulator.')

            while True:
                # Unityからデータを受信する
                self.recv_data, _ = sock.recvfrom(1024)
                self.recv_time, = unpack_from('<Q', self.recv_data, 16)
                send_time = (self.recv_time // self.interval) * self.interval

                # 状態更新の必要を確認
                if self.send_time == send_time:
                    continue

                self.send_time = send_time

                # 状態を更新
                if self.hook is not None:
                    self.hook()

                # データをUnityに送信する
                pack_into('<QQ', self.send_data, 8, self.send_time, self.recv_time)
                sock.sendto(self.send_data, self.send_address)
        except socket.timeout:
            print('Timeout the connection')
        except KeyboardInterrupt:
            print('Interrupted by Keyboard')
        finally:
            print('Closing the connection.')
            sock.close()


class Motor(object):
    def __init__(self, port: int) -> None:
        self.port = port

    def get_count(self) -> int:
        return _read_values('<i', 288 + self.port * 4)[0]

    def set_pwm(self, pwm: int) -> None:
        pwm = min(max(pwm, -100), 100)
        _write_values('<I', 36 + self.port * 4, pwm)

    def set_brake(self, brake: bool) -> None:
        _write_values('<I', 52 + self.port * 4, int(brake))


class ColorSensor(object):
    def get_brightness(self) -> int:
        return _read_values('<i', 44)[0]

    def get_ambient(self) -> int:
        return _read_values('<i', 36)[0]

    def get_color_number(self) -> int:
        return _read_values('<i', 40)[0]

    def get_raw_color(self) -> Tuple[int, int, int]:
        return _read_values('<iii', 48)  # type:ignore


class TouchSensor(object):
    def is_pressed(self) -> bool:
        return _read_values('<i', 144)[0] != 0
