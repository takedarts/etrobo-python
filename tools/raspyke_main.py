# LEGO type:standard slot:3 autostart
import utime
import hub
import ubinascii
import sys

'''
送信（観測）データ: Base64でエンコードした文字列を送受信する
Base64でエンコードした文字列は 0x66, 0x33 で始まる
[0-1] magic number (0x7f, 0x70) (12bit)
[1] checksum (4bit)
[2-4] time
[5-13] motor count (A, B, C) (3 bytes each)
[14-16] one of ambient, color, reflect, rgb (r, g, b)
[17-17] ultrasonic
[18-20] gyro (angle, speed) (12bit each)
[21-23] system info  - number(1byte) value(2bytes)
  0: buttun status (connect=0x01, left=0x02, right=0x04, center=0x08)
  1: battery voltage
  2: battery current

受信（命令）データ: バイナリデータを送受信する
[0] magic number (0x7f)
[1] checksum
[2-2] command
[3-6] value

command: number - value
0x00: ping - time reset (1byte), interval (10-200 msec) (3bytes)
0x01: sound - frequency (Hz), duration (msec) (2bytes each)
0x02: volume - volume (0-10)
0x03: led - color (0-10)
0x04: screen - number (0-20)
0x11: motor A power - power
0x12: motor A brake - 0/1
0x13: motor A reset - 0
0x21: motor B power - power
0x22: motor B brake - 0/1
0x23: motor B reset - 0
0x31: motor C power - power
0x32: motor C brake - 0/1
0x33: motor C reset - 0
0x41: color sensor mode - mode (0=ambient, 1=color, 2=reflect, 3=rgb)
0x51: gyro reset - 0
'''

# 使用ポート
PORT_MOTOR_A = 'A'
PORT_MOTOR_B = 'B'
PORT_MOTOR_C = 'E'
PORT_COLOR_SENSOR = 'C'
PORT_ULTRASONIC_SENSOR = 'F'
PORT_SERIAL = 'D'

# モーターの回転を逆にして指定したい場合、以下に-1を設定する
INVERT_MOTOR_A = 1
INVERT_MOTOR_B = 1
INVERT_MOTOR_C = -1

# タイムアウト時間（ミリ秒）
TIMEOUT_MS = 1000

# 送受信データに含まれるマジックナンバー
MAGIC_NUMBER = 0x7f

# スクリーンに表示する番号のイメージデータ
SCREEN_IMAGES = [
    hub.Image('09990:09090:09090:09090:09990:'),
    hub.Image('00900:00900:00900:00900:00900:'),
    hub.Image('09990:00090:09990:09000:09990:'),
    hub.Image('09990:00090:09990:00090:09990:'),
    hub.Image('09090:09090:09990:00090:00090:'),
    hub.Image('09990:09000:09990:00090:09990:'),
    hub.Image('09990:09000:09990:09090:09990:'),
    hub.Image('09990:09090:09090:00090:00090:'),
    hub.Image('09990:09090:09990:09090:09990:'),
    hub.Image('09990:09090:09990:00090:00090:'),
    hub.Image('10999:10909:10909:10909:10999:'),
    hub.Image('10090:10090:10090:10090:10090:'),
    hub.Image('10999:10009:10999:10900:10999:'),
    hub.Image('10999:10009:10999:10009:10999:'),
    hub.Image('10909:10909:10999:10009:10009:'),
    hub.Image('10999:10900:10999:10009:10999:'),
    hub.Image('10999:10900:10999:10909:10999:'),
    hub.Image('10999:10909:10909:10009:10009:'),
    hub.Image('10999:10909:10999:10909:10999:'),
    hub.Image('10999:10909:10999:10009:10009:'),
    hub.Image.CHESSBOARD,
]


class Motor(object):
    def __init__(self, port, invert):
        self.device = port.device
        self.motor = port.motor
        self.invert = invert

        self.device.mode(2)

    def set_power(self, power):
        self.motor.pwm(self.invert * power)

    def set_brake(self, brake):
        if brake == 1:
            self.motor.brake()
        else:
            self.motor.float()

    def reset_count(self):
        self.motor.preset(0)

    def get_count(self):
        return self.invert * self.device.get()[0]


