from etrobo_python import ColorSensor, ETRobo, Motor, SonarSensor, TouchSensor


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
        # f'ColorSensor: brightness={color_sensor.get_brightness()}',
        # f'ColorSensor: ambient={color_sensor.get_ambient()}',
        f'ColorSensor: raw_color={color_sensor.get_raw_color()}',
        f'SonarSensor: listen={sonar_sensor.listen()}',
        f'SonarSensor: distance={sonar_sensor.get_distance()}',
    ]

    print('\n'.join(lines))


def run(backend: str) -> None:
    (ETRobo(backend='simulator')
     .add_device('right_motor', device_type='motor', port='B')
     .add_device('left_motor', device_type='motor', port='C')
     .add_device('touch_sensor', device_type='touch_sensor', port='1')
     .add_device('color_sensor', device_type='color_sensor', port='2')
     .add_device('sonar_sensor', device_type='sonar_sensor', port='3')
     .add_handler(print_obtained_values)
     .dispatch(course='left', interval=0.1))
