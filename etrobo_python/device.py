try:
    from typing import Tuple
except BaseException:
    pass


class Hub(object):
    def set_led(self, color: str) -> None:
        '''LEDの発光色を設定する。
        発光色の名前は black, red, green, orange のいずれか。

        Args:
            color: LEDの発光色の名前。
        '''
        raise NotImplementedError()

    def get_time(self) -> float:
        '''現在時刻を返す。
        シミュレータ環境の場合は、シミュレータ上での時刻を返す。

        Returns:
            現在時刻（単位は秒）。
        '''
        raise NotImplementedError()

    def get_battery_voltage(self) -> int:
        '''バッテリーの出力電圧を返す。
        シミュレータ環境の場合は常に8000mVを返す。

        Return:
            バッテリーの出力電圧（単位はmV）。
        '''
        raise NotImplementedError()

    def get_battery_current(self) -> int:
        '''バッテリーの出力電流を返す。
        シミュレータ環境の場合は常に200mAを返す。

        Return:
            バッテリーの出力電流（単位はmA）。
        '''
        raise NotImplementedError()

    def play_speaker_tone(self, frequency: int, duration: float) -> None:
        '''スピーカーからビープ音を鳴らす。
        シミュレータ環境の場合は何もしない。

        Args:
            frequency: ビープ音の周波数。
            duration: 音を鳴らす時間（単位は秒）。
        '''
        raise NotImplementedError()

    def set_speaker_volume(self, volume: int) -> None:
        '''スピーカーの音量を設定する。
        シミュレータ環境の場合は何もしない。

        Args:
            volume: スピーカーの音量（単位は%）。
        '''
        raise NotImplementedError()


class Motor(object):
    def get_count(self) -> int:
        '''モーターの回転角度を返す。

        Returns:
            モーターの回転角度（単位はdeg）。
        '''
        raise NotImplementedError()

    def reset_count(self) -> None:
        '''モータの回転角度の値を0に設定する。
        '''
        raise NotImplementedError()

    def set_power(self, power: int) -> None:
        '''モーターの回転力を設定する。

        Args:
            power: モーターの回転力。
        '''
        raise NotImplementedError()

    def set_brake(self, brake: bool) -> None:
        '''ブレーキモードを設定する。

        Args:
            brake: Trueを指定した場合はブレーキモードとなる。
        '''
        raise NotImplementedError()


class ColorSensor(object):
    def get_brightness(self) -> int:
        '''反射光の測定値を返す。

        Returns:
            反射光の測定値。
        '''
        raise NotImplementedError()

    def get_ambient(self) -> int:
        '''環境光の測定値を返す。

        Returns:
            環境光の測定値。
        '''
        raise NotImplementedError()

    def get_raw_color(self) -> Tuple[int, int, int]:
        '''RGBの測定値を返す。

        Returns:
            測定された(Red, Green, Blue)の値。
        '''
        raise NotImplementedError()


class TouchSensor(object):
    def is_pressed(self) -> bool:
        '''タッチセンサの測定値を返す。

        Returns:
            タッチセンサが押されていればTrue。
        '''
        raise NotImplementedError()


class SonarSensor(object):
    def listen(self) -> bool:
        '''超音波信号の受信状況を返す。

        Returns:
            超音波信号を受信できていればTrue。
        '''
        raise NotImplementedError()

    def get_distance(self) -> int:
        '''超音波信号によって測定された物体までの距離を返す。

        Returns:
            超音波信号によって測定された物体までの距離（単位はmm）。
        '''
        raise NotImplementedError()


class GyroSensor(object):
    def reset(self) -> None:
        '''ジャイロセンサの角速度を0度にセットする。
        '''
        raise NotImplementedError()

    def get_angle(self) -> int:
        '''ジャイロセンサで測定された現在の角度を返す。

        Returns:
            測定された現在の角度（単位はdeg）。
        '''
        raise NotImplementedError()

    def get_angler_velocity(self) -> int:
        '''ジャイロセンサで測定された角速度を返す。

        Returns:
            測定された角速度（単位はdeg）。
        '''
        raise NotImplementedError()
