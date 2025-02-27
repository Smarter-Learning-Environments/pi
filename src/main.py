import time
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, reason_code, properties):
	print(f"Connected with result code {reason_code}")
	


mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.connect("192.168.50.208", 1883, 60)
mqttc.loop_start()

msg_info = mqttc.publish("paho/test/topic", "Hello from pi!")
print("Sent")
msg_info.wait_for_publish()
print("Published")
