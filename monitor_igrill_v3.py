import json
import time
import paho.mqtt.client as mqtt

from igrill import IGrillV3Peripheral

ADDRESS = 'D4:81:CA:23:67:A1'
mqtt_server = "mqtt"
# DATA_FILE = '/tmp/igrill.json'
INTERVAL = 15

# MQTT Section
client = mqtt.Client()
client.connect(mqtt_server, 1883, 60)
client.loop_start()

if __name__ == '__main__':
 periph = IGrillV3Peripheral(ADDRESS)
 while True:
  temperature=periph.read_temperature()
  # Probe 1
  if temperature[1] != 63536.0:
   client.publish("bbq/probe1", temperature[1])

  # Probe 2
  if temperature[2] != 63536.0:
   client.publish("bbq/probe2", temperature[2])

  # Probe 3
  if temperature[3] != 63536.0:
   client.publish("bbq/probe3", temperature[3])

  # Probe 4
  if temperature[4] != 63536.0:
   client.publish("bbq/probe4", temperature[4])

  client.publish("bbq/battery", periph.read_battery())

  time.sleep(INTERVAL)
