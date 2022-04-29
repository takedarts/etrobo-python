# pythonでETロボコンに出場するためのミドルウェア

2022年度のETロボコンはリアル大会とシミュレーション大会の両方が行われることになりました。
リアル大会ではLEGO Mindstorms EV3かSPIKEの実機を制御するプログラムを開発することになりますし、シミュレーション大会ではシミュレータ上で動く制御プログラムを開発することになります。
もちろん、シミュレータでは実機の動きを再現していますので、シミュレータを使って制御プログラムの開発とデバッグを行い、実機でパラメータの調整を行う方法を使えば効率よく制御プログラムを開発できそうです。
シミュレータを使って実機用のプログラムを開発するという方法は大会運営側も想定していまして、公式の開発環境である[EV3RT](https://dev.toppers.jp/trac_user/ev3pf/wiki/WhatsEV3RT)を使うと、シミュレータと実機の両方で動作する制御プログラムを作れます。

それでは、pythonを使ってETロボコンに出場できるのかというと、実機であるEV3やSPIKEの制御を行うRaspberry Piではmicropythonが動きますので、実機を使うリアル大会の方は出場可能です。
また、シミュレータについても、[ETロボコンシミュレータのPython用クライアントライブラリ](https://github.com/YoshitakaAtarashi/ETroboSimController)がありますので、pythonを使ってシミュレーションすることも可能です。
ただし、シミュレータ環境とEV3環境で使用するpythonライブラリが異なりますので、シミュレータで開発した制御プログラムをEV3環境やSPIKE環境で動かすことはできませんでした。

そこで、**ETロボコンのシミュレータ環境とEV3環境の両方に対応した制御プログラムを開発するためのミドルウェア**を作りました。
それぞれの環境で共通となる部分をAPIとして公開し、それぞれの環境で異なる部分はバックエンドとして隠蔽する構成になっています。
そのため、このミドルウェアで開発した制御プログラムは、バックエンドを変更することにより、シミュレータ環境とEV3環境のどちらでも動作します。
詳しくは[samplesディレクトリ](samples)に置いてあるサンプルプログラムを参考にしてください。

現在のところ、シミュレータ環境とEV3環境のみをサポートしています。
SPIKE環境(RasPike環境)については実機を入手できましたら開発をはじめます。

## シミュレータ環境へのインストール
[ETロボコンのシミュレータ](https://github.com/ETrobocon/etrobo)をインストールし、その環境にpython（version 3.7以上）をインストールします。
その後、以下のコマンドを実行し、このミドルウェア`etrobo_python`をインストールします。
```
pip install git+https://github.com/takedarts/etrobo-python
```

## EV3環境へのインストール
準備中

## サンプルプログラム
```python
from etrobo_python import ColorSensor, ETRobo, Motor, SonarSensor, TouchSensor

# センサやモータを制御するプログラムは制御ハンドラとして登録します。
# 実行時に登録されたデバイスは、制御ハンドラに渡される引数を介して制御します。
# 以下の制御ハンドラは、センサやモータの観測値を出力するプログラムです。
def print_obtained_values(
    right_motor: Motor,
    left_motor: Motor,
    touch_sensor: TouchSensor,
    color_sensor: ColorSensor,
    sonar_sensor: SonarSensor,
) -> None:
    lines = [
        f'RightMotor: count={right_motor.get_count()}',
        f'LeftMotor: count={left_motor.get_count()}',
        f'TouchSensor: pressed={touch_sensor.is_pressed()}',
        f'ColorSensor: raw_color={color_sensor.get_raw_color()}',
        f'SonarSensor: listen={sonar_sensor.listen()}',
        f'SonarSensor: distance={sonar_sensor.get_distance()}',
    ]
    print('\n'.join(lines))

# シミュレータ環境で上記の制御ハンドラを実行するコードです。
# 制御対象のデバイスを登録し、上記の制御ハンドラを登録しています。
# backendを'pybricks'に変更することでEV3環境でも動作します。
(ETRobo(backend='simulator')
 .add_device('right_motor', device_type='motor', port='B')
 .add_device('left_motor', device_type='motor', port='C')
 .add_device('touch_sensor', device_type='touch_sensor', port='1')
 .add_device('color_sensor', device_type='color_sensor', port='2')
 .add_device('sonar_sensor', device_type='sonar_sensor', port='3')
 .add_handler(print_obtained_values)
 .dispatch(course='left', interval=0.1))
```

## TODO
- ジャイロセンサの追加
- HUBの追加（時刻・バッテリー電圧/電流のサポート）
- Bluetooth通信のサポート(EV3環境・SPIKE環境のみ)