class ColorSensor(object):
    def __init__(self, port):
        self.device = port.device
        self.mode = 0  # 0=ambient, 1=color, 2=reflect, 3=rgb
        self.device.mode(2)

    def set_mode(self, mode):
        if self.mode == mode:
            return

        self.mode = mode

        if self.mode == 0:
            self.device.mode(2)
        elif self.mode == 1:
            self.device.mode(0)
        elif self.mode == 2:
            self.device.mode(1)
        elif self.mode == 3:
            self.device.mode(5)

    def get_values(self):
        values = self.device.get()

        # ambient, color, reflectモード
        if self.mode == 0 or self.mode == 1 or self.mode == 2:
            if values is not None and values[0] is not None:
                return values[0], 0, self.mode
            else:
                return 0, 0, self.mode
        # rgbモード
        elif self.mode == 3:
            if values is not None and len(values) >= 3 and values[0] is not None:
                red = min(values[0] // 4, 254) + 1
                green = min(values[1] // 4, 254) + 1
                blue = min(values[2] // 4, 254) + 1
                return red, green, blue
            else:
                return 1, 1, 1
        else:
            return 0, 0, 255


class UltrasonicSensor(object):
    def __init__(self, port):
        self.device = port.device
        self.device.mode(5, b'\t\t\t\t')
        self.device.mode(0)

    def get_value(self):
        values = self.device.get()
        if values is not None and values[0] is not None:
            return values[0]
        else:
            return 255


class Device(object):
    def __init__(self):
        # ジャイロセンサの状態を初期化する
        hub.motion.align_to_model(hub.FRONT, hub.TOP)
        hub.motion.yaw_pitch_roll(0)
        utime.sleep(1)

        # デバイスの準備ができるまで待つ
        while True:
            if (
                getattr(hub.port, PORT_MOTOR_A).motor is not None
                and getattr(hub.port, PORT_MOTOR_B).motor is not None
                and getattr(hub.port, PORT_MOTOR_C).motor is not None
                and getattr(hub.port, PORT_COLOR_SENSOR).device is not None
                and getattr(hub.port, PORT_ULTRASONIC_SENSOR).device is not None
            ):
                break

        # デバイス制御用のオブジェクトを作成する
        self.motor_a = Motor(getattr(hub.port, PORT_MOTOR_A), INVERT_MOTOR_A)
        self.motor_b = Motor(getattr(hub.port, PORT_MOTOR_B), INVERT_MOTOR_B)
        self.motor_c = Motor(getattr(hub.port, PORT_MOTOR_C), INVERT_MOTOR_C)
        self.color_sensor = ColorSensor(getattr(hub.port, PORT_COLOR_SENSOR))
        self.ultrasonic_sensor = UltrasonicSensor(getattr(hub.port, PORT_ULTRASONIC_SENSOR))

    def execute(self, command, value):
        if command == 0x00:
            utime.sleep_ms(value)
        elif command == 0x01:
            freq = value >> 16
            duration = value & 0xffff
            hub.sound.beep(freq, duration)
        elif command == 0x02:
            hub.sound.volume(value)
        elif command == 0x03 and 0 <= value < 10:
            hub.led(value)
        elif command == 0x04 and value < len(SCREEN_IMAGES):
            hub.display.show(SCREEN_IMAGES[value])
        elif command == 0x11:
            self.motor_a.set_power(value)
        elif command == 0x12:
            self.motor_a.set_brake(value)
        elif command == 0x13:
            self.motor_a.reset_count()
        elif command == 0x21:
            self.motor_b.set_power(value)
        elif command == 0x22:
            self.motor_b.set_brake(value)
        elif command == 0x23:
            self.motor_b.reset_count()
        elif command == 0x31:
            self.motor_c.set_power(value)
        elif command == 0x32:
            self.motor_c.set_brake(value)
        elif command == 0x33:
            self.motor_c.reset_count()
        elif command == 0x41:
            self.color_sensor.set_mode(value)
        elif command == 0x51:
            hub.motion.yaw_pitch_roll(0)

    def apply(self, send_buffer, report_number, current_time):
        process_time = current_time
        motor_a_count = self.motor_a.get_count()
        motor_b_count = self.motor_b.get_count()
        motor_c_count = self.motor_c.get_count()
        color0, color1, color2 = self.color_sensor.get_values()
        ultrasonic = self.ultrasonic_sensor.get_value()
        gyro_angle = hub.motion.yaw_pitch_roll()[0]
        gyro_speed = hub.motion.gyroscope()[2]
        gyro_value = (gyro_angle & 0xfff) << 12 | gyro_speed & 0xfff

        if report_number == 0:
            report_value = (
                int(hub.button.connect.is_pressed()) << 0
                | int(hub.button.left.is_pressed()) << 1
                | int(hub.button.right.is_pressed()) << 2
                | int(hub.button.center.is_pressed()) << 3
            )
        elif report_number == 1:
            report_value = hub.battery.voltage()
        elif report_number == 2:
            report_value = hub.battery.current()
        else:
            report_value = 0

        send_buffer[0] = 0x7f
        send_buffer[1] = 0x70
        send_buffer[2:5] = int.to_bytes(process_time & 0xffffff, 3, 'big')
        send_buffer[5:8] = int.to_bytes(motor_a_count & 0xffffff, 3, 'big')
        send_buffer[8:11] = int.to_bytes(motor_b_count & 0xffffff, 3, 'big')
        send_buffer[11:14] = int.to_bytes(motor_c_count & 0xffffff, 3, 'big')
        send_buffer[14] = color0 & 0xff
        send_buffer[15] = color1 & 0xff
        send_buffer[16] = color2 & 0xff
        send_buffer[17] = ultrasonic & 0xff
        send_buffer[18:21] = int.to_bytes(gyro_value & 0xffffff, 3, 'big')
        send_buffer[21] = report_number & 0xff
        send_buffer[22:24] = int.to_bytes(report_value & 0xffff, 2, 'big')

        send_buffer[1] |= sum(send_buffer[2:]) & 0x0f


class Communicator(object):
    def __init__(self):
        # 送受信バッファを作成する
        self.recv_buffer = bytearray(7)
        self.send_buffer = bytearray(24)
        self.send_buffer[0] = MAGIC_NUMBER

        # シリアル通信オブジェクトを作成する
        self.serial = getattr(hub.port, PORT_SERIAL)
        self.serial.mode(hub.port.MODE_FULL_DUPLEX)
        utime.sleep(1)
        self.serial.baud(115_200)

        # シリアル通信の受信バッファをクリアする
        while self.serial.read(self.recv_buffer) != 0:
            pass

        # 基準時間
        self.base_time = 0
        # 最後に命令データを受信した時間
        self.receive_time = 0

        # 観測データを送信する間隔（ミリ秒）
        self.report_intereval = 10
        # 最後に観測データを送信した時間
        self.report_time = 0
        # 観測データとして送信する番号
        self.report_number = 0

    def communicate(self, device):
        while True:
            # 切断中なら0.5秒間スリープする
            if self.base_time == 0:
                utime.sleep_ms(500)

            # 現在時刻を取得する
            current_time = utime.ticks_ms()

            # 命令データを受信する
            if self._receive():
                self.receive_time = current_time

                # 命令番号と値を取り出す
                command = self.recv_buffer[2]
                value = int.from_bytes(self.recv_buffer[3:7], 'big')
                if value >= 0x80000000:
                    value -= 0x100000000

                # PING命令を受信した場合
                if command == 0x00:
                    self.report_intereval = min(max(value & 0xff, 10), 200)
                    if value >> 24 == 0x01:
                        self.base_time = current_time
                        hub.display.show(hub.Image.CHESSBOARD)
                # それ以外の命令を受信した場合はその命令を実行する
                else:
                    device.execute(command, value)

                # 次の命令を受信する（命令の受信を優先する）
                continue

            # 最後に命令データを受信してから一定時間経過していたら切断状態にする
            if current_time - self.receive_time >= TIMEOUT_MS:
                self.base_time = 0
                hub.display.show(hub.Image.SQUARE_SMALL)

            # 観測データを送信する
            if current_time - self.report_time >= self.report_intereval:
                self.report_time = current_time
                self.report_number = (self.report_number + 1) % 3
                device.apply(self.send_buffer, self.report_number, current_time - self.base_time)
                self._send()

    def _receive(self):
        # データを受信する
        size = self.serial.read(self.recv_buffer)
        if size == 0:
            return False

        while size < len(self.recv_buffer):
            buffer = self.serial.read(len(self.recv_buffer) - size)
            if len(buffer) == 0:
                continue

            for i in range(len(buffer)):
                self.recv_buffer[size + i] = buffer[i]

            size += len(buffer)

        # マジックナンバーをチェックする
        while self.recv_buffer[0] != MAGIC_NUMBER:
            offset = -1
            for i, v in enumerate(self.recv_buffer[:size]):
                if v == MAGIC_NUMBER:
                    offset = i
                    break

            if offset < 0:
                return False

            for i in range(len(self.recv_buffer) - offset):
                self.recv_buffer[i] = self.recv_buffer[i + offset]

            size -= offset

        # 不足しているデータを受信する
        while size < len(self.recv_buffer):
            buffer = self.serial.read(len(self.recv_buffer) - size)
            if len(buffer) == 0:
                continue

            for i in range(len(buffer)):
                self.recv_buffer[size + i] = buffer[i]

            size += len(buffer)

        # チェックサムを確認する
        if self.recv_buffer[1] != sum(self.recv_buffer[2:]) & 0xff:
            return False

        return True

    def _send(self):
        # base64に変換する
        data = ubinascii.b2a_base64(self.send_buffer)[:-1].decode('ascii')

        # 送信する
        offset = 0

        while offset < len(data):
            size = self.serial.write(data[offset:offset + 32])
            if size > 0:
                offset += size


def main():
    try:
        # 時計アニメーションを表示する
        hub.display.show(hub.Image.ALL_CLOCKS, delay=200, clear=True, wait=False, loop=True, fade=0)

        # オブジェクトを作成する
        device = Device()
        communicator = Communicator()

        # 四角形を表示する
        hub.display.show(hub.Image.SQUARE_SMALL)

        # メインループ
        communicator.communicate(device)
    except BaseException as ex:
        hub.display.show(hub.Image.NO)
        with open('error.log', 'w') as f:
            sys.print_exception(ex, f)
        raise ex


main()
