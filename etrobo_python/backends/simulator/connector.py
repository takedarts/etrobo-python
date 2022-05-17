import socket
import threading
from struct import pack_into, unpack_from
from typing import Any, Callable, List, Optional, Tuple

_CONNECTOR: Optional['_Connector'] = None


def connect_simulator(
    handler: Callable[[], None],
    interval: float,
    address: str,
    course: str,
    timeout: float,
) -> None:
    global _CONNECTOR

    if _CONNECTOR is not None:
        raise Exception(
            'This process have already connected to the simulator.')

    _CONNECTOR = _Connector(
        handler=handler,
        interval=interval,
        address=address,
        course=course,
        timeout=timeout)
    _CONNECTOR.run()
    _CONNECTOR = None


def _get_connector() -> '_Connector':
    global _CONNECTOR

    if _CONNECTOR is None:
        raise Exception(
            'This process have been not connected to the simulator yet.')

    return _CONNECTOR


class _Connector(object):
    def __init__(
        self,
        handler: Callable[[], None],
        interval: float,
        address: str,
        course: str,
        timeout: float,
    ) -> None:
        if course.lower() == 'right':
            self.send_address = (address, 54003)
            self.recv_address = ('0.0.0.0', 54004)
        else:
            self.send_address = (address, 54001)
            self.recv_address = ('0.0.0.0', 54002)

        self.handler = handler
        self.interval = round(interval * 1_000_000)
        self.timeout = timeout

        self.recv_buffer = bytearray(1024)
        self.recv_data = bytearray(1024)
        self.send_data = bytearray(1024)
        self.reserved_data: List[Tuple[str, int, Tuple[Any, ...]]] = []

        self.recv_time = 0
        self.proc_time = 0
        self.running = False

        self.lock = threading.Lock()
        self.event = threading.Event()

        self.sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
        self.sock.bind(self.recv_address)
        self.sock.settimeout(self.timeout)

    def read_values(self, fmt: str, offset: int) -> Tuple[Any, ...]:
        return unpack_from(fmt, self.recv_data, offset)

    def write_values(self, fmt: str, offset: int, *args) -> None:
        pack_into(fmt, self.send_data, offset, *args)

    def reserve_values(self, fmt: str, offset: int, *args) -> None:
        self.reserved_data.append((fmt, offset, args))

    def run(self) -> None:
        receiver_thread = threading.Thread(
            target=self._run_receiver,
            name='Simulator_run_receiver',
        )

        handler_thread = threading.Thread(
            target=self._run_handler,
            name='Simulator_run_handler',
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
            self.event.set()
            receiver_thread.join()
            handler_thread.join()

    def _run_receiver(self) -> None:
        buffer = bytearray(1024)

        try:
            # Unityに接続
            print(f'Connecting to the Unity Simulator {self.send_address}.')
            pack_into('<4sI', self.send_data, 0, b'ETTX', 1)
            pack_into('<II', self.send_data, 24, 512, 512)
            self.sock.sendto(self.send_data, self.send_address)

            self.sock.recvfrom_into(buffer)
            self.recv_time = unpack_from('<Q', buffer, 16)[0]
            print('Connected to the Unity Simulator.')

            while self.running:
                # Unityからデータを受信する
                self.sock.recvfrom_into(buffer)

                # 状態を更新する
                with self.lock:
                    self.recv_time = unpack_from('<Q', buffer, 16)[0]
                    self.recv_buffer[:] = buffer

                # 計算スレッドに通知
                self.event.set()
        except socket.timeout:
            print('Connection is timeout.')
        finally:
            print('Closing the connection.')
            self.running = False
            self.event.set()
            self.sock.close()

    def _run_handler(self) -> None:
        try:
            while self.event.wait(self.timeout) and self.running:
                self.event.clear()

                # 時刻を確認する
                with self.lock:
                    proc_time = (self.recv_time // self.interval) * self.interval

                    if self.proc_time == proc_time:
                        continue

                    self.proc_time = proc_time
                    self.recv_data[:] = self.recv_buffer

                # 状態を更新する
                for fmt, offset, args in self.reserved_data:
                    pack_into(fmt, self.send_data, offset, *args)

                self.reserved_data.clear()
                self.handler()

                # データをUnityに送信する
                pack_into('<QQ', self.send_data, 8, self.recv_time, self.recv_time)
                self.sock.sendto(self.send_data, self.send_address)
        except StopIteration:
            print('Stopped by handler.')
        finally:
            self.running = False


class Hub(object):
    def set_led(self, color: int) -> None:
        _get_connector().write_values('<I', 32, color)

    def get_time(self) -> float:
        return _get_connector().recv_time / 1_000_000


class Motor(object):
    def __init__(self, port: int) -> None:
        self.port = port

    def get_count(self) -> int:
        return _get_connector().read_values('<i', 288 + self.port * 4)[0]

    def reset_count(self) -> None:
        _get_connector().write_values('<i', 68 + self.port * 4, 1)
        _get_connector().reserve_values('<i', 68 + self.port * 4, 0)

    def set_pwm(self, pwm: int) -> None:
        pwm = min(max(pwm, -100), 100)
        _get_connector().write_values('<i', 36 + self.port * 4, pwm)

    def set_brake(self, brake: bool) -> None:
        _get_connector().write_values('<I', 52 + self.port * 4, int(brake))


class ColorSensor(object):
    def get_brightness(self) -> int:
        return _get_connector().read_values('<i', 44)[0]

    def get_ambient(self) -> int:
        return _get_connector().read_values('<i', 36)[0]

    def get_color_number(self) -> int:
        return _get_connector().read_values('<i', 40)[0]

    def get_raw_color(self) -> Tuple[int, int, int]:
        return _get_connector().read_values('<iii', 48)  # type:ignore


class TouchSensor(object):
    def is_pressed(self) -> bool:
        return _get_connector().read_values('<i', 144)[0] != 0


class SonarSensor(object):
    def listen(self) -> bool:
        return _get_connector().read_values('<i', 124)[0] != 0

    def get_distance(self) -> int:
        return _get_connector().read_values('<i', 120)[0]


class GyroSensor(object):
    def reset(self) -> None:
        _get_connector().write_values('<i', 84, 1)
        _get_connector().reserve_values('<i', 84, 0)

    def get_angle(self) -> int:
        return _get_connector().read_values('<i', 60)[0]

    def get_angler_velocity(self) -> int:
        return _get_connector().read_values('<i', 64)[0]
