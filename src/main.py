import time
import utils
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, reason_code, properties):
	print(f"Connected with result code {reason_code}")

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.connect(utils.ENV_VARS.MQTT_BROKER_HOST, 1883, 60)
mqttc.loop_start()

msg_info = mqttc.publish(f"sensor_service/{utils.ENV_VARS.MODULE_ID}/fake-sensor", "12:34")


print("Sent")
msg_info.wait_for_publish()
print("Published")
