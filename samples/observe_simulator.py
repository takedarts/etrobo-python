import argparse

from etrobo_python import ColorSensor, ETRobo, GyroSensor, Hub, Motor, SonarSensor, TouchSensor


def print_obtained_values_in_simulation(
    hub: Hub,
    right_motor: Motor,
    left_motor: Motor,
    touch_sensor: TouchSensor,
    color_sensor: ColorSensor,
    sonar_sensor: SonarSensor,
    gyro_sensor: GyroSensor,
) -> None:
    lines = [
        'Hub: time={}'.format(hub.get_time()),
        'Hub: battery_voltage={}'.format(hub.get_battery_voltage()),
        'Hub: battery_current={}'.format(hub.get_battery_current()),
        'RightMotor: count={}'.format(right_motor.get_count()),
        'LeftMotor: count={}'.format(left_motor.get_count()),
        'TouchSensor: pressed={}'.format(touch_sensor.is_pressed()),
        'ColorSensor: brightness={}'.format(color_sensor.get_brightness()),
        'ColorSensor: ambient={}'.format(color_sensor.get_ambient()),
        'ColorSensor: raw_color={}'.format(color_sensor.get_raw_color()),
        'SonarSensor: listen={}'.format(sonar_sensor.listen()),
        'SonarSensor: distance={}'.format(sonar_sensor.get_distance()),
        'GyroSensor: angle={}'.format(gyro_sensor.get_angle()),
        'GyroSensor: velocity={}'.format(gyro_sensor.get_angler_velocity()),
    ]

    print('\n'.join(lines))


def print_obtained_values_in_realworld(
    hub: Hub,
    right_motor: Motor,
    left_motor: Motor,
    touch_sensor: TouchSensor,
    color_sensor: ColorSensor,
    sonar_sensor: SonarSensor,
    gyro_sensor: GyroSensor,
) -> None:
    lines = [
        'Hub: time={}'.format(hub.get_time()),
        'Hub: battery_voltage={}'.format(hub.get_battery_voltage()),
        'Hub: battery_current={}'.format(hub.get_battery_current()),
        'RightMotor: count={}'.format(right_motor.get_count()),
        'LeftMotor: count={}'.format(left_motor.get_count()),
        'TouchSensor: pressed={}'.format(touch_sensor.is_pressed()),
        'ColorSensor: raw_color={}'.format(color_sensor.get_raw_color()),
        'SonarSensor: distance={}'.format(sonar_sensor.get_distance()),
        'GyroSensor: angle={}'.format(gyro_sensor.get_angle()),
        'GyroSensor: velocity={}'.format(gyro_sensor.get_angler_velocity()),
    ]

    print('\n'.join(lines))


def run(backend: str, **kwargs) -> None:
    if backend == 'simulator':
        print_obtained_values = print_obtained_values_in_simulation
    else:
        print_obtained_values = print_obtained_values_in_realworld

    (ETRobo(backend=backend)
     .add_hub(name='hub')
     .add_device(name='right_motor', device_type=Motor, port='B')
     .add_device(name='left_motor', device_type=Motor, port='C')
     .add_device(name='touch_sensor', device_type=TouchSensor, port='1')
     .add_device(name='color_sensor', device_type=ColorSensor, port='2')
     .add_device(name='sonar_sensor', device_type=SonarSensor, port='3')
     .add_device(name='gyro_sensor', device_type=GyroSensor, port='4')
     .add_handler(print_obtained_values)
     .dispatch(course='left', interval=0.1, **kwargs))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--logfile', type=str, default=None, help='Path to log file')
    args = parser.parse_args()
    run(backend='simulator', logfile=args.logfile)
