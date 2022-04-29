try:
    from typing import Tuple
except BaseException:
    pass


class Motor(object):
    def get_count(self) -> int:
        '''モーターの回転角度を返す。

        Returns:
          モーターの回転角度（単位はdeg）。
        '''
        raise NotImplementedError()

    def set_pwm(self, pwm: int) -> None:
        '''モーターのPWMの値を設定する。

        Args:
          pwm: PWMの設定値。
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
          環境光の測定値
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
        超音波信号が受信できていない場合の値は不定。

        Returns:
          超音波信号によって測定された物体までの距離（単位はmm）。
        '''
        raise NotImplementedError()
