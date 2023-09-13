## ETロボコン2023のためのpythonミドルウェア
このミドルウェアは以下の環境で動作するプログラムの開発をサポートします。

- Similator環境: シミュレータ上のロボットを制御するプログラムを開発できます。
- RasPike環境: 実機SPIKEを制御するプログラムを開発できます。
- RasPyke環境: 実機SPIKEを制御するプログラムを開発できます。
- Pybricks環境: 実機EV3を制御するプログラムを開発できます。

上記の環境でロボットの制御に必要となる手続きを共通のAPIとして実装していますので、上記のすべての環境で同様に動作するプログラムを開発することが可能です。ただし、制御パラメータの基準値はそれぞれの環境で異なりますので、それぞれの環境ごとにパラメータチューニングが必要となります。

RasPike環境とRasPyke環境は、どちらも実機SPIKEを制御するプログラムを開発できますが、SPIKEのPrime Hubを制御するプログラムが異なります。RasPike環境ではETロボコン公式のPrime Hub制御プログラムを使用しますが、RasPyke環境では独自実装のPrime Hub制御プログラムを使用します。詳細は[RasPyke環境(SPIKE)でのプログラム実行手順](https://github.com/takedarts/etrobo-python/wiki/install-raspyke)を参照してください。

### インストール方法
- [Windows環境でのインストール方法とプログラム実行手順](https://github.com/takedarts/etrobo-python/wiki/install-windows)
- [MacOSX環境でのインストール方法とプログラム実行手順](https://github.com/takedarts/etrobo-python/wiki/install-macosx)
- [RasPike環境(SPIKE)でのプログラム実行手順](https://github.com/takedarts/etrobo-python/wiki/install-raspike)
- [RasPyke環境(SPIKE)でのプログラム実行手順](https://github.com/takedarts/etrobo-python/wiki/install-raspyke)
- [Pybricks(EV3)でのプログラム実行手順](https://github.com/takedarts/etrobo-python/wiki/install-ev3)

### ミドルウェアの使い方
- [チュートリアル](https://github.com/takedarts/etrobo-python/wiki/tutorial)
- [APIドキュメント](https://takedarts.github.io/etrobo-python/etrobo_python.html)

## これは何？
昨年度に引き続き、2023年度のETロボコンもリアル大会とシミュレーション大会の両方が開催されることになりました。
リアル大会ではLEGO SPIKE PrimeかLEGO Mindstorms EV3の実機を制御するプログラムを開発することになりますが、大会運営よりUnityを使ったシミュレータが公開されていますので、シミュレータを使って制御プログラムの開発とデバッグを行い、実機でパラメータの調整を行う方法を使えば効率よく制御プログラムを開発できそうです。
シミュレータを使って実機用のプログラムを開発するという方法は大会運営側も想定していまして、公式の開発環境である[EV3RT](https://dev.toppers.jp/trac_user/ev3pf/wiki/WhatsEV3RT)を使った場合はシミュレータと実機の両方で動作する制御プログラムを開発できます。
ただ、EV3RTはC/C++での開発のみをサポートしていますので、pythonを使った制御プログラムを開発できません。

ただ、実機であるEV3やSPIKEの制御を行うRaspberry Piではmicropythonが動作しますので、実機を使うリアル大会についてはpythonを用いて開発した制御プログラムで出場できます。
また、シミュレータについても、[ETロボコンシミュレータのPython用クライアントライブラリ](https://github.com/YoshitakaAtarashi/ETroboSimController)が公開されていますので、pythonを使って開発した制御プログラムをシミュレータ環境で実行することも可能です。
しかし、シミュレータ環境とEV3環境で使用するpythonライブラリが異なりますので、シミュレータで開発した制御プログラムをEV3環境やSPIKE環境で動かすことはできませんでした。

そこで、**シミュレータ環境とEV3環境の両方に対応した制御プログラムをpythonで開発するためのミドルウェア**を作りました。
それぞれの環境で共通となる部分をAPIとして公開し、それぞれの環境で異なる部分はバックエンドとして隠蔽する構成になっています。
そのため、このミドルウェアで開発した制御プログラムは、バックエンドを変更することにより、シミュレータ環境とEV3環境のどちらでも動作します。
詳しくは[samplesディレクトリ](https://github.com/takedarts/etrobo-python/tree/main/samples)に置いてあるサンプルプログラムを参考にしてください。

## サンプルプログラム
```python
from etrobo_python import (ColorSensor, ETRobo, GyroSensor, Hub, Motor,
                           SonarSensor, TouchSensor)

# センサやモータを制御するプログラムは制御ハンドラとして登録します。
# 実行時に登録されたデバイスは、制御ハンドラに渡される引数を介して制御します。
# 以下の制御ハンドラは、センサやモータの観測値を出力するプログラムです。
def print_obtained_values(
    hub: Hub,
    right_motor: Motor,
    left_motor: Motor,
    touch_sensor: TouchSensor,
    color_sensor: ColorSensor,
    sonar_sensor: SonarSensor,
    gyro_sensor: GyroSensor,
) -> None:
    lines = [
        'Hub: battery_voltage={}'.format(hub.get_battery_voltage()),
        'RightMotor: count={}'.format(right_motor.get_count()),
        'LeftMotor: count={}'.format(left_motor.get_count()),
        'TouchSensor: pressed={}'.format(touch_sensor.is_pressed()),
        'ColorSensor: raw_color={}'.format(color_sensor.get_raw_color()),
        'SonarSensor: distance={}'.format(sonar_sensor.get_distance()),
        'GyroSensor: velocity={}'.format(gyro_sensor.get_angler_velocity()),
    ]
    print('\n'.join(lines))

# シミュレータ環境で上記の制御ハンドラを実行するコードです。
# 制御対象のデバイスを登録し、上記の制御ハンドラを登録しています。
# backendを'pybricks'に変更することでEV3環境でも動作します。
(ETRobo(backend='simulator')
 .add_hub(name='hub')
 .add_device('right_motor', device_type='motor', port='B')
 .add_device('left_motor', device_type='motor', port='C')
 .add_device('touch_sensor', device_type='touch_sensor', port='1')
 .add_device('color_sensor', device_type='color_sensor', port='2')
 .add_device('sonar_sensor', device_type='sonar_sensor', port='3')
 .add_device('gyro_sensor', device_type='gyro_sensor', port='4')
 .add_handler(print_obtained_values)
 .dispatch(course='left', interval=0.1))
```
