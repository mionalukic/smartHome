import paho.mqtt.client as mqtt
import json

client = mqtt.Client()
client.connect("localhost", 1883, 60)

payload = {
    "component": "DS1",
    "value": 1,
    "timestamp": 123
}

client.publish("iot/test", json.dumps(payload))
client.disconnect()
