from etrobo_python.device import (ColorSensor, Device, GyroSensor, Hub, Motor, SonarSensor,
                                  TouchSensor)

try:
    from pathlib import Path
    from typing import List, Optional, Tuple, Union
except BaseException:
    pass


def _get_type_name(device: Device) -> str:
    if isinstance(device, Hub):
        return 'hub'
    elif isinstance(device, Motor):
        return 'motor'
    elif isinstance(device, ColorSensor):
        return 'color_sensor'
    elif isinstance(device, TouchSensor):
        return 'touch_sensor'
    elif isinstance(device, SonarSensor):
        return 'sonar_sensor'
    elif isinstance(device, GyroSensor):
        return 'gyro_sensor'
    else:
        raise ValueError('Invalid device class: {}'.format(device.__class__.__name__))


def _get_binary_length(device_type: str) -> int:
    if device_type == 'hub':
        return 5
    elif device_type == 'motor':
        return 4
    elif device_type == 'color_sensor':
        return 5
    elif device_type == 'touch_sensor':
        return 1
    elif device_type == 'sonar_sensor':
        return 2
    elif device_type == 'gyro_sensor':
        return 4
    else:
        raise ValueError('Invalid device type: {}'.format(device_type))


class LogReader(object):
    '''ログデータをファイルから読み込むためのクラス。
    LogWriterで作成されたログファイルを読み込み、デバイスごとに分割したデータを取得する。

    ログファイルのフォーマットについては、LogWriterの説明を参照。

    Args:
        path: ログファイルのパス
    '''

    def __init__(self, path: Union[str, Path]) -> None:
        self.path = str(path)

        self.reader = open(self.path, 'rb')
        size = int.from_bytes(self.reader.read(2), 'big')

        tokens = self.reader.read(size).decode('utf-8').split(',')
        name_types = [token.split(':') for token in tokens]
        self.devices = [(name, device_type) for name, device_type in name_types]

        lengths = [_get_binary_length(device_type) for _, device_type in self.devices]
        self.offsets = [sum(lengths[:i]) for i in range(len(lengths) + 1)]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.reader.close()

    def get_devices(self) -> List[Tuple[str, str]]:
        '''ログファイルに記録されているデバイスのリストを取得する。

        Returns:
            デバイスのリスト。
            デバイスは(変数名, デバイスタイプ)のタプルで表現される。
        '''
        return self.devices

    def read(self) -> Optional[List[bytes]]:
        '''ログファイルからデバイスごとに分割したデータを取得する。

        Returns:
            デバイスごとに分割したデータのリスト。
            デバイスのリストの順番はget_devices()で取得したものと同じ。
            ログデータが壊れている（と思われる）場合はNoneを返す。
        '''
        buffer = self.reader.read(self.offsets[-1])

        if len(buffer) < self.offsets[-1]:
            return None

        return [buffer[b:e] for b, e in zip(self.offsets[:-1], self.offsets[1:])]

    def close(self) -> None:
        '''ログファイルを閉じる。'''
        self.reader.close()

    def __iter__(self):
        return self

    def __next__(self) -> List[bytes]:
        data = self.read()
        if data is None:
            raise StopIteration()
        return data


class LogWriter(object):
    '''ログデータをファイルに書き込むためのクラス。
    モータやセンサから取得したデータをログファイルに書き込む。

    **ログファイルのフォーマット**

    .. code-block:: none

        デバイスのリストの文字列のバイト数(2バイト)
        デバイスのリストのUTF-8文字列(変数名1:デバイスタイプ1,変数名2:デバイスタイプ2,...)
        以下、それぞれのデバイスから取得されたデータを時刻順に並べたもの
          - Hub: 時刻(4バイト), ボタンの状態(1バイト)
            ボタンの状態: 左ボタン=0x01, 右ボタン=0x02, 上ボタン=0x04, 下ボタン=0x08
          - Motor: モーターの回転角度(4バイト)
          - ColorSensor: brightness(1バイト), ambient(1バイト), raw_color(1バイト * 3)
          - TouchSensor: タッチセンサの状態(1バイト)
          - SonarSensor: 距離(2バイト)
          - GyroSensor: 角度(2バイト), 角速度(2バイト)

    **ログデータの例**

    ログデータの取得対象となるデバイスがleft_motor:motor・right_motor:motor・color_sensor:color_sensorの場合、
    以下のログデータが作成される。

    .. code-block:: none

        0x003c (デバイスリストの文字列のバイト数)
        "left_motor:motor,right_motor:motor,color_sensor:color_sensor" (UTF-8文字列)
        (left_motorの回転角度, right_motorの回転角度, color_sensorのbrightness, ambient, raw_color)
        (left_motorの回転角度, right_motorの回転角度, color_sensorのbrightness, ambient, raw_color)
        (left_motorの回転角度, right_motorの回転角度, color_sensorのbrightness, ambient, raw_color)
        ...

    Args:
        path: ログファイルのパス
        devices: ログファイルに記録するデバイスのリスト。
            デバイスは(変数名, デバイスオブジェクト)のタプルで指定する。
    '''

    def __init__(
        self,
        path: Union[str, Path],
        devices: List[Tuple[str, Device]],
    ) -> None:
        self.path = str(path)
        self.writer = open(self.path, 'wb')

        device_types = [_get_type_name(device) for _, device in devices]
        lengths = [_get_binary_length(device_type) for device_type in device_types]
        self.offsets = [sum(lengths[:i]) for i in range(len(lengths) + 1)]
        self.buffer = bytearray(sum(lengths))

        name_types = ['{}:{}'.format(name, _get_type_name(device)) for name, device in devices]
        binary = ','.join(name_types).encode('utf-8')
        self.writer.write(int.to_bytes(len(binary), 2, 'big'))
        self.writer.write(binary)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.writer.close()

    def write(self, devices: List[Device]) -> None:
        '''デバイスから取得したデータをログファイルに書き込む。

        Args:
            devices: ログファイルに記録するデバイスのリスト。
        '''
        for offset, device in zip(self.offsets, devices):
            binary = device.get_log()
            self.buffer[offset:offset + len(binary)] = binary

        self.writer.write(self.buffer)

    def flush(self) -> None:
        '''ログファイルに書き込みバッファの内容を書き込む。'''
        self.writer.flush()

    def close(self) -> None:
        '''ログファイルを閉じる。'''
        self.writer.close()
