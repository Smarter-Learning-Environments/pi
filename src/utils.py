import os
# from enum import StrEnum

class ENV_VARS:
    MQTT_BROKER_HOST, MODULE_ID = None, None
    try:
        MQTT_BROKER_HOST = os.getenv('MQTT_BROKER_HOST', "192.168.1.33")
        MODULE_ID = os.getenv("MODULE_ID", "PI_MAC")
    except:
        print('Please set env vars!')
        exit(1)