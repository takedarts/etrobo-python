try:
    from typing import Any, Callable, List, Tuple
except BaseException:
    pass


class ETRobo(object):
    def __init__(self, backend: str) -> None:
        '''ロボットを制御するためのオブジェクトを作成する。
        実行環境に適したバックエンドプログラムを指定すること。

        バックエンドプログラム:
            simulator: Unityのシミュレータ環境でのロボット制御
            pybricks: micropythonを使ったEV3ロボットの制御
            raspike: micropythonを使ったRasPikeロボットの制御（未実装）

        例:
            制御対象としてHUBタイプのデバイス「body」とmotorタイプのデバイス「motor1」を登録した場合、
            制御ハンドラには Hubオブジェクトが引数「body」として、Motorオブジェクトが引数「motor1」として渡される。

            def motor_handler(
                body: etrobo_python.Hub,
                motor1: etrobo_python.Motor,
            ) -> None:
                ...

            etrobo = ETRobo(backend)
            etrobo.add_hub('body')
            etrobo.add_device('motor1', device_type='motor', port='A')
            etrobo.add_handler(motor_handler)

        Args:
            backend: バックエンドプログラムの名前
        '''
        if backend == 'simulator':
            from .backends import simulator
            self.backend = simulator  # type: Any
        elif backend == 'pybricks':
            from .backends import pybricks
            self.backend = pybricks
        else:
            raise NotImplementedError(
                'Unsupported backend: {}'.format(backend))

        self.devices = []  # type: List[Tuple[str, Any]]
        self.handlers = []  # type: List[Callable[..., None]]

    def add_hub(self, name: str) -> 'ETRobo':
        '''制御対象としてHubを登録する。
        このメソッドが実行された場合、Hubオブジェクトが制御ハンドラに引数として渡される。

        Args:
            name: 制御オブジェクトの名前（handlerに渡される引数名）。

        Returns:
            このオブジェクト
        '''
        device = self.backend.create_device('hub', '')
        self.devices.append((name, device))
        return self

    def add_device(self, name: str, device_type: str, port: str) -> 'ETRobo':
        '''制御対象となるデバイスを登録する。
        ここで登録されたデバイスオブジェクトは制御ハンドラに引数として渡される。

        制御デバイスは以下のものをサポートしている:
            motor, color_sensor, touch_sensor, sonar_sensor

        Args:
            name: 制御オブジェクトの名前（handlerに渡される引数名）。
            device_type: 制御デバイスの種類
            port: 制御デバイスを接続しているポート

        Returns:
            このオブジェクト
        '''
        device = self.backend.create_device(device_type, port)
        self.devices.append((name, device))
        return self

    def add_handler(self, handler: Callable[..., None]) -> 'ETRobo':
        '''制御ハンドラを登録する。
        ここで登録された制御ハンドラは、制御プログラムの実行開始後に指定された間隔で実行される。

        Args:
            handler: 制御ハンドラ

        Returns:
            このオブジェクト
        '''
        self.handlers.append(handler)
        return self

    def dispatch(self, interval=0.01, **kwargs) -> None:
        '''制御プログラムを実行する。

        Args:
            interval: 制御ハンドラの実行間隔
            kwargs: バックエンドプログラムに渡される引数
        '''
        self.backend.create_dispatcher(
            devices=self.devices,
            handlers=self.handlers,
            interval=interval,
            **kwargs,
        ).dispatch()
