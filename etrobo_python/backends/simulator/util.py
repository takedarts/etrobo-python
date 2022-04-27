from typing import Any


import etrobosim.ev3api as ev3


def get_ev3port(port: str) -> Any:
    if port == 'A':
        return ev3.ePortM.PORT_A
    elif port == 'B':
        return ev3.ePortM.PORT_B
    elif port == 'C':
        return ev3.ePortM.PORT_C
    elif port == 'D':
        return ev3.ePortM.PORT_D
    elif port == '1':
        return ev3.ePortS.PORT_1
    elif port == '2':
        return ev3.ePortS.PORT_2
    elif port == '3':
        return ev3.ePortS.PORT_3
    elif port == '4':
        return ev3.ePortS.PORT_4
    else:
        raise Exception(f'Unknown port: {port}')
