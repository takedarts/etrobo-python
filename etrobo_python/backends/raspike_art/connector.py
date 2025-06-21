import threading
import time
from typing import Callable

import libraspike_art_python as lib
from .device import stop_all_motors


class Connector(object):
    def __init__(
        self,
        handler: Callable[[], None],
        interval: float,
        port: str,
    ) -> None:
        '''SPIKEとの接続オブジェクトを初期化する。
        Args:
            handler (Callable[[], None]): 定期的に呼び出す関数。
            interval (float): 呼び出し間隔（秒）。
            port (str): SPIKEに接続するUSBポート。
        '''
        self.handler = handler
        self.interval = interval
        self.port = port
        self.terminated = False

    def run(self) -> None:
        # SPIKEへのUSB通信を開く
        desc = lib.raspike_open_usb_communication(self.port)
        if desc is None:
            raise Exception(f'USB port unable to open: {self.port}')

        # SPIKEとの通信を初期化する
        lib.raspike_prot_init(desc)

        self.terminated = False

        receiver_thread = threading.Thread(
            target=self.receive,
            name='Raspike_hub_receiver',
            daemon=True)
        receiver_thread.start()

        # 定期的にハンドラを実行する
        previous_time = 0

        try:
            while True:
                # 時刻を確認する
                interval_time = int(self.interval * 1000)
                current_time = int(time.time() * 1000)
                process_time = (current_time // interval_time) * interval_time

                # 前回の時刻との間隔が設定値より短いなら待機する
                if process_time == previous_time:
                    next_time = previous_time + interval_time
                    time.sleep((next_time - current_time) * 0.001)
                    continue

                # 制御処理を実行する
                previous_time = process_time
                self.handler()
        except StopIteration:
            print('Stopped by handler.')
        except KeyboardInterrupt:
            print('Interrupted by keyboard.')
            stop_all_motors()
        finally:
            self.terminated = True

        # 通信スレッドの終了を待機する
        receiver_thread.join()

    def receive(self) -> None:
        while not self.terminated:
            lib.raspike_prot_receive()
