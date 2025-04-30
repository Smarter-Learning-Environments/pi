import os
# from uuid import getnode as get_mac
# from enum import StrEnum

class ENV_VARS:
    MQTT_BROKER_HOST, MODULE_ID = None, None
    try:
        MQTT_BROKER_HOST = os.getenv('MQTT_BROKER_HOST', "192.168.1.37")
        MODULE_ID = os.getenv("MODULE_ID", "PI_MAC")
    except:
        print('Please set env vars!')
        exit(1)
    URL = "http://" + MQTT_BROKER_HOST + ":8000/discover-module"
    # MAC_STR = ':'.join(f'{(get_mac() >> (8 * i)) & 0xFF:02X}' for i in reversed(range(6)))
    with open("/sys/class/net/wlan0/address") as f:
        MAC_STR = f.read().strip().upper()
    