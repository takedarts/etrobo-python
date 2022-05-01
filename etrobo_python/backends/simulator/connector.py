from typing import Any, Callable, List, Optional, Tuple
import socket
from struct import pack_into, unpack_from


_CONNECTOR: Optional['_Connector'] = None


def get_connector() -> '_Connector':
    global _CONNECTOR

    if _CONNECTOR is None:
        raise Exception('Simulator have been not connected yet.')

    return _CONNECTOR


def _read_values(fmt: str, offset: int) -> Tuple[Any, ...]:
    return unpack_from(fmt, get_connector().recv_data, offset)


def _write_values(fmt: str, offset: int, *args) -> None:
    pack_into(fmt, get_connector().send_data, offset, *args)


def _reserve_values(fmt: str, offset: int, *args) -> None:
    get_connector().reserve_data.append((fmt, offset, args))


def connect_simulator(
    hook: Callable[[], None],
    address: str = '127.0.0.1',
    course: str = 'left',
    interval: float = 0.01,
    timeout: float = 5.0,
) -> None:
    global _CONNECTOR

    if _CONNECTOR is not None:
        raise Exception('Simulator is already connected.')

    _CONNECTOR = _Connector(
        hook=hook,
        address=address,
        course=course,
        interval=interval,
        timeout=timeout)
    _CONNECTOR.run()
    _CONNECTOR = None


class _Connector(object):
    def __init__(
        self,
        hook: Callable[[], None],
        address: str = '127.0.0.1',
        course: str = 'left',
        interval: float = 0.01,
        timeout: float = 5.0,
    ) -> None:
        if course.lower() == 'right':
            self.send_address = (address, 54003)
            self.recv_address = ('0.0.0.0', 54004)
        else:
            self.send_address = (address, 54001)
            self.recv_address = ('0.0.0.0', 54002)

        self.interval = round(interval * 1_000_000)

        self.send_data = bytearray(1024)
        self.recv_data = b'0' * 1024

        self.send_time = 0
        self.recv_time = 0

        self.hook = hook
        self.timeout = timeout
        self.reserve_data: List[Tuple[str, int, Tuple[Any, ...]]] = []

    def run(self) -> None:
        sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        sock.bind(self.recv_address)

        try:
            # Unityに接続
            print(f'Connecting to the Unity Simulator {self.send_address}.')
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
                for fmt, offset, args in self.reserve_data:
                    pack_into(fmt, self.send_data, offset, *args)

                self.reserve_data.clear()
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


class Hub(object):
    def set_led(self, color: int) -> None:
        _write_values('<I', 32, color)

    def get_time(self) -> float:
        return get_connector().recv_time / 1_000_000


class Motor(object):
    def __init__(self, port: int) -> None:
        self.port = port

    def get_count(self) -> int:
        return _read_values('<i', 288 + self.port * 4)[0]

    def reset_count(self) -> None:
        _write_values('<i', 68 + self.port * 4, 1)
        _reserve_values('<i', 68 + self.port * 4, 0)

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


class SonarSensor(object):
    def listen(self) -> bool:
        return _read_values('<i', 124)[0] != 0

    def get_distance(self) -> int:
        return _read_values('<i', 120)[0]


class GyroSensor(object):
    def reset(self) -> None:
        _write_values('<i', 84, 1)
        _reserve_values('<i', 84, 0)

    def get_angle(self) -> int:
        return _read_values('<i', 60)[0]

    def get_angler_velocity(self) -> int:
        return _read_values('<i', 64)[0]
