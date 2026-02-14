import time, json
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("localhost", 1883, 60)

open_payload = {
  "device_id":"pi1_door_001",
  "sensor_type":"door_sensor",
  "component":"DS1",
  "state":"open",
  "value":1,
  "simulated":True,
  "timestamp": time.time()
}
client.publish("smarthome/test", json.dumps(open_payload))

time.sleep(6)

close_payload = dict(open_payload)
close_payload["state"] = "closed"
close_payload["value"] = 0
close_payload["timestamp"] = time.time()
client.publish("smarthome/test", json.dumps(close_payload))

client.disconnect()
