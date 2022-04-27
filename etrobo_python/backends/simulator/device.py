from typing import Any

from .devices.color_sensor import ColorSensorImpl
from .devices.motor import MotorImpl


def create_device(device_type: str, port: str) -> Any:
    if device_type == 'motor':
        return MotorImpl(port)
    if device_type == 'color_sensor':
        return ColorSensorImpl(port)
    else:
        raise NotImplementedError(f'Unsupported device: {device_type}')
