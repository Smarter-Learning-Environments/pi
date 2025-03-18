import os
# from enum import StrEnum

class ENV_VARS:
    MQTT_BROKER_HOST, MODULE_ID = None, None
    try:
        MQTT_BROKER_HOST = os.getenv('MQTT_BROKER_HOST')
        MODULE_ID = os.getenv("MODULE_ID")
    except:
        print('Please set env vars!')
        exit(1)