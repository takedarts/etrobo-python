from etrobo_python import (ColorSensor, ETRobo, GyroSensor, Motor, SonarSensor,
                           TouchSensor)


def print_obtained_values_in_simulation(
    right_motor: Motor,
    left_motor: Motor,
    touch_sensor: TouchSensor,
    color_sensor: ColorSensor,
    sonar_sensor: SonarSensor,
    gyro_sensor: GyroSensor,
) -> None:
    lines = [
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
    right_motor: Motor,
    left_motor: Motor,
    touch_sensor: TouchSensor,
    color_sensor: ColorSensor,
    sonar_sensor: SonarSensor,
    gyro_sensor: GyroSensor,
) -> None:
    lines = [
        'RightMotor: count={}'.format(right_motor.get_count()),
        'LeftMotor: count={}'.format(left_motor.get_count()),
        'TouchSensor: pressed={}'.format(touch_sensor.is_pressed()),
        'ColorSensor: raw_color={}'.format(color_sensor.get_raw_color()),
        'SonarSensor: distance={}'.format(sonar_sensor.get_distance()),
        'GyroSensor: velocity={}'.format(gyro_sensor.get_angler_velocity()),
    ]

    print('\n'.join(lines))


def run(backend: str) -> None:
    if backend == 'simulator':
        print_obtained_values = print_obtained_values_in_simulation
    else:
        print_obtained_values = print_obtained_values_in_realworld

    (ETRobo(backend=backend)
     .add_device('right_motor', device_type='motor', port='B')
     .add_device('left_motor', device_type='motor', port='C')
     .add_device('touch_sensor', device_type='touch_sensor', port='1')
     .add_device('color_sensor', device_type='color_sensor', port='2')
     .add_device('sonar_sensor', device_type='sonar_sensor', port='3')
     .add_device('gyro_sensor', device_type='gyro_sensor', port='4')
     .add_handler(print_obtained_values)
     .dispatch(course='left', interval=0.1))