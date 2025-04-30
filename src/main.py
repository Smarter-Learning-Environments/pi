import sys
import time
import utils
import logging
import requests
import statistics
import paho.mqtt.client as mqtt

try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559

from bme280 import BME280
from enviroplus import gas
from pms5003 import PMS5003
from pms5003 import ReadTimeoutError as pmsReadTimeoutError


# Create a values dict to store the data
variables = ["temperature",
             "pressure",
             "humidity",
             "light",
             "oxidised",
             "reduced",
             "nh3",
             "pm1",
             "pm25",
             "pm10"]

sensor_count = 10

json = {
  "hw_id": utils.ENV_VARS.MAC_STR,
  "sensor_count": sensor_count,
  "sensor_descriptions": variables
}

num_readings_per_publish = 60 # 1 sample per 10 seconds, 10 minute intervals

readings = [[0 for _ in range(num_readings_per_publish)] for _ in range(sensor_count)]

response = requests.post(utils.ENV_VARS.URL, json=json)

if(response.status_code == 200 or response.status_code == 409):
    print("Healthy connection to backend")
else:
    print(response.status_code)
    print(response.text)
    print("Backend discovery failed, exiting...")
    exit(1)

def on_connect(client, userdata, flags, reason_code, properties):
	print(f"Connected with result code {reason_code}")

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.connect(utils.ENV_VARS.MQTT_BROKER_HOST, 1883, keepalive=30)
mqttc.loop_start()

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S")

logging.info("""

Press Ctrl+C to exit!

""")

# BME280 temperature/pressure/humidity sensor
bme280 = BME280()

# PMS5003 particulate sensor
pms5003 = PMS5003()

# Get the temperature of the CPU for compensation
def get_cpu_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = f.read()
        temp = int(temp) / 1000.0
    return temp


# Tuning factor for compensation. Decrease this number to adjust the
# temperature down, and increase to adjust up
factor = 2.25

cpu_temps = [get_cpu_temperature()] * 5

sensor = 0     # The starting mode

def publish_data(data, sensor): 
    try:
        msg_info = mqttc.publish(f"sensor_service/{utils.ENV_VARS.MAC_STR}/{sensor}", f"{data}:{data}")
        msg_info.wait_for_publish()
        print(f"sensor_service/{utils.ENV_VARS.MAC_STR}/{sensor}")
        print(f"{data}:{data}")
    except:
        print("Could not publish...")
        try:
            mqttc.connect(utils.ENV_VARS.MQTT_BROKER_HOST, 1883, keepalive=30)
        except:
            print("Could not reconnect...")

# The main loop
try:
    while True:
        # poll sensors
        for i in range(num_readings_per_publish * sensor_count):
            time.sleep(1)
            sensor += 1
            sensor %= len(variables)
            data = 0

            # One mode for each variable
            if sensor == 0:
                # variable = "temperature"
                unit = "°C"
                cpu_temp = get_cpu_temperature()
                # Smooth out with some averaging to decrease jitter
                cpu_temps = cpu_temps[1:] + [cpu_temp]
                avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
                raw_temp = bme280.get_temperature()
                data = raw_temp - ((avg_cpu_temp - raw_temp) / factor)
                # display_text(variables[mode], data, unit)

            if sensor == 1:
                # variable = "pressure"
                unit = "hPa"
                data = bme280.get_pressure()
                # display_text(variables[mode], data, unit)

            if sensor == 2:
                # variable = "humidity"
                unit = "%"
                data = bme280.get_humidity()
                # display_text(variables[mode], data, unit)

            if sensor == 3:
                # variable = "light"
                unit = "Lux"
                data = ltr559.get_lux()
                # display_text(variables[mode], data, unit)

            if sensor == 4:
                # variable = "oxidised"
                unit = "kO"
                data = gas.read_all()
                data = data.oxidising / 1000
                # display_text(variables[mode], data, unit)

            if sensor == 5:
                # variable = "reduced"
                unit = "kO"
                data = gas.read_all()
                data = data.reducing / 1000
                # display_text(variables[mode], data, unit)

            if sensor == 6:
                # variable = "nh3"
                unit = "kO"
                data = gas.read_all()
                data = data.nh3 / 1000
                # display_text(variables[mode], data, unit)

            if sensor == 7:
                # variable = "pm1"
                unit = "ug/m3"
                try:
                    data = pms5003.read()
                except pmsReadTimeoutError:
                    logging.warning("Failed to read PMS5003")
                else:
                    data = float(data.pm_ug_per_m3(1.0))
                    # display_text(variables[mode], data, unit)

            if sensor == 8:
                # variable = "pm25"
                unit = "ug/m3"
                try:
                    data = pms5003.read()
                except pmsReadTimeoutError:
                    logging.warning("Failed to read PMS5003")
                else:
                    data = float(data.pm_ug_per_m3(2.5))
                    # display_text(variables[mode], data, unit)

            if sensor == 9:
                # variable = "pm10"
                unit = "ug/m3"
                try:
                    data = pms5003.read()
                except pmsReadTimeoutError:
                    logging.warning("Failed to read PMS5003")
                else:
                    data = float(data.pm_ug_per_m3(10))
                    # display_text(variables[mode], data, unit)

            print(f"read sensor {sensor}:{data}")
            readings[sensor][int(i / sensor_count)] = data
        
        # report averages
        for i in range(sensor_count):
            publish_data(data=statistics.mean(readings[i]), sensor=i)
            


                
# Exit cleanly
except KeyboardInterrupt:
    sys.exit(0)
    